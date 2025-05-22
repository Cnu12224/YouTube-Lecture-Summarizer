import os
import re
from youtube_transcript_api import YouTubeTranscriptApi
from google.generativeai import GenerativeModel, configure
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Gemini API key
GEMINI_API_KEY = "provide yor API key"
configure(api_key=GEMINI_API_KEY)

# Initialize Gemini model
model = GenerativeModel("gemini-2.0-flash")

def get_youtube_video_id(url):
    """Extract YouTube video ID from URL."""
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    raise ValueError(f"Invalid YouTube URL: {url}")

def fetch_transcript(video_url):
    """Fetch transcript from YouTube video."""
    try:
        video_id = get_youtube_video_id(video_url)
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry["text"] for entry in transcript])
    except Exception as e:
        raise Exception(f"Error fetching transcript for {video_url}: {str(e)}")

def chunk_transcript(text, max_length=500000):
    """Split transcript into chunks to handle large inputs."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1
        if current_length >= max_length:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = 0
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

def summarize_text(text, video_title="Video Summary"):
    """Summarize text using Gemini API with detailed notes prompt."""
    prompt_template = f"""
  Prompt:

I’d like you to create detailed, engaging, and comprehensive notes summarizing the content of the provided video transcript, formatted for a college Learning Management System (LMS) platform. The notes should be thorough, well-organized, and designed to help students understand and review the material effectively, especially for a long video (e.g., several hours). Please follow these guidelines to craft notes that are clear, educational, and approachable, using the structure and tone described below:

Thorough Coverage:
Include every key point, concept, subtopic, example, definition, formula, diagram (described in text), case study, anecdote, and practical application from the transcript.
Ensure no information is omitted.
For a lengthy video (e.g., an 11-hour lecture), create extensive notes that reflect the depth and complexity, potentially spanning multiple pages.
Clear Structure:
Introduction (3-4 sentences):
Briefly introduce the video’s main topic, purpose, and scope.
Explain how it connects to the course.
Provide a quick overview of the video’s structure to set the stage.
Key Sections:
Divide the content into numbered sections based on the video’s major topics or chapters.
For each section:
Use bullet points or subheadings to cover subtopics, concepts, or examples.
Explain each point clearly, including all relevant examples, definitions, formulas, diagrams (described in text), and real-world applications.
Keep explanations concise yet detailed to ensure clarity without overwhelming students.
Conclusion (3-4 sentences):
Summarize the main takeaways.
Highlight their importance to the course.
Connect them to future topics or skills students will build on.
Focus on Clarity and Engagement:
Capture all core ideas, supporting details, and practical insights.
Include specific examples, real-world applications, and descriptions of any diagrams or visuals to make the content relatable and clear.
For long videos, address all segments or chapters systematically to cover everything.
Tone:
Use a professional yet approachable tone that feels natural for college students.
Avoid overly formal or stiff language.
Steer clear of slang or overly casual phrases to maintain academic quality.
Avoid:
Don’t use filler phrases, personal opinions, or off-topic details.
Avoid repetitive phrases like “In this video,” “The presenter explains,” or “As stated.”
Length and PDF Format:
Create notes long enough to fully cover the content, potentially spanning multiple pages for long videos (e.g., 10+ pages for an 11-hour video).
Use clear section breaks, headings, and subheadings to ensure readability in a multi-page PDF.
Handling Large Transcripts:
For extensive transcripts, break the content into logical segments (e.g., by chapters or time intervals).
Weave all segments into a cohesive set of notes, ensuring no details are missed.
Transcript:

