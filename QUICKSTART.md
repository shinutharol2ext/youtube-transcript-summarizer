# Quick Start Guide

Get started with AI-powered YouTube video summarization in 5 minutes!

## 1. Install Dependencies

```bash
cd youtube-transcript-summarizer/youtube-transcript-summarizer
pip install -r requirements.txt
pip install -e .
```

## 2. Configure AWS (Choose One Method)

### Method A: AWS CLI (Easiest)
```bash
aws configure
# Enter your AWS credentials when prompted
```

### Method B: Environment File
```bash
cp .env.example .env
# Edit .env and add your AWS credentials
```

## 3. Enable Bedrock Access

1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Click "Model access" in the sidebar
3. Request access to your preferred model family:
   - **Amazon Nova** - Best for cost/performance balance
   - **Anthropic Claude** - Best for quality
   - **Meta Llama** - Open source option
   - **Mistral AI** - Efficient and fast
   - **AI21 Jamba** - Long context windows
   - **Cohere Command** - Balanced performance
4. Wait for approval (usually instant)

## 4. Run Your First Summary

```bash
# Make sure you're in the project directory
cd youtube-transcript-summarizer/youtube-transcript-summarizer

# Run the tool
python3 -m src.cli "https://www.youtube.com/watch?v=YOUR_VIDEO_ID"
```

That's it! The tool will:
1. ✅ Fetch the video transcript
2. ✅ Use AWS Bedrock AI to generate a summary
3. ✅ Extract key points with timestamps
4. ✅ Save everything to a markdown file

## Try Different Models

```bash
# Cost-effective (recommended for most users)
export BEDROCK_MODEL_ID=amazon.nova-lite-v1:0
python3 -m src.cli "https://www.youtube.com/watch?v=VIDEO_ID"

# High quality
export BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
python3 -m src.cli "https://www.youtube.com/watch?v=VIDEO_ID"

# Fast and efficient
export BEDROCK_MODEL_ID=meta.llama3-1-8b-instruct-v1:0
python3 -m src.cli "https://www.youtube.com/watch?v=VIDEO_ID"
```

## Example Output

```markdown
# Video Title

## Overview
This video covers the fundamentals of machine learning, including supervised and unsupervised learning approaches. The presenter explains key concepts with practical examples and demonstrates how to build your first ML model.

## Key Points
- **00:45** - Introduction to machine learning and its applications in modern technology
- **03:20** - Explanation of supervised learning with classification examples
- **07:15** - Deep dive into unsupervised learning and clustering algorithms
- **12:30** - Practical demonstration of building a simple ML model
- **18:00** - Best practices for model evaluation and validation

## Full Transcript
[Complete transcript text...]
```

## Troubleshooting

**"Access Denied" Error?**
- Make sure you've requested Bedrock model access (Step 3)
- Check your IAM permissions include `bedrock:InvokeModel`

**"Credentials Not Found" Error?**
- Run `aws configure` or create a `.env` file with your credentials

**AI Summary Not Working?**
- Don't worry! The tool automatically falls back to rule-based summarization
- Check the console for warning messages

## Next Steps

- Read [BEDROCK_SETUP.md](BEDROCK_SETUP.md) for detailed AWS configuration
- Check [README.md](README.md) for all features and 25+ supported models
- Try different model families (Nova, Claude, Llama, Mistral, Jamba, Cohere)
- Compare quality vs cost tradeoffs between models

## Cost Estimate

Typical costs per video (using recommended models):

**Amazon Nova Lite (recommended):**
- 5-minute video: < $0.01
- 30-minute video: ~$0.01
- 1-hour video: ~$0.02

**Anthropic Claude 3.5 Haiku:**
- 5-minute video: ~$0.01
- 30-minute video: ~$0.02
- 1-hour video: ~$0.03-0.05

**Meta Llama 3.1 8B:**
- 5-minute video: < $0.01
- 30-minute video: < $0.01
- 1-hour video: ~$0.01-0.02
