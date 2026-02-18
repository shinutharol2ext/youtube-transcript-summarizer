"""Command-line interface for YouTube Transcript Summarizer."""

import sys
import argparse
from typing import List

from src.orchestrator import process_video
from src.models import Err


def parse_arguments(args: List[str]) -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Args:
        args: Raw command line arguments
        
    Returns:
        Parsed arguments object
    """
    parser = argparse.ArgumentParser(
        description="YouTube Transcript Summarizer - Generate transcripts and summaries from YouTube videos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://www.youtube.com/watch?v=dQw4w9WgXcQ
  %(prog)s https://youtu.be/dQw4w9WgXcQ -o ./output
  %(prog)s https://youtube.com/watch?v=VIDEO_ID --source-lang ml --translate-to en
        """
    )
    
    parser.add_argument(
        'url',
        help='YouTube video URL'
    )
    
    parser.add_argument(
        '-o', '--output-dir',
        default='.',
        help='Output directory for markdown file (default: current directory)'
    )
    
    parser.add_argument(
        '--source-lang',
        help='Source language code (e.g., en, es, zh-Hans, hi, ar, pt, ru, ja, de, fr, ko, it, ml, ta, te). If not specified, auto-detects from 25+ supported languages'
    )
    
    parser.add_argument(
        '--translate-to',
        help='Translate transcript to this language (e.g., en for English)'
    )
    
    parser.add_argument(
        '--api-key',
        help='API key for LLM service (optional, for future use)'
    )
    
    return parser.parse_args(args)


def main(args: List[str] = None) -> int:
    """
    Main entry point for the CLI.
    
    Args:
        args: Command line arguments (defaults to sys.argv[1:])
        
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    if args is None:
        args = sys.argv[1:]
    
    try:
        # Parse arguments
        parsed_args = parse_arguments(args)
        
        # Process video
        print(f"Processing video: {parsed_args.url}")
        if parsed_args.source_lang:
            print(f"Source language: {parsed_args.source_lang}")
        if parsed_args.translate_to:
            print(f"Translating to: {parsed_args.translate_to}")
        
        result = process_video(
            parsed_args.url,
            parsed_args.output_dir,
            source_lang=parsed_args.source_lang,
            translate_to=parsed_args.translate_to
        )
        
        # Handle result
        if isinstance(result, Err):
            print(f"\nError: {result.error.message}", file=sys.stderr)
            if result.error.details:
                print(f"Details: {result.error.details}", file=sys.stderr)
            return 1
        
        # Success
        output_path = result.value
        print(f"\nSuccess! Transcript and summary saved to: {output_path}")
        return 0
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
