#!/usr/bin/env python3
"""
CLI tool for generating social media posts using OpenRouter API and Mastodon.
Usage examples:
    python generate.py --platform mastodon
    python generate.py --platform mastodon --topic "product launch" --count 3 --post
    python generate.py --platform twitter --length short
"""

import argparse
import os
import sys
from dotenv import load_dotenv
from post_generator import SocialMediaPostGenerator

# Load environment variables
load_dotenv()


def main():
    parser = argparse.ArgumentParser(
        description="Generate brand-aligned social media posts using OpenRouter API and Mastodon",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a single Mastodon post (preview only)
  python generate.py --platform mastodon

  # Generate, preview, and post to Mastodon (with confirmation)
  python generate.py --platform mastodon --post

  # Generate 3 Mastodon posts about community
  python generate.py --platform mastodon --topic "community" --count 3

  # Generate a Twitter post (preview only)
  python generate.py --platform twitter --length short

  # Generate and post to Mastodon with custom visibility
  python generate.py --platform mastodon --post --visibility unlisted

  # Generate post without hashtags
  python generate.py --platform mastodon --no-hashtags
        """
    )

    parser.add_argument(
        "--platform",
        type=str,
        choices=["mastodon", "twitter", "instagram", "linkedin", "facebook"],
        default="mastodon",
        help="Social media platform (default: mastodon)"
    )

    parser.add_argument(
        "--topic",
        type=str,
        help="Specific topic to focus on (e.g., 'product launch', 'community', 'trust')"
    )

    parser.add_argument(
        "--tone",
        type=str,
        help="Tone override (defaults to brand voice)"
    )

    parser.add_argument(
        "--length",
        type=str,
        choices=["short", "medium", "long"],
        default="medium",
        help="Post length (default: medium)"
    )

    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Number of posts to generate (default: 1)"
    )

    parser.add_argument(
        "--no-hashtags",
        action="store_true",
        help="Don't include hashtags"
    )

    parser.add_argument(
        "--api-key",
        type=str,
        help="OpenRouter API key (or set OPEN_ROUTER_API in .env)"
    )

    parser.add_argument(
        "--model",
        type=str,
        default="openai/gpt-4o-mini",
        help="OpenRouter model to use (default: openai/gpt-4o-mini). Format: provider/model"
    )

    parser.add_argument(
        "--post",
        action="store_true",
        help="Post to Mastodon (only works if MASTODON_ACCESS_TOKEN is set)"
    )

    parser.add_argument(
        "--visibility",
        type=str,
        choices=["public", "unlisted", "private", "direct"],
        default="public",
        help="Mastodon post visibility (default: public). Only used with --post"
    )

    parser.add_argument(
        "--mastodon-instance",
        type=str,
        help="Mastodon instance URL (or set MASTODON_INSTANCE_URL in .env)"
    )

    args = parser.parse_args()

    # Check for API key
    api_key = args.api_key or os.getenv("OPEN_ROUTER_API")
    if not api_key:
        print("Error: OpenRouter API key required.", file=sys.stderr)
        print("Set OPEN_ROUTER_API in .env file or use --api-key flag", file=sys.stderr)
        sys.exit(1)

    # Warn if trying to post without Mastodon config
    if args.post and not os.getenv("MASTODON_ACCESS_TOKEN"):
        print("Warning: --post specified but MASTODON_ACCESS_TOKEN not set.", file=sys.stderr)
        print("Post will be generated but not posted.", file=sys.stderr)

    try:
        # Initialize generator
        mastodon_token = os.getenv("MASTODON_ACCESS_TOKEN")
        mastodon_instance = args.mastodon_instance or os.getenv("MASTODON_INSTANCE_URL")

        generator = SocialMediaPostGenerator(
            api_key=api_key,
            model=args.model,
            mastodon_token=mastodon_token,
            mastodon_instance=mastodon_instance
        )

        # Generate and optionally post
        if args.count == 1:
            # Generate the post first
            post = generator.generate_post(
                platform=args.platform,
                topic=args.topic,
                tone=args.tone,
                length=args.length,
                include_hashtags=not args.no_hashtags
            )

            # Show the generated post
            print("\n" + "=" * 60)
            print("Generated Post:")
            print("=" * 60)
            print(post)
            print("=" * 60)

            # If --post flag is set and Mastodon is configured, ask for confirmation
            if args.post and generator.mastodon:
                print(f"\nVisibility: {args.visibility}")
                print("\nDo you want to post this to Mastodon? (y/n): ", end="")

                try:
                    confirmation = input().strip().lower()
                    if confirmation in ['y', 'yes']:
                        # Post to Mastodon
                        try:
                            mastodon_response = generator.mastodon.post_status(
                                post,
                                visibility=args.visibility
                            )
                            print("\n✅ Posted to Mastodon!")
                            print(f"URL: {mastodon_response.get('url', 'N/A')}")
                        except Exception as e:
                            print(f"\n❌ Failed to post: {e}")
                    else:
                        print("\n❌ Post cancelled. Not posted to Mastodon.")
                except (KeyboardInterrupt, EOFError):
                    print("\n\n❌ Cancelled. Not posted to Mastodon.")
            elif args.post and not generator.mastodon:
                print("\n(Post not published - Mastodon not configured)")
            else:
                # Just generated, not posting
                pass
        else:
            # Generate multiple posts
            posts = generator.generate_multiple_posts(
                count=args.count,
                platform=args.platform,
                topic=args.topic,
                tone=args.tone,
                length=args.length,
                include_hashtags=not args.no_hashtags
            )

            # Show all generated posts
            for i, post in enumerate(posts, 1):
                print(f"\n--- Post {i} ---")
                print(post)
                print()

            # If --post flag is set and Mastodon is configured, ask which one to post
            if args.post and generator.mastodon:
                print("\n" + "=" * 60)
                print(f"Which post would you like to post to Mastodon? (1-{args.count}, or 'none'): ", end="")
                try:
                    selection = input().strip().lower()
                    if selection == 'none':
                        print("❌ Post cancelled. Not posted to Mastodon.")
                    else:
                        try:
                            post_index = int(selection) - 1
                            if 0 <= post_index < len(posts):
                                selected_post = posts[post_index]
                                print(f"\nVisibility: {args.visibility}")
                                print("\nConfirm posting this post? (y/n): ", end="")
                                confirm = input().strip().lower()

                                if confirm in ['y', 'yes']:
                                    try:
                                        result = generator.mastodon.post_status(
                                            selected_post,
                                            visibility=args.visibility
                                        )
                                        print(f"\n✅ Posted to Mastodon!")
                                        print(f"URL: {result.get('url', 'N/A')}")
                                    except Exception as e:
                                        print(f"\n❌ Failed to post: {e}")
                                else:
                                    print("\n❌ Post cancelled.")
                            else:
                                print(f"\n❌ Invalid selection. Please choose 1-{args.count}.")
                        except ValueError:
                            print("\n❌ Invalid input. Please enter a number or 'none'.")
                except (KeyboardInterrupt, EOFError):
                    print("\n\n❌ Cancelled. Not posted to Mastodon.")

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
