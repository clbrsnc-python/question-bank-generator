import json
from google import genai
from google.genai import types

def generate_question_bank(
    num_questions: int,
    question_types: list,
    selected_chapters: list,
    syllabus_tree: dict,
    pyq_profile: dict,
    indexed_resources: dict,
    api_key: str
) -> list:
    """
    Generates a calibrated question bank bounded strictly by the syllabus and
    matching the PYQ difficulty and style profile.
    """
    client = genai.Client(api_key=api_key.strip())
    
    prompt = f"""
    You are an expert subject matter examiner. Generate a high-quality Question Bank of EXACTLY {num_questions} questions.
    
    CRITICAL CONSTRAINTS:
    1. SCOPE BOUNDARY: Every question MUST be strictly within these selected chapters and topics from the syllabus:
       {json.dumps(selected_chapters)}
    2. EXAM CALIBRATION (from Previous Year Questions):
       - Benchmark Difficulty: {pyq_profile.get('difficulty_benchmark', 'Medium')}
       - Stem Style: {pyq_profile.get('question_stem_style', 'Academic and conceptual')}
       - Distractor Strategy: {pyq_profile.get('distractor_patterns', 'Common student misconceptions')}
    3. QUESTION TYPES TO INCLUDE: {", ".join(question_types)}
    
    4. FACTUAL GROUND TRUTH (Learning Resources):
       {json.dumps(indexed_resources)[:4000]}
    
    OUTPUT FORMAT:
    Return a strictly valid JSON array of question objects matching this schema:
    [
      {{
        "question_id": 1,
        "chapter": "Chapter Name",
        "topic": "Specific Topic",
        "question_type": "MCQ or Short Answer",
        "difficulty": "Easy/Medium/Hard",
        "question": "The question text here...",
        "options": {{
          "A": "Option A text",
          "B": "Option B text",
          "C": "Option C text",
          "D": "Option D text"
        }},
        "correct_answer": "Option letter (e.g. B) or short model answer",
        "explanation": "Detailed step-by-step academic explanation.",
        "syllabus_ref": "Specific syllabus topic reference"
      }}
    ]
    
    Ensure options are included for MCQs. For Short Answer questions, options can be null.
    Generate EXACTLY {num_questions} questions now.
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
                    temperature=0.3
                )
            )
            questions = json.loads(response.text)
            return questions
        except Exception as e:
            last_error = e
            continue
            
    raise RuntimeError(f"Failed to generate questions via Gemini API: {str(last_error)}")
