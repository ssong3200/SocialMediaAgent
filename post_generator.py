"""
Social Media Post Generator using OpenRouter API and Mastodon integration.
Generates brand-aligned social media posts based on company documentation.
"""

import os
import requests
from typing import Optional, List, Dict
from dotenv import load_dotenv
from brand_context import get_full_brand_context

# Load environment variables
load_dotenv()


class MastodonClient:
    """Client for posting to Mastodon."""

    def __init__(self, access_token: Optional[str] = None, instance_url: Optional[str] = None):
        """
        Initialize Mastodon client.

        Args:
            access_token: Mastodon access token from .env (MASTODON_ACCESS_TOKEN)
            instance_url: Mastodon instance URL (e.g., https://mastodon.social)
                         If None, will try to extract from token or use default
        """
        self.access_token = access_token or os.getenv("MASTODON_ACCESS_TOKEN")
        self.instance_url = instance_url or os.getenv("MASTODON_INSTANCE_URL")

        if not self.access_token:
            raise ValueError(
                "Mastodon access token required. Set MASTODON_ACCESS_TOKEN in .env file."
            )

        # If instance_url not provided, try to extract from token format or use default
        if not self.instance_url:
            # Token format might be: instance_url:access_token
            if ":" in self.access_token and self.access_token.startswith("http"):
                parts = self.access_token.split(":", 1)
                self.instance_url = parts[0]
                self.access_token = parts[1]
            else:
                # Default to a common instance - user should set MASTODON_INSTANCE_URL
                self.instance_url = "https://mastodon.social"
                print(f"Warning: Using default Mastodon instance: {self.instance_url}")
                print("Set MASTODON_INSTANCE_URL in .env to use a different instance")

        # Validate and clean the instance URL
        self.instance_url = self._validate_instance_url(self.instance_url)

        # Clean up access token (remove any whitespace)
        if self.access_token:
            self.access_token = self.access_token.strip()

    def _validate_instance_url(self, url: str) -> str:
        """
        Validate and clean the Mastodon instance URL.

        The instance URL should be just the base domain (e.g., https://mastodon.social),
        not a profile URL (e.g., https://mastodon.social/@username) or home page.

        Args:
            url: The instance URL to validate

        Returns:
            Cleaned and validated instance URL
        """
        if not url:
            return url

        # Remove trailing slashes
        url = url.rstrip('/')

        # Check for common mistakes: profile URLs, home page, etc.
        invalid_patterns = [
            '/@',  # Profile URLs like /@username
            '/home',  # Home page
            '/web/',  # Web interface
            '/api/',  # API endpoints (shouldn't be in instance URL)
        ]

        for pattern in invalid_patterns:
            if pattern in url:
                # Extract just the base URL
                base_url = url.split(pattern)[0]
                print(f"⚠️  Warning: Detected invalid instance URL pattern '{pattern}'")
                print(f"   Original: {url}")
                print(f"   Corrected to: {base_url}")
                print(f"   The instance URL should be just the base domain (e.g., https://mastodon.social)")
                url = base_url.rstrip('/')
                break

        # Ensure it starts with http:// or https://
        if not url.startswith(('http://', 'https://')):
            raise ValueError(
                f"Invalid Mastodon instance URL: {url}\n"
                "The instance URL must start with http:// or https://\n"
                "Example: https://mastodon.social"
            )

        return url

    def post_status(self, status: str, visibility: str = "public") -> Dict:
        """
        Post a status to Mastodon.

        Args:
            status: The text content to post (max 500 chars for most instances)
            visibility: Visibility level: public, unlisted, private, direct

        Returns:
            Response dictionary from Mastodon API
        """
        # Validate post length (most Mastodon instances have a 500 character limit)
        if len(status) > 500:
            raise ValueError(
                f"Post is too long ({len(status)} characters). "
                f"Mastodon posts are limited to 500 characters. "
                f"Current length: {len(status)} characters."
            )

        if not status or not status.strip():
            raise ValueError("Post content cannot be empty")

        url = f"{self.instance_url.rstrip('/')}/api/v1/statuses"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        data = {
            "status": status,
            "visibility": visibility
        }

        try:
            response = requests.post(url, headers=headers, json=data)

            # If there's an error, try to extract the detailed error message
            if not response.ok:
                error_msg = f"HTTP {response.status_code}: {response.reason}"

                # Try to get detailed error from response body
                try:
                    error_data = response.json()
                    if isinstance(error_data, dict):
                        if "error" in error_data:
                            error_msg += f"\nError: {error_data['error']}"
                        if "error_description" in error_data:
                            error_msg += f"\nDescription: {error_data['error_description']}"
                        # Mastodon sometimes returns errors in a different format
                        if "message" in error_data:
                            error_msg += f"\nMessage: {error_data['message']}"
                except (ValueError, KeyError):
                    # If we can't parse JSON, include the raw response text
                    if response.text:
                        error_msg += f"\nResponse: {response.text[:200]}"

                raise requests.exceptions.HTTPError(error_msg, response=response)

            return response.json()
        except requests.exceptions.HTTPError as e:
            # Re-raise HTTP errors with better messages
            raise RuntimeError(f"Error posting to Mastodon: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error posting to Mastodon: {str(e)}")


