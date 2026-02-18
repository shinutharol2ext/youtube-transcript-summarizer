# YouTube Transcript Summarizer

A command-line tool that processes YouTube videos in 25+ languages to generate plain text transcripts and structured markdown summaries with AI-powered key points and timestamps using AWS Bedrock models.

## Features

- Extract transcripts from YouTube videos in 25+ languages
- Support for major world languages including:
  - English, Spanish, Chinese (Simplified & Traditional)
  - Hindi, Arabic, Portuguese, Bengali, Russian
  - Japanese, German, French, Korean, Italian
  - Turkish, Vietnamese, Polish, Ukrainian, Dutch
  - Thai, Indonesian, Malayalam, Tamil, Telugu, Marathi
  - And many more...
- Automatic language detection (tries 25+ languages automatically)
- Translation support for compatible language pairs
- **AI-powered summarization using AWS Bedrock (25+ models supported)**
- Support for Amazon Nova, Claude, Llama, Mistral, Jamba, and Cohere models
- Generate intelligent overview summaries
- Identify key points with timestamps using AI
- Output structured markdown documents
- Support for educational content, interviews, and tutorials
- Fallback to rule-based summarization if AI is unavailable

## Installation

1. Clone the repository
2. Navigate to the project directory:

```bash
cd youtube-transcript-summarizer/youtube-transcript-summarizer
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Install the package in development mode:

```bash
pip install -e .
```

5. Configure AWS Bedrock:
   - See [AWS Bedrock Setup Guide](BEDROCK_SETUP.md) for detailed instructions
   - See [Quick Start Guide](QUICKSTART.md) for 5-minute setup

## Usage

### Quick Start

```bash
# 1. Navigate to project directory
cd youtube-transcript-summarizer/youtube-transcript-summarizer

# 2. Configure AWS credentials
aws configure

# 3. Set up environment
cp .env.example .env
# Edit .env and add:
# AWS_REGION=us-east-1
# BEDROCK_MODEL_ID=amazon.nova-lite-v1:0

# 4. Run the tool
python3 -m src.cli "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Basic Usage

```bash
python3 -m src.cli https://www.youtube.com/watch?v=VIDEO_ID
```

### With Custom Output Directory

```bash
python3 -m src.cli https://www.youtube.com/watch?v=VIDEO_ID -o ./output
```

### Language Options

The tool supports 25+ major world languages with automatic detection:

**Supported Languages:**
- English (en), Spanish (es), Chinese Simplified (zh-Hans), Chinese Traditional (zh-Hant)
- Hindi (hi), Arabic (ar), Portuguese (pt), Bengali (bn), Russian (ru)
- Japanese (ja), German (de), French (fr), Korean (ko), Italian (it)
- Turkish (tr), Vietnamese (vi), Polish (pl), Ukrainian (uk), Dutch (nl)
- Thai (th), Indonesian (id), Malayalam (ml), Tamil (ta), Telugu (te), Marathi (mr)

```bash
# Auto-detect language (tries 25+ languages automatically)
python3 -m src.cli https://www.youtube.com/watch?v=VIDEO_ID

# Specify source language explicitly
python3 -m src.cli https://www.youtube.com/watch?v=VIDEO_ID --source-lang es

# Chinese (Simplified)
python3 -m src.cli https://www.youtube.com/watch?v=VIDEO_ID --source-lang zh-Hans

# Chinese (Traditional)
python3 -m src.cli https://www.youtube.com/watch?v=VIDEO_ID --source-lang zh-Hant

# Hindi
python3 -m src.cli https://www.youtube.com/watch?v=VIDEO_ID --source-lang hi

# Arabic
python3 -m src.cli https://www.youtube.com/watch?v=VIDEO_ID --source-lang ar

# Translate transcript (for compatible language pairs)
python3 -m src.cli https://www.youtube.com/watch?v=VIDEO_ID --source-lang es --translate-to en
```

### Model Selection

The tool supports 25+ AWS Bedrock models across 6 model families:

**Amazon Nova (Recommended):**
- `amazon.nova-micro-v1:0` - Fastest, most cost-effective
- `amazon.nova-lite-v1:0` - Balanced performance (default)
- `amazon.nova-pro-v1:0` - Highest quality

