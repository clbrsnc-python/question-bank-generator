import json
from google import genai
from google.genai import types

CANDIDATE_MODELS = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]

def index_learning_resources(raw_resource_text: str, syllabus_tree: dict, api_key: str) -> dict:
    """
    Chunks learning resource text and tags passages strictly to topics in the syllabus_tree.
    Filters out any out-of-syllabus material.
    """
    clean_key = api_key.strip().strip('"').strip("'")
    client = genai.Client(api_key=clean_key)
    
    # Extract list of valid chapters and topics for explicit prompting
    valid_topics = []
    for ch in syllabus_tree.get("chapters", []):
        valid_topics.append(f"Chapter: {ch.get('chapter_name')}, Topics: {', '.join(ch.get('topics', []))}")
    
    topics_str = "\n".join(valid_topics)
    
    prompt = f"""
    You are an academic content editor. Map the following learning resource content strictly to the allowed Syllabus Topics.
    Ignore any content that does not match these syllabus topics.
    
    Allowed Syllabus Topics:
    ---
    {topics_str}
    ---
    
    Learning Resource Content:
    ---
    {raw_resource_text[:10000]}
    ---
    
    Output a JSON object mapping each Chapter Name to relevant factual passages extracted from the resource:
    {{
      "Chapter Name 1": [
        "Key factual passage or formula ground truth 1",
        "Key factual passage or formula ground truth 2"
      ]
    }}
    
    Output strictly valid JSON.
    """
    
    response = None
    last_err = None
    for model_name in CANDIDATE_MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )
            if response and response.text:
                break
        except Exception as e:
            last_err = e
            continue
            
    if response is None or not response.text:
        raise RuntimeError(f"Gemini API error during resource indexing: {str(last_err)}")
    
    try:
        indexed_content = json.loads(response.text)
        return indexed_content
    except Exception as e:
        # Fallback: simple text blob under first chapter
        ch_name = syllabus_tree.get("chapters", [{}])[0].get("chapter_name", "General")
        return {ch_name: [raw_resource_text[:3000]]}
