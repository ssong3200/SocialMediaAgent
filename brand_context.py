"""
Brand context and company information extracted from Notion docs.
This file contains the foundational information used to generate brand-aligned social media posts.
"""

COMPANY_OVERVIEW = """
We are building a social skincare discovery platform that helps people make smarter skincare decisions through trusted reviews from friends and the wider community.

Skincare is personal, expensive, and overwhelming. Ingredient lists are long, marketing is noisy, and most reviews online are either paid, anonymous, or hard to trust. Our platform solves this by making skincare discovery social, transparent, and data-driven.

Users can rate and review skincare products they've tried, follow friends (and creators), and see skincare recommendations based on real usage and honest feedback. Instead of guessing what might work, users discover what actually works for people they trust.

Our long-term goal is to become the go-to place for skincare knowledge, community-driven product discovery, and personalized routines.
"""

WHAT_WE_DO = """
Our product is a social-first skincare review and discovery app.

Users can:
- Review and rate skincare products they've personally used
- Track products they are currently using or want to try
- Follow friends and see their ratings, reviews, and routines
- Discover new products through social feeds instead of ads
- Browse aggregated ratings by skin type, concern, and category

Unlike traditional review platforms, we prioritize **who** the review comes from, not just the review itself. A 4-star rating from a friend with similar skin concerns is far more valuable than hundreds of anonymous reviews.

Over time, the platform will support:
- Skin profiles (type, concerns, sensitivities)
- Smarter recommendations
- Routine-building tools
- Creator and dermatologist verification
- Brand transparency and ingredient insights

We are building infrastructure for trust in skincare.
"""

BRAND_IDENTITY = """
Our brand is built on trust, clarity, and community.

Skincare should feel empowering, not confusing or gatekept. Our tone is honest, friendly, and informed without being intimidating. We avoid overhyped language and focus on real experiences.

**Brand pillars:**
- **Trust over trends** – Real users, real results
- **Social proof** – Friends > influencers > ads
- **Transparency** – Clear ratings, clear opinions
- **Inclusivity** – All skin types, routines, and budgets welcome

Visually, the brand should feel:
- Clean but not clinical
- Modern but warm
- Minimal without being sterile

We want users to feel like they're getting skincare advice from a smart, honest friend — not a marketing department.
"""

VISION_MISSION = """
Our vision is to redefine how people discover and trust skincare.

In the future, skincare decisions won't start with ads or sponsored posts. They'll start with community data, social trust, and personal relevance. We want to be the layer that sits between brands and consumers — translating marketing into truth.

Long-term, we aim to:
- Become the largest trusted skincare review graph
- Power personalized skincare recommendations
- Influence better product formulation through honest feedback
- Help users spend less money on products that don't work for them

If someone asks, "What skincare should I try?", the answer should start with us.
"""

def get_full_brand_context():
    """Returns the complete brand context for LLM prompts."""
    return f"""
COMPANY OVERVIEW:
{COMPANY_OVERVIEW}

WHAT WE DO:
{WHAT_WE_DO}

BRAND & IDENTITY:
{BRAND_IDENTITY}

VISION & MISSION:
{VISION_MISSION}
"""
