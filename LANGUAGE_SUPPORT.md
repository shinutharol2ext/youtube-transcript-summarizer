# Language Support Guide

The YouTube Transcript Summarizer supports 25+ major world languages with automatic detection and translation capabilities.

## Supported Languages

### Tier 1: Major Global Languages

| Language | Code | Native Name | Notes |
|----------|------|-------------|-------|
| English | `en` | English | Default fallback |
| Spanish | `es` | Español | 2nd most spoken |
| Chinese (Simplified) | `zh-Hans` | 简体中文 | Mainland China |
| Chinese (Traditional) | `zh-Hant` | 繁體中文 | Taiwan, Hong Kong |
| Hindi | `hi` | हिन्दी | India |
| Arabic | `ar` | العربية | Middle East, North Africa |
| Portuguese | `pt` | Português | Brazil, Portugal |
| Bengali | `bn` | বাংলা | Bangladesh, India |
| Russian | `ru` | Русский | Russia, Eastern Europe |
| Japanese | `ja` | 日本語 | Japan |

### Tier 2: European Languages

| Language | Code | Native Name | Notes |
|----------|------|-------------|-------|
| German | `de` | Deutsch | Germany, Austria |
| French | `fr` | Français | France, Africa |
| Italian | `it` | Italiano | Italy |
| Polish | `pl` | Polski | Poland |
| Ukrainian | `uk` | Українська | Ukraine |
| Dutch | `nl` | Nederlands | Netherlands |

### Tier 3: Asian Languages

| Language | Code | Native Name | Notes |
|----------|------|-------------|-------|
| Korean | `ko` | 한국어 | South Korea |
| Turkish | `tr` | Türkçe | Turkey |
| Vietnamese | `vi` | Tiếng Việt | Vietnam |
| Thai | `th` | ไทย | Thailand |
| Indonesian | `id` | Bahasa Indonesia | Indonesia |

### Tier 4: Indian Languages

| Language | Code | Native Name | Notes |
|----------|------|-------------|-------|
| Malayalam | `ml` | മലയാളം | Kerala, India |
| Tamil | `ta` | தமிழ் | Tamil Nadu, India |
| Telugu | `te` | తెలుగు | Andhra Pradesh, India |
| Marathi | `mr` | मराठी | Maharashtra, India |

## Usage Examples

### Automatic Language Detection

The tool automatically tries all supported languages in order of global usage:

```bash
python3 -m src.cli "https://www.youtube.com/watch?v=VIDEO_ID"
```

The tool will:
1. Try English first (most common)
2. Then Spanish, Chinese, Hindi, Arabic, etc.
3. Stop when it finds an available transcript
4. Display which language was detected

### Specify Language Explicitly

If you know the video language, specify it for faster processing:

```bash
# Spanish video
python3 -m src.cli "https://www.youtube.com/watch?v=VIDEO_ID" --source-lang es

# Chinese (Simplified) video
python3 -m src.cli "https://www.youtube.com/watch?v=VIDEO_ID" --source-lang zh-Hans

# Hindi video
python3 -m src.cli "https://www.youtube.com/watch?v=VIDEO_ID" --source-lang hi

# Arabic video
python3 -m src.cli "https://www.youtube.com/watch?v=VIDEO_ID" --source-lang ar

# Japanese video
python3 -m src.cli "https://www.youtube.com/watch?v=VIDEO_ID" --source-lang ja

# German video
python3 -m src.cli "https://www.youtube.com/watch?v=VIDEO_ID" --source-lang de

# French video
python3 -m src.cli "https://www.youtube.com/watch?v=VIDEO_ID" --source-lang fr

# Korean video
python3 -m src.cli "https://www.youtube.com/watch?v=VIDEO_ID" --source-lang ko

# Russian video
python3 -m src.cli "https://www.youtube.com/watch?v=VIDEO_ID" --source-lang ru

# Portuguese video
python3 -m src.cli "https://www.youtube.com/watch?v=VIDEO_ID" --source-lang pt
```

### Translation Support

Translate transcripts between supported language pairs:

```bash
# Spanish to English
python3 -m src.cli "https://www.youtube.com/watch?v=VIDEO_ID" --source-lang es --translate-to en

# Chinese to English
python3 -m src.cli "https://www.youtube.com/watch?v=VIDEO_ID" --source-lang zh-Hans --translate-to en

# Hindi to English
python3 -m src.cli "https://www.youtube.com/watch?v=VIDEO_ID" --source-lang hi --translate-to en

# English to Spanish
python3 -m src.cli "https://www.youtube.com/watch?v=VIDEO_ID" --source-lang en --translate-to es

# Japanese to English
python3 -m src.cli "https://www.youtube.com/watch?v=VIDEO_ID" --source-lang ja --translate-to en
```

