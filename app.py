"""
FastAPI application for Social Media Post Generator
Provides REST API endpoints for generating and managing social media posts.
"""

import os
import sqlite3
from datetime import datetime
from typing import Optional, List
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from post_generator import SocialMediaPostGenerator

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Social Media Post Generator API",
    description="API for generating brand-aligned social media posts",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DB_PATH = Path("/opt/socialmedia-agent/posts.db")

def init_db():
    """Initialize SQLite database with posts table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,
            content TEXT NOT NULL,
            topic TEXT,
            tone TEXT,
            length TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            posted_at TIMESTAMP,
            mastodon_url TEXT,
            status TEXT DEFAULT 'generated'
        )
    """)
    conn.commit()
    conn.close()

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# Pydantic models
class PostRequest(BaseModel):
    platform: str = Field(..., description="Platform: mastodon, twitter, instagram, linkedin, facebook")
    topic: Optional[str] = Field(None, description="Specific topic to focus on")
    tone: Optional[str] = Field(None, description="Tone override")
    length: str = Field("medium", description="Post length: short, medium, long")
    include_hashtags: bool = Field(True, description="Include hashtags")
    post_to_mastodon: bool = Field(False, description="Post to Mastodon immediately")
    visibility: str = Field("public", description="Mastodon visibility: public, unlisted, private, direct")
    include_image: bool = Field(False, description="Generate and attach an image using Replicate")

class PostResponse(BaseModel):
    id: int
    platform: str
    content: str
    topic: Optional[str]
    tone: Optional[str]
    length: str
    created_at: str
    posted_at: Optional[str]
    mastodon_url: Optional[str]
    status: str
    image_url: Optional[str] = None
    image_path: Optional[str] = None

class PostListResponse(BaseModel):
    posts: List[PostResponse]
    total: int

# Initialize post generator
try:
    replicate_token = os.getenv("REPLICATE_API_TOKEN")
    generator = SocialMediaPostGenerator(replicate_token=replicate_token)
except Exception as e:
    print(f"Warning: Post generator initialization failed: {e}")
    generator = None

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Social Media Post Generator API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "generate": "/api/posts/generate",
            "list": "/api/posts",
            "get": "/api/posts/{post_id}",
            "delete": "/api/posts/{post_id}"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected" if DB_PATH.exists() else "not found",
        "generator": "initialized" if generator else "not initialized"
    }

@app.post("/api/posts/generate", response_model=PostResponse)
async def generate_post(request: PostRequest):
    """
    Generate a new social media post.
    """
    if not generator:
        raise HTTPException(status_code=500, detail="Post generator not initialized")
    
    try:
        # Use generate_and_post if posting or including image
        if request.post_to_mastodon or request.include_image:
            result = generator.generate_and_post(
                platform=request.platform,
                topic=request.topic,
                tone=request.tone,
                length=request.length,
                include_hashtags=request.include_hashtags,
                visibility=request.visibility,
                post_to_mastodon=request.post_to_mastodon,
                include_image=request.include_image
            )
            content = result["post"]
            posted_at = datetime.utcnow().isoformat() if result.get("posted") else None
            mastodon_url = result.get("mastodon_url")
            status = "posted" if result.get("posted") else "generated"
            image_url = result.get("image", {}).get("url") if result.get("image") else None
            image_path = result.get("image", {}).get("path") if result.get("image") else None
        else:
            # Just generate the post
            content = generator.generate_post(
                platform=request.platform,
                topic=request.topic,
                tone=request.tone,
                length=request.length,
                include_hashtags=request.include_hashtags
            )
            posted_at = None
            mastodon_url = None
            status = "generated"
            image_url = None
            image_path = None
        
        # Save to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Insert into database
        cursor.execute("""
            INSERT INTO posts (platform, content, topic, tone, length, posted_at, mastodon_url, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            request.platform,
            content,
            request.topic,
            request.tone,
            request.length,
            posted_at,
            mastodon_url,
            status
        ))
        
        post_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Return response
        return PostResponse(
            id=post_id,
            platform=request.platform,
            content=content,
            topic=request.topic,
            tone=request.tone,
            length=request.length,
            created_at=datetime.utcnow().isoformat(),
            posted_at=posted_at,
            mastodon_url=mastodon_url,
            status=status,
            image_url=image_url,
            image_path=image_path
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating post: {str(e)}")

@app.get("/api/posts", response_model=PostListResponse)
async def list_posts(
    platform: Optional[str] = Query(None, description="Filter by platform"),
    limit: int = Query(50, ge=1, le=100, description="Number of posts to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    List all generated posts with optional filtering.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Build query
    query = "SELECT * FROM posts"
    params = []
    
    if platform:
        query += " WHERE platform = ?"
        params.append(platform)
    
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    # Get total count
    count_query = "SELECT COUNT(*) FROM posts"
    if platform:
        count_query += " WHERE platform = ?"
        cursor.execute(count_query, [platform])
    else:
        cursor.execute(count_query)
    total = cursor.fetchone()[0]
    
    conn.close()
    
    posts = [
        PostResponse(
            id=row["id"],
            platform=row["platform"],
            content=row["content"],
            topic=row["topic"],
            tone=row["tone"],
            length=row["length"],
            created_at=row["created_at"],
            posted_at=row["posted_at"],
            mastodon_url=row["mastodon_url"],
            status=row["status"]
        )
        for row in rows
    ]
    
    return PostListResponse(posts=posts, total=total)

@app.get("/api/posts/{post_id}", response_model=PostResponse)
async def get_post(post_id: int):
    """
    Get a specific post by ID.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return PostResponse(
        id=row["id"],
        platform=row["platform"],
        content=row["content"],
        topic=row["topic"],
        tone=row["tone"],
        length=row["length"],
        created_at=row["created_at"],
        posted_at=row["posted_at"],
        mastodon_url=row["mastodon_url"],
        status=row["status"]
    )

@app.delete("/api/posts/{post_id}")
async def delete_post(post_id: int):
    """
    Delete a post by ID.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return {"message": "Post deleted successfully", "id": post_id}

@app.post("/api/posts/{post_id}/post")
async def post_to_mastodon(
    post_id: int,
    visibility: str = Query("public", description="Mastodon visibility")
):
    """
    Post an existing generated post to Mastodon.
    """
    if not generator or not generator.mastodon:
        raise HTTPException(status_code=500, detail="Mastodon client not configured")
    
    # Get post from database
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Post not found")
    
    if row["status"] == "posted":
        conn.close()
        raise HTTPException(status_code=400, detail="Post already posted to Mastodon")
    
    # Post to Mastodon
    try:
        result = generator.mastodon.post_status(
            row["content"],
            visibility=visibility
        )
        
        # Update database
        posted_at = datetime.utcnow().isoformat()
        mastodon_url = result.get("url")
        
        cursor.execute("""
            UPDATE posts 
            SET posted_at = ?, mastodon_url = ?, status = ?
            WHERE id = ?
        """, (posted_at, mastodon_url, "posted", post_id))
        
        conn.commit()
        conn.close()
        
        return {
            "message": "Post published to Mastodon",
            "id": post_id,
            "mastodon_url": mastodon_url
        }
        
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Error posting to Mastodon: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
