import json
import os
from pypdf import PdfReader
from google import genai
from google.genai import types

def extract_text_from_file(file_path_or_bytes, filename: str) -> str:
    """Extract raw text from PDF or TXT upload."""
    if filename.endswith(".pdf"):
        reader = PdfReader(file_path_or_bytes)
        text = "\n".join([page.extract_text() or "" for page in reader.pages])
        return text
    elif filename.endswith(".txt"):
        if isinstance(file_path_or_bytes, bytes):
            return file_path_or_bytes.decode("utf-8")
        else:
            with open(file_path_or_bytes, "r", encoding="utf-8") as f:
                return f.read()
    else:
        raise ValueError("Unsupported file format. Please upload PDF or TXT.")

def parse_syllabus(raw_text: str, subject_name: str, api_key: str) -> dict:
    """
    Parses raw syllabus text into a structured JSON boundary tree containing
    chapters, topics, subtopics, and explicit exclusions.
    """
    client = genai.Client(api_key=api_key.strip())
    
    prompt = f"""
    You are an expert curriculum design assistant. Analyze the following raw syllabus text for the subject "{subject_name}".
    Extract and structure the syllabus strictly into a JSON object with the following schema:
    
    {{
      "subject": "{subject_name}",
      "chapters": [
        {{
          "chapter_id": "CH1",
          "chapter_name": "Name of Chapter",
          "topics": ["Topic 1", "Topic 2"],
          "key_concepts": ["Concept A", "Concept B"],
          "explicit_exclusions": ["Out of scope topic if mentioned"]
        }}
      ]
    }}
    
    Raw Syllabus Text:
    ---
    {raw_text[:8000]}
    ---
    
    Output strictly valid JSON matching the schema above.
    """
    
    models_to_try = ["gemini-2.0-flash", "gemini-1.5-flash"]
    last_error = None
    
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2
                )
            )
            parsed_json = json.loads(response.text)
            return parsed_json
        except Exception as e:
            last_error = e
            continue
            
    raise RuntimeError(f"Gemini API Call failed: {str(last_error)}")
