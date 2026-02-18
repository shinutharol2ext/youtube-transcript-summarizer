# Implementation Plan: YouTube Transcript Summarizer

## Overview

This implementation plan breaks down the YouTube Transcript Summarizer into discrete coding tasks. Each task builds incrementally on previous work, with testing integrated throughout to validate functionality early. The implementation follows a bottom-up approach: core utilities → data models → individual components → integration → CLI interface.

## Tasks

- [x] 1. Set up project structure and core data models
  - Create directory structure (src/, tests/)
  - Define data models: TranscriptSegment, Transcript, KeyPoint, Summary, YouTubeURL, MarkdownDocument, ProcessingError, ErrorType
  - Define Result type (Ok, Err) for error handling
  - Set up pytest and hypothesis testing frameworks
  - Create requirements.txt with dependencies: youtube-transcript-api, hypothesis, pytest
  - _Requirements: All (foundational)_

- [x] 1.1 Write property test for Result type
  - **Property: Result type preserves values**
  - **Validates: Requirements N/A (infrastructure)**

- [x] 2. Implement URL validation component
  - [x] 2.1 Implement extract_video_id function
    - Support youtube.com/watch?v=VIDEO_ID format
    - Support youtu.be/VIDEO_ID format
    - Handle URLs with additional query parameters
    - Return None for invalid URLs
    - _Requirements: 1.2, 1.4_
  
  - [x] 2.2 Implement validate_youtube_url function
    - Use extract_video_id to parse URL
    - Return Ok(YouTubeURL) for valid URLs
    - Return Err(ProcessingError) with INVALID_URL for invalid URLs
    - _Requirements: 1.1, 1.3_
  
  - [x] 2.3 Write property test for URL validation
    - **Property 1: Valid YouTube URLs are accepted**
    - **Validates: Requirements 1.1, 1.4**
  
  - [x] 2.4 Write property test for video ID extraction
    - **Property 2: Video ID extraction consistency**
    - **Validates: Requirements 1.2**
  
  - [x] 2.5 Write property test for invalid URL rejection
    - **Property 3: Invalid URLs are rejected with errors**
    - **Validates: Requirements 1.3**
  
  - [x] 2.6 Write unit tests for URL validation
    - Test specific valid URL formats
    - Test specific invalid URL examples
    - Test edge cases (empty string, malformed URLs)
    - _Requirements: 1.1, 1.2, 1.3_

- [x] 3. Implement transcript fetching component
  - [x] 3.1 Implement fetch_transcript function
    - Use youtube-transcript-api to fetch transcript
    - Request English language transcripts
    - Return Ok(Transcript) on success
    - Return Err with VIDEO_NOT_FOUND for missing videos
    - Return Err with TRANSCRIPT_NOT_AVAILABLE when no transcript exists
    - Return Err with LANGUAGE_NOT_AVAILABLE when English not available
    - Handle network errors with NETWORK_ERROR
    - _Requirements: 2.1, 2.3, 5.1, 5.2, 7.2, 7.3_
  
  - [x] 3.2 Implement get_plain_text function
    - Concatenate all transcript segments in chronological order
    - Join segments with spaces
    - Return complete plain text string
    - _Requirements: 2.2_
  
  - [x] 3.3 Write property test for plain text ordering
    - **Property 4: Plain text preserves chronological order**
    - **Validates: Requirements 2.2**
  
  - [x] 3.4 Write unit tests for transcript fetching
    - Mock youtube-transcript-api responses
    - Test successful transcript retrieval
    - Test error cases (video not found, no transcript, wrong language)
    - Test network error handling
    - _Requirements: 2.1, 2.3, 5.2, 7.2, 7.3_

- [x] 4. Checkpoint - Ensure core data retrieval works
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement timestamp formatting utilities
  - [x] 5.1 Implement format_timestamp function
    - Format seconds as MM:SS for videos under 1 hour
    - Format seconds as HH:MM:SS for videos 1 hour or longer
    - Handle edge cases (0 seconds, fractional seconds)
    - _Requirements: 3.4_
  
  - [x] 5.2 Write property test for timestamp formatting
    - **Property 6: Timestamp format matches video duration**
    - **Validates: Requirements 3.4**
  
  - [x] 5.3 Write unit tests for timestamp formatting
    - Test specific durations (59s, 60s, 3599s, 3600s)
    - Test edge cases (0s, fractional seconds)
    - _Requirements: 3.4_

- [x] 6. Implement summarization component
  - [x] 6.1 Implement generate_summary function
    - Integrate with LLM API (OpenAI or Anthropic)
    - Create prompt with transcript text
    - Parse LLM response to extract overview and key points
    - Associate timestamps with key points based on transcript segments
    - Return Summary object with overview and key_points list
    - _Requirements: 3.1, 3.2, 3.3_
  
  - [x] 6.2 Implement extract_key_points helper function
    - Use LLM to identify important moments in transcript
    - Match key points to transcript segments for timestamps
    - Format timestamps using format_timestamp
    - Rank by relevance if needed
    - _Requirements: 3.2, 3.3_
  
  - [x] 6.3 Write property test for key point timestamps
    - **Property 5: All key points have timestamps**
    - **Validates: Requirements 3.3**
  
  - [x] 6.4 Write unit tests for summarization
    - Mock LLM API responses
    - Test summary generation with sample transcripts
    - Test key point extraction and timestamp association
    - Test error handling for API failures
    - _Requirements: 3.1, 3.2, 3.3, 7.5_