**Anthropic Claude:**
- `anthropic.claude-3-5-sonnet-20241022-v2:0` - Latest, most capable
- `anthropic.claude-3-5-haiku-20241022-v1:0` - Fast and efficient
- `anthropic.claude-3-opus-20240229-v1:0` - Powerful reasoning
- `anthropic.claude-3-sonnet-20240229-v1:0` - Balanced
- `anthropic.claude-3-haiku-20240307-v1:0` - Fast

**Meta Llama:**
- `meta.llama3-1-405b-instruct-v1:0` - Largest, most capable
- `meta.llama3-1-70b-instruct-v1:0` - Strong performance
- `meta.llama3-1-8b-instruct-v1:0` - Fast and efficient
- `meta.llama3-2-90b-instruct-v1:0` - Latest large model
- `meta.llama3-2-11b-instruct-v1:0` - Balanced
- `meta.llama3-2-3b-instruct-v1:0` - Compact
- `meta.llama3-2-1b-instruct-v1:0` - Ultra-fast

**Mistral AI:**
- `mistral.mistral-large-2407-v1:0` - Latest, most capable
- `mistral.mistral-large-2402-v1:0` - Powerful
- `mistral.mixtral-8x7b-instruct-v0:1` - Mixture of experts
- `mistral.mistral-7b-instruct-v0:2` - Fast and efficient

**AI21 Labs Jamba:**
- `ai21.jamba-1-5-large-v1:0` - Large context window
- `ai21.jamba-1-5-mini-v1:0` - Efficient

**Cohere Command:**
- `cohere.command-r-plus-v1:0` - Enhanced capabilities
- `cohere.command-r-v1:0` - Balanced

**Switch models by editing `.env`:**
```bash
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
```

**Disable AI (use rule-based summarization):**
```bash
USE_AI_SUMMARY=false
```

### Command-Line Options

- `url` (required): YouTube video URL
- `-o, --output-dir`: Output directory for markdown file (default: current directory)
- `--source-lang`: Source language code (e.g., en, es, zh-Hans, hi, ar, pt, ru, ja, de, fr, ko, it, ml, ta, te). If not specified, auto-detects from 25+ supported languages
- `--translate-to`: Translate transcript to target language (e.g., en for English). Note: Not all language pairs support translation
- `--api-key`: API key for LLM service (optional, for future use)

## Output Format

The tool generates a markdown file with the following structure:

```markdown
# Video Title

## Overview
Brief 2-3 sentence summary of the video content.

## Key Points
- **00:15** - First key point
- **02:30** - Second key point
- **05:45** - Third key point

## Full Transcript
Complete plain text transcript of all spoken content.
```

## Requirements

- Python 3.9+
- youtube-transcript-api
- boto3 (AWS SDK) + AWS account with Bedrock access
- hypothesis (for testing)
- pytest (for testing)

## Configuration

### AWS Bedrock Configuration

**Step 1: AWS Credentials**

The tool uses AWS Bedrock for AI-powered summarization. Configure AWS credentials:

**Method 1: AWS CLI (Recommended)**
```bash
aws configure
```

**Method 2: Environment Variables**
Copy `.env.example` to `.env` and set your AWS credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```bash
# AWS Bedrock Configuration
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=amazon.nova-lite-v1:0

# Optional: AWS credentials (if not using AWS CLI)
# AWS_ACCESS_KEY_ID=your_access_key_here
# AWS_SECRET_ACCESS_KEY=your_secret_key_here

# Enable AI
USE_AI_SUMMARY=true
```

**Step 2: Bedrock Model Options**

The tool supports 25+ AWS Bedrock models across 6 families:
- **Amazon Nova**: micro, lite, pro (recommended for cost/performance)
- **Anthropic Claude**: 3.5 Sonnet, 3.5 Haiku, 3 Opus, 3 Sonnet, 3 Haiku
- **Meta Llama**: 3.1 (8B, 70B, 405B), 3.2 (1B, 3B, 11B, 90B)
- **Mistral AI**: 7B, Large, Mixtral 8x7B
- **AI21 Jamba**: 1.5 Mini, 1.5 Large
- **Cohere Command**: R, R+

See "Model Selection" section above for complete model IDs.

**Step 3: AWS Bedrock Access**

