
# YouTube Video Transcript Summarizer to PDF

This project takes YouTube video URLs, extracts their transcripts, summarizes them using Google's Gemini model, and generates a structured, multi-page PDF designed for Learning Management Systems (LMS).

## Features

- Extracts video transcripts via `youtube_transcript_api`
- Summarizes transcript using Gemini (Generative AI)
- Automatically generates a title for each video
- Produces a structured multi-page PDF with sections:
  - Introduction
  - Key Sections
  - Conclusion

## Requirements

- Python 3.x
- Google API Key for Gemini
- Chrome browser for YouTube access (optional for future expansion)
- Required Python packages (see `requirements.txt`)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/video-pdf-summarizer.git
   cd video-pdf-summarizer
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Update `video_pdf.py` with:
   - Your Gemini API key
   - Desired YouTube video URLs
   - PDF output directory

4. Run the script:
   ```bash
   python video_pdf.py
   ```

## Note

This tool is intended for educational purposes. Always comply with the terms of service for YouTube and Google APIs.
