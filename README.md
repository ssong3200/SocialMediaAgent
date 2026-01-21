# SocialMediaAgent

An LLM-powered social media post generator that creates brand-aligned content based on your company's Notion documentation. This tool helps you generate consistent, on-brand social media posts for Twitter, Instagram, LinkedIn, and Facebook.

## Features

- 🎯 **Brand-Aligned Content**: Uses your company's brand voice, values, and messaging
- 📱 **Multi-Platform Support**: Generates posts optimized for Mastodon, Twitter, Instagram, LinkedIn, and Facebook
- 🤖 **OpenRouter Integration**: Uses OpenRouter API for flexible LLM model selection
- 📮 **Mastodon Posting**: Direct posting to Mastodon instances
- 🎨 **Customizable**: Control topic, tone, length, and hashtags
- 🔄 **Batch Generation**: Generate multiple variations at once
- 💡 **Smart Prompts**: Built-in prompts that incorporate your brand identity

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root with your API keys:

```bash
# OpenRouter API Key
OPEN_ROUTER_API=your-openrouter-api-key-here

# Mastodon Access Token (optional, for direct posting)
MASTODON_ACCESS_TOKEN=your-mastodon-access-token-here

# Mastodon Instance URL (optional, if not included in token)
MASTODON_INSTANCE_URL=https://mastodon.social
```

