# Changelog

All notable changes to this project will be documented in this file.

## [2.1.0] - 2026-02-17

### Added
- Support for 25+ major world languages with automatic detection
- Language support for:
  - English, Spanish, Chinese (Simplified & Traditional)
  - Hindi, Arabic, Portuguese, Bengali, Russian
  - Japanese, German, French, Korean, Italian
  - Turkish, Vietnamese, Polish, Ukrainian, Dutch
  - Thai, Indonesian, Malayalam, Tamil, Telugu, Marathi
- Automatic language detection that tries all supported languages
- Improved language fallback mechanism
- Comprehensive language support documentation (LANGUAGE_SUPPORT.md)

### Changed
- Updated orchestrator to try 25+ languages automatically instead of just Malayalam and English
- Enhanced CLI help text with more language examples
- Updated README with comprehensive language support information

### Documentation
- Created LANGUAGE_SUPPORT.md with complete language guide
- Updated README.md with 25+ language examples
- Added language-specific usage examples
- Added multilingual AI summarization guidance

## [2.0.0] - 2026-02-17

### Added
- Support for 25+ AWS Bedrock models across 6 model families:
  - Amazon Nova (micro, lite, pro)
  - Anthropic Claude (3.5 Sonnet, 3.5 Haiku, 3 Opus, 3 Sonnet, 3 Haiku)
  - Meta Llama (3.1: 8B/70B/405B, 3.2: 1B/3B/11B/90B)
  - Mistral AI (7B, Large, Mixtral 8x7B)
  - AI21 Labs Jamba (1.5 Mini, 1.5 Large)
  - Cohere Command (R, R+)
- Automatic model family detection from model ID
- Model-specific request/response format handling
- Enhanced BedrockClient with multi-model support

### Changed
- Updated `src/bedrock_client.py` to support all Bedrock model families
- Updated all documentation to reflect multi-model support
- Simplified configuration (removed AI_PROVIDER variable)
- Enhanced error messages with model-specific guidance

### Removed
- OpenAI integration (removed `src/openai_client.py`)
- OpenAI-related documentation (OPENAI_SETUP.md, MULTI_PROVIDER_GUIDE.md)
- AI_PROVIDER configuration variable
- openai package dependency

### Documentation
- Updated README.md with all 25+ supported models
- Updated BEDROCK_SETUP.md with multi-model setup instructions
- Updated AI_IMPLEMENTATION.md with technical details for all model families
- Updated QUICKSTART.md with model selection examples
- Updated setup.py and pyproject.toml descriptions

## [1.0.0] - 2026-02-16

### Added
- Initial release with AWS Bedrock Nova support
- OpenAI ChatGPT integration
- Multi-provider support (Bedrock and OpenAI)
- AI-powered summarization with automatic fallback
- Malayalam and English transcript support
- Property-based testing with Hypothesis

### Features
- YouTube transcript extraction
- AI-powered summary generation
- Key point extraction with timestamps
- Markdown output format
- Flexible model selection
- Comprehensive error handling
