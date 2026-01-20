# SocialMediaAgent

An LLM-powered social media post generator that creates brand-aligned content based on your company's Notion documentation. This tool helps you generate consistent, on-brand social media posts for Twitter, Instagram, LinkedIn, and Facebook.

## Features

- 🎯 **Brand-Aligned Content**: Uses your company's brand voice, values, and messaging
- 📱 **Multi-Platform Support**: Generates posts optimized for Twitter, Instagram, LinkedIn, and Facebook
- 🎨 **Customizable**: Control topic, tone, length, and hashtags
- 🔄 **Batch Generation**: Generate multiple variations at once
- 💡 **Smart Prompts**: Built-in prompts that incorporate your brand identity

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up OpenAI API Key

You'll need an OpenAI API key. Get one from [OpenAI Platform](https://platform.openai.com/api-keys).

**Option A: Environment Variable (Recommended)**
```bash
export OPENAI_API_KEY='your-api-key-here'
```

**Option B: Create `.env` file**
```bash
cp .env.example .env
# Then edit .env and add your API key
```

**Option C: Pass via command line**
Use the `--api-key` flag when running the script.

## Usage

### Command Line Interface

The easiest way to generate posts is using the CLI tool:

```bash
# Generate a Twitter post
python generate.py --platform twitter

# Generate an Instagram post about community
python generate.py --platform instagram --topic "community"

# Generate 3 LinkedIn posts
python generate.py --platform linkedin --count 3

# Generate a long-form LinkedIn post
python generate.py --platform linkedin --length long

# Generate without hashtags
python generate.py --platform twitter --no-hashtags

# Custom topic and tone
python generate.py --platform instagram --topic "product launch" --tone "excited but authentic"
```

### Python API

You can also use the generator programmatically:

```python
from post_generator import SocialMediaPostGenerator
import os

# Initialize generator
generator = SocialMediaPostGenerator(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o-mini"  # or "gpt-4" for better quality
)

# Generate a single post
post = generator.generate_post(
    platform="twitter",
    topic="community trust",
    length="medium",
    include_hashtags=True
)
print(post)

# Generate multiple variations
posts = generator.generate_multiple_posts(
    count=3,
    platform="instagram",
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
| `--platform` | Platform: twitter, instagram, linkedin, facebook | twitter |
| `--topic` | Specific topic to focus on | None |
| `--tone` | Tone override | Brand voice |
| `--length` | Post length: short, medium, long | medium |
| `--count` | Number of posts to generate | 1 |
| `--no-hashtags` | Don't include hashtags | False |
| `--api-key` | OpenAI API key | Uses env var |
| `--model` | OpenAI model to use | gpt-4o-mini |

## Platform-Specific Details

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

### Using Different Models

- `gpt-4o-mini`: Fast and cost-effective (default)
- `gpt-4o`: Better quality, slightly more expensive
- `gpt-4`: Highest quality, most expensive

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

### "OpenAI API key required" error
- Make sure you've set `OPENAI_API_KEY` environment variable or passed `--api-key`
- Verify your API key is valid at [OpenAI Platform](https://platform.openai.com/)

### Posts don't match brand voice
- Review and update `brand_context.py` with more specific brand guidelines
- Try adjusting the `--tone` parameter
- Consider using a more advanced model like `gpt-4o`

### Posts are too generic
- Use more specific `--topic` values
- Add more detail to your brand context in `brand_context.py`
- Try generating multiple posts and selecting the best

## Cost Considerations

- `gpt-4o-mini`: ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens
- Each post generation uses roughly 500-1000 tokens
- Very cost-effective for regular use

## Next Steps

Consider extending this tool with:
- Integration with Notion API to automatically pull latest docs
- Scheduled post generation
- Post analytics and A/B testing
- Integration with social media APIs for direct publishing
- Template system for common post types

## License

MIT License - feel free to use and modify for your needs.