class SocialMediaPostGenerator:
    """Generates social media posts using OpenRouter API with brand context."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "openai/gpt-4o-mini",
        mastodon_token: Optional[str] = None,
        mastodon_instance: Optional[str] = None
    ):
        """
        Initialize the post generator.

        Args:
            api_key: OpenRouter API key. If None, will try to get from OPEN_ROUTER_API env var.
            model: Model to use for generation (default: openai/gpt-4o-mini)
                   Format: "provider/model-name" (e.g., "anthropic/claude-3-haiku")
            mastodon_token: Optional Mastodon access token for direct posting
            mastodon_instance: Optional Mastodon instance URL
        """
        self.api_key = api_key or os.getenv("OPEN_ROUTER_API")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key required. Set OPEN_ROUTER_API in .env file."
            )

        self.model = model
        self.brand_context = get_full_brand_context()

        # Initialize Mastodon client if token provided
        self.mastodon = None
        if mastodon_token or os.getenv("MASTODON_ACCESS_TOKEN"):
            try:
                self.mastodon = MastodonClient(
                    access_token=mastodon_token,
                    instance_url=mastodon_instance
                )
            except Exception as e:
                print(f"Warning: Mastodon client not initialized: {e}")

    def generate_post(
        self,
        platform: str = "mastodon",
        topic: Optional[str] = None,
        tone: Optional[str] = None,
        length: str = "medium",
        include_hashtags: bool = True
    ) -> str:
        """
        Generate a social media post.

        Args:
            platform: Target platform (mastodon, twitter, instagram, linkedin, facebook)
            topic: Optional specific topic to focus on (e.g., "product launch", "community")
            tone: Optional tone override (defaults to brand voice)
            length: Post length - "short", "medium", or "long"
            include_hashtags: Whether to include relevant hashtags

        Returns:
            Generated social media post
        """
        # Platform-specific constraints
        platform_constraints = {
            "mastodon": {
                "max_chars": 500,
                "description": "Mastodon post (500 characters typical max)"
            },
            "twitter": {
                "max_chars": 280,
                "description": "Twitter/X post (280 characters max)"
            },
            "instagram": {
                "max_chars": 2200,
                "description": "Instagram post (can include caption and hashtags)"
            },
            "linkedin": {
                "max_chars": 3000,
                "description": "LinkedIn post (professional tone)"
            },
            "facebook": {
                "max_chars": 5000,
                "description": "Facebook post"
            }
        }

        if platform.lower() not in platform_constraints:
            raise ValueError(f"Platform must be one of: {', '.join(platform_constraints.keys())}")

        constraints = platform_constraints[platform.lower()]

        # Length guidance
        length_guidance = {
            "short": "Keep it concise and punchy",
            "medium": "Moderate length with key points",
            "long": "More detailed and comprehensive"
        }

        # Build the prompt
        prompt = self._build_prompt(
            platform=platform,
            platform_desc=constraints["description"],
            max_chars=constraints["max_chars"],
            topic=topic,
            tone=tone,
            length_guidance=length_guidance.get(length, "medium"),
            include_hashtags=include_hashtags
        )

        # Generate post using OpenRouter
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "HTTP-Referer": "https://github.com/your-org/socialmedia-agent",  # Optional
                    "X-Title": "Social Media Agent",  # Optional
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert social media content creator who writes engaging, brand-aligned posts."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 500
                }
            )

            response.raise_for_status()
            result = response.json()
            post = result["choices"][0]["message"]["content"].strip()

            # Post-process: truncate if still too long (intelligently preserve hashtags)
            post = self._truncate_post_if_needed(post, constraints["max_chars"])

            return post

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error generating post via OpenRouter: {str(e)}")
        except KeyError as e:
            raise RuntimeError(f"Unexpected response format from OpenRouter: {str(e)}")

    def generate_and_post(
        self,
        platform: str = "mastodon",
        topic: Optional[str] = None,
        tone: Optional[str] = None,
        length: str = "medium",
        include_hashtags: bool = True,
        visibility: str = "public",
        post_to_mastodon: bool = True
    ) -> Dict:
        """
        Generate a post and optionally post it to Mastodon.

        Args:
            platform: Target platform
            topic: Optional topic
            tone: Optional tone override
            length: Post length
            include_hashtags: Whether to include hashtags
            visibility: Mastodon visibility (public, unlisted, private, direct)
            post_to_mastodon: Whether to actually post to Mastodon (default: True)

        Returns:
            Dictionary with 'post' (generated text) and 'mastodon_response' (if posted)
        """
        post = self.generate_post(
            platform=platform,
            topic=topic,
            tone=tone,
            length=length,
            include_hashtags=include_hashtags
        )

        result = {"post": post}

        if post_to_mastodon and self.mastodon:
            try:
                mastodon_response = self.mastodon.post_status(post, visibility=visibility)
                result["mastodon_response"] = mastodon_response
                result["posted"] = True
                result["mastodon_url"] = mastodon_response.get("url", "N/A")
            except Exception as e:
                result["posted"] = False
                result["error"] = str(e)
        else:
            result["posted"] = False
            if not self.mastodon:
                result["note"] = "Mastodon client not configured"
            else:
                result["note"] = "Posting disabled"

        return result

    def generate_multiple_posts(
        self,
        count: int = 3,
        platform: str = "mastodon",
        topic: Optional[str] = None,
        **kwargs
    ) -> List[str]:
        """
        Generate multiple variations of posts.

        Args:
            count: Number of posts to generate
            platform: Target platform
            topic: Optional topic focus
            **kwargs: Additional arguments passed to generate_post

        Returns:
            List of generated posts
        """
        posts = []
        for i in range(count):
            post = self.generate_post(platform=platform, topic=topic, **kwargs)
            posts.append(post)
        return posts

    def _build_prompt(
        self,
        platform: str,
        platform_desc: str,
        max_chars: int,
        topic: Optional[str],
        tone: Optional[str],
        length_guidance: str,
        include_hashtags: bool
    ) -> str:
        """Build the prompt for the LLM."""

        topic_section = ""
        if topic:
            topic_section = f"\nSPECIFIC TOPIC TO FOCUS ON: {topic}"

        tone_section = ""
        if tone:
            tone_section = f"\nTONE OVERRIDE: {tone}"
        else:
            tone_section = "\nTONE: Use the brand voice described above (honest, friendly, informed, not intimidating)"

        hashtag_instruction = ""
        if include_hashtags:
            hashtag_instruction = "\n- Include 3-5 relevant hashtags at the end (e.g., #skincare #skincaretips #skincarereviews)"

        prompt = f"""Generate a {platform_desc} for our skincare platform.

