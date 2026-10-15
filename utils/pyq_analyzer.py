import json
from google import genai
from google.genai import types

def analyze_pyqs(raw_text: str, subject_name: str, api_key: str) -> dict:
    """
    Analyzes sample Previous Year Questions (PYQs) to create an Exam Calibration Profile
    capturing question styles, difficulty benchmarks, and Bloom's taxonomy breakdown.
    """
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    You are an educational assessment expert analyzing Previous Year Questions (PYQs) for {subject_name}.
    Analyze the questions below and generate a Calibration Profile in strict JSON format:
    
    {{
      "difficulty_benchmark": "Easy/Medium/Hard",
      "blooms_taxonomy_distribution": {{
        "recall_knowledge_pct": 30,
        "application_numerical_pct": 50,
        "analysis_synthesis_pct": 20
      }},
      "question_stem_style": "Concise scenario-based / direct conceptual / numerical word problems",
      "distractor_patterns": "Common student misconceptions, sign errors, definitions confused",
      "typical_question_types": ["MCQ", "Short Answer", "Numerical"]
    }}
    
    Raw PYQs Text:
    ---
    {raw_text[:8000]}
    ---
    
    Output strictly valid JSON matching the schema above.
    """
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2
        )
    )
    
    try:
        profile = json.loads(response.text)
        return profile
    except Exception as e:
        return {
            "difficulty_benchmark": "Medium",
            "blooms_taxonomy_distribution": {"recall_knowledge_pct": 40, "application_numerical_pct": 40, "analysis_synthesis_pct": 20},
            "question_stem_style": "Standard academic questions",
            "distractor_patterns": "Plausible misconceptions",
            "typical_question_types": ["MCQ", "Short Answer"]
        }
