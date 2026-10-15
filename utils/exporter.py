import pandas as pd
from fpdf import FPDF
import io

def export_to_csv(questions: list) -> str:
    """Converts question bank list to CSV string for download."""
    flattened = []
    for q in questions:
        opts = q.get("options") or {}
        row = {
            "ID": q.get("question_id"),
            "Chapter": q.get("chapter"),
            "Topic": q.get("topic"),
            "Type": q.get("question_type"),
            "Difficulty": q.get("difficulty"),
            "Question": q.get("question"),
            "Option A": opts.get("A", ""),
            "Option B": opts.get("B", ""),
            "Option C": opts.get("C", ""),
            "Option D": opts.get("D", ""),
            "Correct Answer": q.get("correct_answer"),
            "Explanation": q.get("explanation")
        }
        flattened.append(row)
    
    df = pd.DataFrame(flattened)
    return df.to_csv(index=False)


def export_to_pdf(questions: list, subject_name: str) -> bytes:
    """Generates a clean printable PDF test paper and answer key."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Title Header
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"Question Bank Pool - {subject_name}", ln=True, align="C")
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 8, f"Total Questions: {len(questions)} | Bounded by Syllabus Scope", ln=True, align="C")
    pdf.ln(5)
    
    # Render Questions
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "SECTION A: QUESTION PAPER", ln=True)
    pdf.set_font("Helvetica", "", 10)
    
    for i, q in enumerate(questions, 1):
        q_text = f"Q{i}. [{q.get('difficulty', 'Medium')} | {q.get('chapter', '')}] {q.get('question')}"
        pdf.multi_cell(0, 6, q_text)
        
        opts = q.get("options")
        if opts and isinstance(opts, dict):
            for letter in ["A", "B", "C", "D"]:
                if letter in opts and opts[letter]:
                    pdf.multi_cell(0, 5, f"   ({letter}) {opts[letter]}")
        pdf.ln(3)
    
    # Page Break for Answer Key & Explanations
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "SECTION B: ANSWER KEY & EXPLANATIONS", ln=True)
    pdf.set_font("Helvetica", "", 10)
    
    for i, q in enumerate(questions, 1):
        ans_text = f"Q{i} Answer: {q.get('correct_answer')}"
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, ans_text, ln=True)
        
        pdf.set_font("Helvetica", "", 10)
        exp_text = f"Explanation: {q.get('explanation')}\nRef: {q.get('syllabus_ref', 'N/A')}"
        pdf.multi_cell(0, 5, exp_text)
        pdf.ln(3)
        
    return pdf.output()
