# AI Question Bank Pool Generator for Subject Teachers

An AI-powered application built with Streamlit, Python, and Google Gemini to help subject teachers generate high-quality question banks bounded strictly by syllabus scope and calibrated against Previous Year Questions (PYQs).

## Key Features

1. Syllabus Boundary Engine: Parses uploaded PDF/TXT syllabus files into a structured topic hierarchy.
2. PYQ Style Calibration: Analyzes sample past exam papers to extract difficulty benchmarks and Bloom's taxonomy distribution.
3. Resource Grounding: Indexes textbooks and learning resources so every question and answer is grounded in factual truth.
4. Calibrated Generation: Generates MCQs, Short Answers, and Numerical problems with step-by-step explanations.
5. Multi-Format Export: One-click export to CSV and Printable PDF test paper with answer keys.

## Project Structure

```
question-bank-generator/
├── app.py                     # Main Streamlit Multi-step Wizard App
├── requirements.txt           # Project Dependencies
├── .env.example               # Environment Variables Template
└── utils/
    ├── __init__.py
    ├── syllabus_parser.py     # Extracts & parses syllabus into boundary tree
    ├── pyq_analyzer.py        # Extracts difficulty & pattern profile from PYQs
    ├── resource_indexer.py    # Maps learning resources to syllabus topics
    ├── generator.py           # Synthesizes calibrated questions
    └── exporter.py            # Converts question banks to CSV and PDF
```

## Setup & Deployment

1. Initialize repository and install requirements:
   `pip install -r requirements.txt`

2. Configure environment variables in `.env`:
   `GEMINI_API_KEY=your_key_here`

3. Run the Streamlit Application:
   `streamlit run app.py`

4. Deploy to cloud hosting by pushing the repository to GitHub and connecting to Streamlit Cloud.
