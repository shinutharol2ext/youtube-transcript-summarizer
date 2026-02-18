# AWS Bedrock Setup Guide

This guide will help you set up AWS Bedrock for AI-powered video summarization using 25+ supported models across 6 model families.

## Prerequisites

1. An AWS account
2. AWS CLI installed (optional but recommended)
3. Python 3.9 or higher

## Step 1: Enable AWS Bedrock

1. Log in to the [AWS Console](https://console.aws.amazon.com/)
2. Navigate to the **Amazon Bedrock** service
3. Select your preferred region (e.g., `us-east-1`)
4. If this is your first time using Bedrock, you may need to request access

## Step 2: Request Model Access

1. In the Bedrock console, go to **Model access** in the left sidebar
2. Click **Manage model access** or **Request model access**
3. Select the model families you want to use:
   - **Amazon Nova** (micro, lite, pro) - Usually instant approval
   - **Anthropic Claude** (3.5 Sonnet, 3.5 Haiku, 3 Opus, etc.)
   - **Meta Llama** (3.1 and 3.2 series)
   - **Mistral AI** (7B, Large, Mixtral)
   - **AI21 Labs Jamba** (1.5 Mini, 1.5 Large)
   - **Cohere Command** (R, R+)
4. Click **Request model access**
5. Wait for approval (usually instant for most models)

## Step 3: Configure AWS Credentials

### Option A: AWS CLI (Recommended)

Install the AWS CLI and configure your credentials:

```bash
# Install AWS CLI (if not already installed)
# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure credentials
aws configure
```

You'll be prompted for:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., `us-east-1`)
- Default output format (e.g., `json`)

### Option B: Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```bash
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
BEDROCK_MODEL_ID=amazon.nova-lite-v1:0
USE_AI_SUMMARY=true
```

## Step 4: Set Up IAM Permissions

Your AWS user/role needs the following permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": [
                "arn:aws:bedrock:*::foundation-model/*"
            ]
        }
    ]
}
```

To add these permissions:
1. Go to **IAM** in AWS Console
2. Find your user or role
3. Click **Add permissions** → **Create inline policy**
4. Use the JSON above
5. Name it `BedrockModelAccess` and save

## Step 5: Test the Setup

Run a test to verify everything works:

```bash
# Install dependencies
pip install -r requirements.txt

# Test with a YouTube video
python3 -m src.cli "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

If successful, you should see:
- Transcript fetched
- AI-powered summary generated
- Markdown file created

## Troubleshooting

### Error: "Access Denied"

**Problem**: Your AWS credentials don't have Bedrock permissions.

**Solution**: 
1. Check IAM permissions (Step 4)
2. Verify your credentials are correct
3. Ensure you're using the right AWS region

### Error: "Model not found"

**Problem**: The model isn't available in your region or you haven't requested access.

**Solution**:
1. Check model access in Bedrock console (Step 2)
2. Verify the model ID in your `.env` file (see supported models below)
3. Try a different region - model availability varies by region
4. Try a different model family (e.g., switch from Claude to Nova)

### Error: "Unable to locate credentials"

**Problem**: AWS credentials aren't configured.

**Solution**:
1. Run `aws configure` (Option A)
2. Or set environment variables in `.env` (Option B)
3. Check that `.env` file exists and is in the project root

### Fallback to Rule-Based Summarization

If AI summarization fails, the tool automatically falls back to rule-based summarization. You'll see a warning:

```
Warning: AI summarization failed (error details), falling back to rule-based approach
```

This ensures you always get a summary, even if Bedrock is unavailable.

## Cost Considerations

AWS Bedrock charges per token. Approximate costs per 1M tokens (input/output):

**Amazon Nova (Most Cost-Effective):**
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

**Mistral AI:**
- Mistral Large: $2.00 / $6.00
- Mixtral 8x7B: $0.45 / $0.70
- Mistral 7B: $0.15 / $0.20

**AI21 Jamba:**
- Jamba 1.5 Large: $2.00 / $8.00
- Jamba 1.5 Mini: $0.20 / $0.40

**Cohere Command:**
- Command R+: $2.50 / $10.00
- Command R: $0.50 / $1.50

**Typical 10-minute video (~2,000 tokens):**
- Nova Lite: < $0.01 (recommended)
- Claude 3.5 Haiku: ~$0.01
- Llama 3.1 8B: < $0.01
- Mistral 7B: < $0.01

**Recommendation**: Start with `amazon.nova-lite-v1:0` for the best balance of quality and cost.

## Supported Models by Region

Model availability varies by region. Common regions:
- `us-east-1` (US East - N. Virginia) - Most models available
- `us-west-2` (US West - Oregon) - Most models available
- `eu-west-1` (Europe - Ireland) - Many models
- `ap-southeast-1` (Asia Pacific - Singapore) - Many models

**Supported Model Families:**
- Amazon Nova (micro, lite, pro)
- Anthropic Claude (3.5 Sonnet, 3.5 Haiku, 3 Opus, 3 Sonnet, 3 Haiku)
- Meta Llama (3.1 and 3.2 series)
- Mistral AI (7B, Large, Mixtral)
- AI21 Labs Jamba (1.5 Mini, 1.5 Large)
- Cohere Command (R, R+)

Check the [AWS Bedrock documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html) for the latest region availability.

## Next Steps

- Try different model families to find the best fit for your use case
- Compare Nova (cost-effective), Claude (high quality), and Llama (open source)
- Adjust temperature and top_p parameters in `src/bedrock_client.py` for different output styles
- Customize the AI prompt in `src/summarizer.py` for specific content types
- Set up AWS CloudWatch to monitor Bedrock usage and costs
- Use AWS Cost Explorer to track spending by model