Ensure your AWS account has:
1. Bedrock service enabled in your region
2. Access to desired models (request access in AWS Console if needed)
3. Appropriate IAM permissions for `bedrock:InvokeModel`

### Cost Estimates

Approximate costs per 1M tokens (input/output):

**Amazon Nova:**
- Nova Micro: $0.035 / $0.14
- Nova Lite: $0.06 / $0.24 (recommended)
- Nova Pro: $0.80 / $3.20

**Anthropic Claude:**
- Claude 3.5 Sonnet: $3.00 / $15.00
- Claude 3.5 Haiku: $0.80 / $4.00
- Claude 3 Opus: $15.00 / $75.00

**Meta Llama:**
- Llama 3.1 405B: $2.65 / $3.50
- Llama 3.1 70B: $0.99 / $0.99
- Llama 3.1 8B: $0.22 / $0.22

**Typical 10-minute video (~2,000 tokens):**
- Nova Lite: < $0.01
- Claude 3.5 Haiku: ~$0.01
- Llama 3.1 8B: < $0.01

### Additional Resources

- **[AWS Bedrock Setup Guide](BEDROCK_SETUP.md)** - Complete setup instructions
- **[Quick Start Guide](QUICKSTART.md)** - 5-minute quick start
- **[AI Implementation Details](AI_IMPLEMENTATION.md)** - Technical documentation
- **[Language Support Guide](LANGUAGE_SUPPORT.md)** - Complete guide to 25+ supported languages

## Testing

Run the test suite:

```bash
python3 -m pytest tests/ -v
```

Run with coverage:

```bash
python3 -m pytest tests/ --cov=src --cov-report=html
```

## Troubleshooting

### AI Summarization Issues

If AI summarization fails, the tool automatically falls back to rule-based summarization. Common issues:

**Bedrock Access Denied**
```
Error: Bedrock API error (AccessDeniedException)
```
Solution: Ensure your AWS account has Bedrock access and the model is enabled in your region.

**AWS Credentials Not Found**
```
Error: AWS connection error: Unable to locate credentials
```
Solution: Configure AWS credentials using `aws configure` or set environment variables in `.env`

**Model Not Available**
```
Error: Bedrock API error (ResourceNotFoundException)
```
Solution: Check that the model ID is correct and available in your AWS region. Try `amazon.nova-lite-v1:0` or request model access in the Bedrock console.

**Throttling Error**
```
Error: Bedrock API error (ThrottlingException)
```
Solution: You've hit rate limits. Wait a moment and try again, or request a quota increase in AWS Service Quotas.

### Video has no transcript

Some videos don't have captions/transcripts available. The tool will display an error message:
```
Error: No transcript available for this video
```

### Video is private or restricted

Private or age-restricted videos cannot be accessed:
```
Error: Video not found or is private/restricted
```

### Language not available

The requested language transcript is not available:
```
Error: Transcript not available in the requested language
```

### Translation not supported

Some language pairs don't support translation through the YouTube API:
```
Error: The requested language is not translatable
```
In this case, you can still fetch the transcript in its original language without translation.

### Network errors

If you encounter network errors, check your internet connection and try again.

## Development

### Project Structure

```
.
├── src/
│   ├── models.py              # Data models
│   ├── url_validator.py       # URL validation
│   ├── transcript_fetcher.py  # Transcript retrieval
│   ├── timestamp_formatter.py # Timestamp formatting
│   ├── bedrock_client.py      # AWS Bedrock client (25+ models)
│   ├── summarizer.py          # AI-powered summary generation
│   ├── markdown_generator.py  # Markdown formatting
│   ├── file_writer.py         # File operations
│   ├── orchestrator.py        # Pipeline orchestration
│   └── cli.py                 # Command-line interface
├── tests/                     # Test suite
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

### Running Tests

The project uses property-based testing with Hypothesis to ensure correctness:

```bash
# Run all tests
python3 -m pytest tests/

# Run specific test file
python3 -m pytest tests/test_url_validator.py

# Run with verbose output
python3 -m pytest tests/ -v
```

## Future Enhancements

- Batch processing of multiple videos
- Custom summary length configuration
- Export to other formats (PDF, HTML)
- Video title extraction from YouTube API
- Multi-language AI summarization
- Custom prompt templates for different content types
- Streaming responses for real-time summarization
- Cost tracking and analytics

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