{{text}}

    **Output Format**:  
     Video Notes: {video_title}  
     Introduction  
    [Introduction to the topic, purpose, scope, and structure]  

     Key Sections  
    1. [Major Topic 1]  
       - [Subtopic or Concept]: [Detailed explanation with examples, definitions, formulas, or applications]  
       - [Subtopic or Example]: [Detailed explanation with specifics]  
       ...  
    2. [Major Topic 2]  
       - [Subtopic or Concept]: [Detailed explanation with examples, definitions, formulas, or applications]  
       - [Subtopic or Example]: [Detailed explanation with specifics]  
       ...  
    ...  

     Conclusion  
    [Summary of key takeaways, relevance to the course, and future learning connections]
    """

    # Handle large transcripts by chunking
    chunks = chunk_transcript(text, max_length=500000)
    summaries = []

    for i, chunk in enumerate(chunks, 1):
        prompt = prompt_template.format(text=chunk)
        try:
            response = model.generate_content(prompt)
            summaries.append(response.text)
        except Exception as e:
            raise Exception(f"Error summarizing transcript chunk {i}: {str(e)}")

    # Combine summaries, ensuring cohesive structure
    combined_summary = "\n\n".join(summaries)
    if len(chunks) > 1:
        # Add a final pass to ensure cohesive formatting
        final_prompt = f"""
        Combine the following partial summaries into a single, cohesive set of notes, maintaining the required structure (# Video Notes, ## Introduction, ## Key Sections, ## Conclusion). Ensure all sections are integrated logically, avoid repetition, and produce a unified document suitable for a multi-page PDF.

        **Partial Summaries**:  
        {combined_summary}

        **Output Format**:  
        # Video Notes: {video_title}  
        ## Introduction  
        [Unified introduction]  

        ## Key Sections  
        1. [Major Topic 1]  
           - [Subtopic or Concept]: [Detailed explanation]  
           ...  
        ...  

        ## Conclusion  
        [Unified conclusion]  
        """
        try:
            response = model.generate_content(final_prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Error combining summaries: {str(e)}")
    return combined_summary

def create_pdf(summary, output_filename, video_title="Video Summary"):
    """Create a PDF from the summary text."""
    try:
        doc = SimpleDocTemplate(output_filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Add title
        title = Paragraph(video_title, styles["Title"])
        story.append(title)
        story.append(Spacer(1, 12))

        # Add summary (split into paragraphs for long content)
        for paragraph in summary.split("\n\n"):
            para = Paragraph(paragraph.replace("\n", " "), styles["Normal"])
            story.append(para)
            story.append(Spacer(1, 12))

        doc.build(story)
        print(f"PDF created: {output_filename}")
    except Exception as e:
        raise Exception(f"Error creating PDF: {str(e)}")

def generate_title(transcript):
    """Generate a title for the video based on the transcript content."""
    prompt = f"""
    Generate a concise and descriptive title for a video based on the following transcript content. The title should be no more than 10 words and should capture the main topic or theme of the video.

    Transcript:
    {transcript}

    Output Format:
    Title: [Generated Title]
    """
    try:
        response = model.generate_content(prompt)
        return response.text.split("Title: ")[-1].strip()
    except Exception as e:
        raise Exception(f"Error generating title: {str(e)}")

def process_video(video_url, output_dir="provide the path where pdf should be stored"):
    """Process a single video: fetch transcript, generate title, summarize, and create PDF."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Fetch transcript
    transcript = fetch_transcript(video_url)

    # Generate title based on transcript
    video_title = generate_title(transcript)

    # Sanitize filename
    safe_title = "".join(c for c in video_title if c.isalnum() or c in (" ", "_")).rstrip()
    output_filename = os.path.join(output_dir, f"{safe_title}.pdf")

    # Summarize transcript
    summary = summarize_text(transcript, video_title)

    # Create PDF
    create_pdf(summary, output_filename, video_title)

    return output_filename

def main():
    # Example video list (replace with your LMS video URLs)
    videos = [
        {"url": "Provide URL u want to summarize "},
        # Add more videos here
    ]

    for video in videos:
        try:
            output_file = process_video(video["url"])
            print(f"Processed: {video['url']} -> {output_file}")
        except Exception as e:
            print(f"Error processing {video['url']}: {str(e)}")

if __name__ == "__main__":
    main()