**Getting your API keys:**
- **OpenRouter API Key**: Get one from [OpenRouter](https://openrouter.ai/keys)
- **Mastodon Access Token**: Create an app in your Mastodon instance settings (Settings > Development > New Application)

## Usage

### Command Line Interface

The easiest way to generate posts is using the CLI tool:

```bash
# Generate a Mastodon post (preview only)
python generate.py --platform mastodon

# Generate and post to Mastodon
python generate.py --platform mastodon --post

# Generate 3 Mastodon posts about community
python generate.py --platform mastodon --topic "community" --count 3

# Generate a Twitter post
python generate.py --platform twitter --length short

# Generate and post to Mastodon with custom visibility
python generate.py --platform mastodon --post --visibility unlisted

# Generate without hashtags
python generate.py --platform mastodon --no-hashtags

# Custom topic and tone
python generate.py --platform instagram --topic "product launch" --tone "excited but authentic"
```

### Python API

You can also use the generator programmatically:

```python
from post_generator import SocialMediaPostGenerator
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize generator
generator = SocialMediaPostGenerator(
    api_key=os.getenv("OPEN_ROUTER_API"),
    model="openai/gpt-4o-mini"  # or "anthropic/claude-3-haiku", etc.
)

# Generate a single post
post = generator.generate_post(
    platform="mastodon",
    topic="community trust",
    length="medium",
    include_hashtags=True
)
print(post)

# Generate and post to Mastodon
result = generator.generate_and_post(
    platform="mastodon",
    topic="product discovery",
    post_to_mastodon=True,
    visibility="public"
)
print(f"Posted: {result.get('mastodon_url')}")

# Generate multiple variations
posts = generator.generate_multiple_posts(
    count=3,
    platform="mastodon",
    topic="product discovery"
)
for post in posts:
    print(post)
```

### Run Example Script

```bash
python post_generator.py
```

This will generate example posts for different platforms.

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--platform` | Platform: mastodon, twitter, instagram, linkedin, facebook | mastodon |
| `--topic` | Specific topic to focus on | None |
| `--tone` | Tone override | Brand voice |
| `--length` | Post length: short, medium, long | medium |
| `--count` | Number of posts to generate | 1 |
| `--no-hashtags` | Don't include hashtags | False |
| `--api-key` | OpenRouter API key | Uses OPEN_ROUTER_API env var |
| `--model` | OpenRouter model (format: provider/model) | openai/gpt-4o-mini |
| `--post` | Post to Mastodon | False |
| `--visibility` | Mastodon visibility: public, unlisted, private, direct | public |
| `--mastodon-instance` | Mastodon instance URL | Uses MASTODON_INSTANCE_URL env var |

## Platform-Specific Details

- **Mastodon**: 500 character limit (typical), community-focused
- **Twitter**: 280 character limit, concise and punchy
- **Instagram**: Up to 2200 characters, can include hashtags
- **LinkedIn**: Up to 3000 characters, professional tone
- **Facebook**: Up to 5000 characters, conversational

## Brand Context

The generator uses your company's brand information stored in `brand_context.py`, which includes:

- Company Overview
- What We Do
- Brand & Identity (voice, pillars, visual style)
- Vision & Long-Term Mission

To update the brand context, edit `brand_context.py` with your latest Notion documentation.

## Customization

### Updating Brand Context

Edit `brand_context.py` to reflect changes in your Notion docs. The file contains:
- `COMPANY_OVERVIEW`
- `WHAT_WE_DO`
- `BRAND_IDENTITY`
- `VISION_MISSION`

### Adjusting Prompts

Modify the `_build_prompt()` method in `post_generator.py` to customize how prompts are constructed.

### Using Different Models via OpenRouter

OpenRouter supports many models. Specify them in format `provider/model`:

- `openai/gpt-4o-mini`: Fast and cost-effective (default)
- `openai/gpt-4o`: Better quality
- `anthropic/claude-3-haiku`: Fast Claude model
- `anthropic/claude-3-opus`: Highest quality Claude
- `google/gemini-pro`: Google's Gemini model

Browse all available models at [OpenRouter Models](https://openrouter.ai/models).

Change the model via `--model` flag or when initializing `SocialMediaPostGenerator`.

## Project Structure

```
SocialMediaAgent/
├── brand_context.py      # Brand information from Notion docs
├── post_generator.py     # Main LLM post generator class
├── generate.py           # CLI tool for generating posts
├── requirements.txt      # Python dependencies
├── .env.example          # Example environment file
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## Tips for Best Results

1. **Be Specific with Topics**: Instead of generic topics, use specific ones like:
   - "community trust"
   - "product discovery"
   - "transparency in reviews"
   - "friend recommendations"

2. **Iterate**: Generate multiple posts and pick the best ones. Use `--count` to get variations.

3. **Review and Refine**: Always review generated posts to ensure they align with your brand. You can regenerate with different parameters.

4. **Save Good Prompts**: If you find a topic/tone combination that works well, note it down for future use.

5. **Platform Optimization**: Generate platform-specific versions rather than reposting the same content everywhere.

## Troubleshooting

### "OpenRouter API key required" error
- Make sure you've set `OPEN_ROUTER_API` in your `.env` file or passed `--api-key`
- Verify your API key is valid at [OpenRouter](https://openrouter.ai/)

### Mastodon posting not working
- Ensure `MASTODON_ACCESS_TOKEN` is set in your `.env` file
- Verify your Mastodon instance URL is correct in `MASTODON_INSTANCE_URL`
- Check that your access token has write permissions
- Token format can be either just the token, or `instance_url:token`

### Posts don't match brand voice
- Review and update `brand_context.py` with more specific brand guidelines
- Try adjusting the `--tone` parameter
- Consider using a more advanced model like `gpt-4o`

### Posts are too generic
- Use more specific `--topic` values
- Add more detail to your brand context in `brand_context.py`
- Try generating multiple posts and selecting the best

## Cost Considerations

OpenRouter pricing varies by model. Check current rates at [OpenRouter Pricing](https://openrouter.ai/models).
- `openai/gpt-4o-mini`: Very cost-effective
- Each post generation uses roughly 500-1000 tokens
- OpenRouter provides transparent pricing per model

## Next Steps

Consider extending this tool with:
- Integration with Notion API to automatically pull latest docs
- Scheduled post generation
- Post analytics and A/B testing
- Integration with social media APIs for direct publishing
- Template system for common post types

## License

MIT License - feel free to use and modify for your needs.