**Note**: Not all language pairs support translation. YouTube's translation API has limitations.

## AI Summarization in Multiple Languages

AWS Bedrock models support multilingual content:

### Best Models for Multilingual Content

**Amazon Nova:**
- Supports: English, Spanish, French, German, Italian, Portuguese, Japanese, Korean, Chinese, Arabic, Hindi
- Best for: Cost-effective multilingual summarization

**Anthropic Claude:**
- Supports: 100+ languages including all major world languages
- Best for: High-quality multilingual understanding

**Meta Llama:**
- Supports: English, Spanish, French, German, Italian, Portuguese, Hindi, Thai, Vietnamese
- Best for: Open-source multilingual processing

**Mistral:**
- Supports: English, French, German, Spanish, Italian
- Best for: European languages

### Example: Multilingual Workflow

```bash
# Process Spanish video with AI summary
export BEDROCK_MODEL_ID=amazon.nova-lite-v1:0
python3 -m src.cli "https://www.youtube.com/watch?v=SPANISH_VIDEO" --source-lang es

# Process Chinese video with Claude (best multilingual support)
export BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
python3 -m src.cli "https://www.youtube.com/watch?v=CHINESE_VIDEO" --source-lang zh-Hans

# Process Hindi video and translate to English
python3 -m src.cli "https://www.youtube.com/watch?v=HINDI_VIDEO" --source-lang hi --translate-to en
```

## Language Detection Order

When no language is specified, the tool tries languages in this order:

1. English (en) - Most common on YouTube
2. Spanish (es) - 2nd most spoken language
3. Chinese Simplified (zh-Hans) - Largest population
4. Chinese Traditional (zh-Hant) - Taiwan, Hong Kong
5. Hindi (hi) - India
6. Arabic (ar) - Middle East, North Africa
7. Portuguese (pt) - Brazil, Portugal
8. Bengali (bn) - Bangladesh, India
9. Russian (ru) - Russia, Eastern Europe
10. Japanese (ja) - Japan
11. German (de) - Germany, Austria
12. French (fr) - France, Africa
13. Korean (ko) - South Korea
14. Italian (it) - Italy
15. Turkish (tr) - Turkey
16. Vietnamese (vi) - Vietnam
17. Polish (pl) - Poland
18. Ukrainian (uk) - Ukraine
19. Dutch (nl) - Netherlands
20. Thai (th) - Thailand
21. Indonesian (id) - Indonesia
22. Malayalam (ml) - Kerala, India
23. Tamil (ta) - Tamil Nadu, India
24. Telugu (te) - Andhra Pradesh, India
25. Marathi (mr) - Maharashtra, India

This order is based on:
- Global internet usage statistics
- YouTube content availability
- Language speaker populations

## Troubleshooting

### Language Not Available

If you get "Transcript not available in the requested language":

1. **Try auto-detection**: Remove `--source-lang` to let the tool try all languages
2. **Check available languages**: Some videos only have transcripts in specific languages
3. **Try translation**: Use `--translate-to` to translate from available language

### Translation Not Supported

If you get "The requested language is not translatable":

1. **Check language pair**: Not all language pairs support translation
2. **Use AI summarization**: AI models can understand multiple languages without translation
3. **Fetch original**: Get transcript in original language and use AI to summarize

### Chinese Language Codes

YouTube uses different codes for Chinese variants:
- `zh-Hans` - Simplified Chinese (Mainland China)
- `zh-Hant` - Traditional Chinese (Taiwan, Hong Kong)
- `zh-CN` - Alternative for Simplified
- `zh-TW` - Alternative for Traditional

Try both variants if one doesn't work.

## Best Practices

### For Content Creators

1. **Enable auto-generated captions** on your YouTube videos
2. **Add manual captions** for better accuracy
3. **Provide multiple language captions** for international audiences

### For Users

1. **Specify language when known** for faster processing
2. **Use auto-detection** when unsure
3. **Try translation** for cross-language understanding
4. **Use Claude models** for best multilingual AI summarization

## Future Enhancements

Planned language features:
- Support for 50+ additional languages
- Improved language detection accuracy
- Multi-language output (summaries in multiple languages)
- Language-specific AI prompts for better summarization
- Automatic language identification from video metadata

## Contributing

To add support for a new language:
1. Add language code to `orchestrator.py` language list
2. Test with sample videos in that language
3. Update documentation
4. Submit a pull request

## Resources

- [YouTube Transcript API Language Codes](https://github.com/jdepoix/youtube-transcript-api)
- [ISO 639-1 Language Codes](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)
- [AWS Bedrock Language Support](https://docs.aws.amazon.com/bedrock/latest/userguide/models-features.html)
