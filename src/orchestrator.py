"""Orchestration of the video processing pipeline."""

from pathlib import Path

from src.models import ProcessingError, Ok, Err, Result
from src.url_validator import validate_youtube_url
from src.transcript_fetcher import fetch_transcript
from src.summarizer import generate_summary
from src.markdown_generator import generate_markdown
from src.file_writer import save_markdown


def process_video(url: str, output_dir: str = ".", source_lang: str = None, translate_to: str = None) -> Result[Path, ProcessingError]:
    """
    Process a YouTube video through the complete pipeline.
    
    This function orchestrates all components:
    1. Validate URL
    2. Fetch transcript
    3. Generate summary
    4. Generate markdown
    5. Save to file
    
    Args:
        url: YouTube video URL
        output_dir: Directory to save output file
        source_lang: Source language code (default: auto-detect, tries major languages)
        translate_to: Target language for translation (default: None)
        
    Returns:
        Result containing file path on success or ProcessingError on failure
    """
    # Step 1: Validate URL
    url_result = validate_youtube_url(url)
    if isinstance(url_result, Err):
        return url_result
    
    youtube_url = url_result.value
    video_id = youtube_url.video_id
    
    # Step 2: Fetch transcript
    # If no source language specified, try major languages in order of global usage
    if source_lang:
        languages = [source_lang]
    else:
        # Try major world languages in order of internet usage
        languages = [
            'en',  # English
            'es',  # Spanish
            'zh-Hans',  # Chinese (Simplified)
            'zh-Hant',  # Chinese (Traditional)
            'hi',  # Hindi
            'ar',  # Arabic
            'pt',  # Portuguese
            'bn',  # Bengali
            'ru',  # Russian
            'ja',  # Japanese
            'de',  # German
            'fr',  # French
            'ko',  # Korean
            'it',  # Italian
            'tr',  # Turkish
            'vi',  # Vietnamese
            'pl',  # Polish
            'uk',  # Ukrainian
            'nl',  # Dutch
            'th',  # Thai
            'id',  # Indonesian
            'ml',  # Malayalam
            'ta',  # Tamil
            'te',  # Telugu
            'mr',  # Marathi
        ]
    
    transcript_result = None
    last_error = None
    for lang in languages:
        transcript_result = fetch_transcript(video_id, language=lang, translate_to=translate_to)
        if isinstance(transcript_result, Ok):
            print(f"Transcript found in language: {lang}")
            break
        else:
            last_error = transcript_result
    
    if transcript_result is None or isinstance(transcript_result, Err):
        return last_error if last_error else transcript_result
    
    transcript = transcript_result.value
    
    # Step 3: Generate summary
    summary = generate_summary(transcript)
    
    # Step 4: Generate markdown
    # Use video ID as title for now (in production, would fetch actual title)
    video_title = f"Video_{video_id}"
    markdown_doc = generate_markdown(transcript, summary, video_title)
    
    # Step 5: Save to file
    file_result = save_markdown(markdown_doc, video_title, output_dir)
    
    return file_result