- [x] 7. Implement markdown generation component
  - [x] 7.1 Implement format_transcript_section function
    - Create markdown section with "Full Transcript" header
    - Include plain text transcript
    - _Requirements: 4.2_
  
  - [x] 7.2 Implement format_summary_section function
    - Create "Overview" section with summary text
    - Create "Key Points" section with bulleted list
    - Format each key point with timestamp and text
    - _Requirements: 4.3, 4.4_
  
  - [x] 7.3 Implement generate_markdown function
    - Combine video title as main header
    - Include summary section (overview + key points)
    - Include transcript section
    - Ensure proper markdown syntax (headers, lists, formatting)
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [x] 7.4 Write property test for markdown sections
    - **Property 7: Markdown contains all required sections**
    - **Validates: Requirements 4.2, 4.3, 4.4**
  
  - [x] 7.5 Write property test for markdown validity
    - **Property 8: Markdown is syntactically valid**
    - **Validates: Requirements 4.5**
  
  - [x] 7.6 Write unit tests for markdown generation
    - Test section formatting with sample data
    - Test complete markdown document structure
    - Verify markdown syntax correctness
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 8. Checkpoint - Ensure content generation works
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Implement file writing component
  - [x] 9.1 Implement sanitize_filename function
    - Remove invalid characters: / \ : * ? " < > |
    - Replace spaces with underscores or hyphens
    - Limit length to 255 characters
    - Handle empty results (provide default name)
    - _Requirements: 8.3_
  
  - [x] 9.2 Implement handle_filename_conflict function
    - Check if file exists at given path
    - If exists, append number (e.g., filename_1.md, filename_2.md)
    - Find next available number
    - Return unique path
    - _Requirements: 8.4_
  
  - [x] 9.3 Implement save_markdown function
    - Generate filename from video title using sanitize_filename
    - Handle filename conflicts using handle_filename_conflict
    - Write markdown content to file
    - Return Ok(Path) on success
    - Return Err with FILE_WRITE_ERROR on failure
    - _Requirements: 8.1, 8.2_
  
  - [x] 9.4 Write property test for filename sanitization
    - **Property 12: Filenames are sanitized**
    - **Validates: Requirements 8.3**
  
  - [x] 9.5 Write property test for filename conflict resolution
    - **Property 13: Filename conflicts are resolved**
    - **Validates: Requirements 8.4**
  
  - [x] 9.6 Write property test for successful file creation
    - **Property 10: Successful processing creates output file**
    - **Validates: Requirements 8.1**
  
  - [x] 9.7 Write property test for filename generation
    - **Property 11: Filenames are generated from titles**
    - **Validates: Requirements 8.2**
  
  - [x] 9.8 Write unit tests for file operations
    - Test filename sanitization with specific problematic characters
    - Test conflict resolution with existing files
    - Test file writing and reading
    - Test error handling (permissions, disk space)
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 10. Implement error handling and propagation
  - [x] 10.1 Implement process_video orchestration function
    - Chain all components using Result type
    - Propagate errors through pipeline
    - Return final Result[Path, ProcessingError]
    - _Requirements: 7.1_
  
  - [x] 10.2 Write property test for error propagation
    - **Property 9: All errors produce descriptive messages**
    - **Validates: Requirements 7.1**
  
  - [x] 10.3 Write unit tests for error handling
    - Test error propagation through pipeline
    - Verify error messages for each error type
    - Test error recovery scenarios
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 11. Implement CLI interface
  - [x] 11.1 Implement parse_arguments function
    - Use argparse to define CLI arguments
    - Required argument: YouTube URL
    - Optional argument: output directory
    - Optional argument: API key for LLM
    - Return parsed Arguments object
    - _Requirements: 1.1_
  
  - [x] 11.2 Implement main function
    - Parse command-line arguments
    - Call process_video with URL
    - Handle Result: print success message or error
    - Return appropriate exit code (0 for success, 1 for error)
    - _Requirements: All (integration)_
  
  - [x] 11.3 Write integration tests for CLI
    - Test end-to-end processing with mocked APIs
    - Test error handling through CLI
    - Test output file creation
    - _Requirements: All_

- [x] 12. Final checkpoint and integration validation
  - Ensure all tests pass, ask the user if questions arise.

- [x] 13. Add configuration and documentation
  - [x] 13.1 Create configuration file support
    - Support .env file for API keys
    - Support config file for default settings
    - _Requirements: 6.1, 6.2, 6.3_
  
  - [x] 13.2 Create README.md
    - Installation instructions
    - Usage examples
    - Configuration guide
    - Troubleshooting section
    - _Requirements: All (documentation)_
  
  - [x] 13.3 Add example output
    - Include sample markdown output in repository
    - Document expected output format
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

## Notes

- All tasks are required for comprehensive implementation
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties with minimum 100 iterations
- Unit tests validate specific examples and edge cases
- LLM API integration requires API key configuration (OpenAI or Anthropic)
- The youtube-transcript-api library handles the YouTube API interaction
- File operations should be tested with temporary directories to avoid side effects