BRAND CONTEXT:
{self.brand_context}

REQUIREMENTS:
- Platform: {platform_desc}
- CRITICAL: Maximum length is EXACTLY {max_chars} characters or less. This is a hard limit - your response MUST be {max_chars} characters or fewer. Count your characters carefully.
- Length style: {length_guidance}
{topic_section}
{tone_section}
- Must align with brand pillars: Trust over trends, Social proof, Transparency, Inclusivity
- Avoid overhyped language and marketing speak
- Sound like advice from a smart, honest friend
- Be engaging and authentic
{hashtag_instruction}

IMPORTANT: Your response must be {max_chars} characters or less. Do not exceed this limit.

Generate the post now:"""

        return prompt

    def _truncate_post_if_needed(self, post: str, max_chars: int) -> str:
        """
        Intelligently truncate a post if it exceeds the character limit.
        Tries to preserve hashtags and truncate at word boundaries.

        Args:
            post: The post text
            max_chars: Maximum allowed characters

        Returns:
            Truncated post (if needed) that fits within the limit
        """
        if len(post) <= max_chars:
            return post

        # Try to preserve hashtags - extract them first
        words = post.split()
        hashtags = [word for word in words if word.startswith('#')]
        main_content = ' '.join([word for word in words if not word.startswith('#')])

        # Calculate space needed for hashtags (with spaces)
        hashtag_space = len(' '.join(hashtags)) if hashtags else 0
        available_for_content = max_chars - hashtag_space - (1 if hashtags else 0)  # -1 for space before hashtags

        if available_for_content < 50:  # Not enough space for meaningful content
            # Just truncate the whole thing at word boundaries
            truncated = post[:max_chars]
            # Try to truncate at a word boundary
            last_space = truncated.rfind(' ')
            if last_space > max_chars * 0.8:  # Only if we're not losing too much
                truncated = truncated[:last_space]
            return truncated + ('...' if len(post) > max_chars else '')

        # Truncate main content, preserving hashtags
        if len(main_content) > available_for_content:
            # Reserve 3 chars for '...'
            truncate_to = available_for_content - 3
            truncated_content = main_content[:truncate_to]
            # Truncate at word boundary
            last_space = truncated_content.rfind(' ')
            if last_space > truncate_to * 0.8:
                truncated_content = truncated_content[:last_space]
            truncated_content = truncated_content.rstrip() + '...'
        else:
            truncated_content = main_content

        # Reassemble with hashtags
        if hashtags:
            hashtag_str = ' '.join(hashtags)
            result = f"{truncated_content} {hashtag_str}"
        else:
            result = truncated_content

        # Final safety check - if still too long, hard truncate
        if len(result) > max_chars:
            result = result[:max_chars].rstrip()
            # Remove any partial words at the end
            last_space = result.rfind(' ')
            if last_space > max_chars * 0.9:
                result = result[:last_space]
            # Remove trailing ellipsis if we're at the limit
            if result.endswith('...') and len(result) > max_chars - 3:
                result = result[:-3].rstrip()

        return result


def main():
    """Example usage."""
    import sys

    # Check for API key
    if not os.getenv("OPEN_ROUTER_API"):
        print("Error: OPEN_ROUTER_API environment variable not set.")
        print("Set it in your .env file or as an environment variable.")
        sys.exit(1)

    # Initialize generator
    generator = SocialMediaPostGenerator()

    print("Social Media Post Generator (OpenRouter + Mastodon)")
    print("=" * 60)

    # generate a Mastodon post
    print("\n1. Generating Mastodon post...")
    mastodon_post = generator.generate_post(platform="mastodon", topic="community trust")
    print(f"\n{mastodon_post}\n")

    # generate and post to mastodon
    if generator.mastodon:
        print("\n2. Generating and posting to Mastodon...")
        result = generator.generate_and_post(
            platform="mastodon",
            topic="product discovery",
            post_to_mastodon=True  # Set to False to just generate without posting
        )
        print(f"\nGenerated post:\n{result['post']}\n")
        if result.get("posted"):
            print(f"✅ Posted to Mastodon: {result.get('mastodon_url', 'N/A')}")
        else:
            print(f"ℹ️  Not posted: {result.get('note', result.get('error', 'Unknown'))}")
    else:
        print("\n2. Mastodon not configured. Skipping auto-posting.")



if __name__ == "__main__":
    main()
