import streamlit as st
import json
import os
from utils.syllabus_parser import extract_text_from_file, parse_syllabus
from utils.pyq_analyzer import analyze_pyqs
from utils.resource_indexer import index_learning_resources
from utils.generator import generate_question_bank
from utils.exporter import export_to_csv, export_to_pdf

st.set_page_config(
    page_title="Teacher Question Bank Generator",
    page_icon="🎓",
    layout="wide"
)

# Initialize Session State
if "stage" not in st.session_state:
    st.session_state.stage = 1
if "syllabus_tree" not in st.session_state:
    st.session_state.syllabus_tree = None
if "pyq_profile" not in st.session_state:
    st.session_state.pyq_profile = None
if "indexed_resources" not in st.session_state:
    st.session_state.indexed_resources = None
if "generated_questions" not in st.session_state:
    st.session_state.generated_questions = []

# Helper to retrieve API key safely from Streamlit Secrets or Environment
def get_default_api_key():
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    return os.environ.get("GEMINI_API_KEY", "")

default_key = get_default_api_key()

# Sidebar API Key configuration
st.sidebar.title("⚙️ Setup & Credentials")
api_key = st.sidebar.text_input("Gemini API Key", type="password", value=default_key).strip()

st.sidebar.markdown("""
---
### 🔑 How teachers can get a Free API Key:
1. Go to **[aistudio.google.com](https://aistudio.google.com)**
2. Sign in with any Google Account.
3. Click **Get API key** ➔ **Create API key**.
4. Copy your key and paste it above!
""")

if not api_key:
    st.sidebar.warning("⚠️ Please enter a valid Gemini API Key in the sidebar or Streamlit Secrets to proceed.")

st.title("🎓 AI Question Bank Generator for Subject Teachers")
st.caption("Generate syllabus-bounded, PYQ-calibrated question pools without hallucinations.")

# Progress bar / Steps UI
steps = ["1. Subject & Syllabus", "2. PYQ Calibration", "3. Resources Grounding", "4. Generation & Export"]
st.progress((st.session_state.stage) / 4)

# ----------------------------------------------------
# STAGE 1: Subject Selection & Syllabus Upload
# ----------------------------------------------------
if st.session_state.stage == 1:
    st.header("Step 1: Select Subject & Upload Syllabus Boundary")
    subject_name = st.text_input("Subject Name (e.g. Grade 10 Physics, High School Chemistry)", "Grade 10 Physics")
    syllabus_file = st.file_uploader("Upload Syllabus (PDF or TXT)", type=["pdf", "txt"])
    
    if st.button("Process Syllabus ➡️", disabled=not (syllabus_file and api_key)):
        with st.spinner("Extracting & parsing syllabus hierarchy..."):
            try:
                raw_syllabus = extract_text_from_file(syllabus_file, syllabus_file.name)
                tree = parse_syllabus(raw_syllabus, subject_name, api_key)
                if "error" in tree and len(tree.get("chapters", [])) <= 1:
                    st.warning(f"Note during syllabus parsing: {tree['error']}")
                st.session_state.syllabus_tree = tree
                st.session_state.subject_name = subject_name
                st.session_state.stage = 2
                st.rerun()
            except Exception as e:
                st.error(f"❌ Gemini API Error during processing: {str(e)}")
                st.info("💡 Tip: Verify your Gemini API key in the sidebar or create a new key at aistudio.google.com")

# ----------------------------------------------------
# STAGE 2: PYQ Calibration
# ----------------------------------------------------
elif st.session_state.stage == 2:
    st.header("Step 2: Upload Sample Previous Year Questions (PYQs)")
    st.info("Upload sample exam papers/PYQs so the system learns your target difficulty rating and style.")
    
    pyq_file = st.file_uploader("Upload PYQs (PDF or TXT)", type=["pdf", "txt"])
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Analyze PYQs ➡️", disabled=not (pyq_file and api_key)):
            with st.spinner("Analyzing PYQ exam pattern & Bloom's taxonomy distribution..."):
                try:
                    raw_pyq = extract_text_from_file(pyq_file, pyq_file.name)
                    profile = analyze_pyqs(raw_pyq, st.session_state.subject_name, api_key)
                    st.session_state.pyq_profile = profile
                    st.session_state.stage = 3
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Gemini API Error during PYQ analysis: {str(e)}")
    with col2:
        if st.button("Skip PYQs (Use Default Calibration) ➡️"):
            st.session_state.pyq_profile = {
                "difficulty_benchmark": "Medium",
                "question_stem_style": "Standard academic questions",
                "distractor_patterns": "Standard conceptual misconceptions"
            }
            st.session_state.stage = 3
            st.rerun()

# ----------------------------------------------------
# STAGE 3: Learning Resource Ingestion
# ----------------------------------------------------
elif st.session_state.stage == 3:
    st.header("Step 3: Grounding Resources (Textbooks / Notes / Links)")
    st.write("Provide textbooks, reference notes, or text materials as the factual source.")
    
    resource_file = st.file_uploader("Upload Learning Resource File (PDF or TXT)", type=["pdf", "txt"])
    resource_text_input = st.text_area("Or paste web article/notes text directly:", height=150)
    
    if st.button("Map Resources to Syllabus ➡️", disabled=not (api_key)):
        with st.spinner("Chunking resources & filtering out-of-syllabus content..."):
            try:
                combined_text = ""
                if resource_file:
                    combined_text += extract_text_from_file(resource_file, resource_file.name) + "\n"
                if resource_text_input:
                    combined_text += resource_text_input
                    
                indexed = index_learning_resources(combined_text, st.session_state.syllabus_tree, api_key)
                st.session_state.indexed_resources = indexed
                st.session_state.stage = 4
                st.rerun()
            except Exception as e:
                st.error(f"❌ Gemini API Error during resource indexing: {str(e)}")

# ----------------------------------------------------
# STAGE 4: Question Generation & Export
# ----------------------------------------------------
elif st.session_state.stage == 4:
    st.header("Step 4: Generate Calibrated Question Bank")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Generation Settings")
        num_q = st.number_input("Number of Questions to Generate", min_value=1, max_value=50, value=10)
        q_types = st.multiselect("Question Types", ["MCQ", "Short Answer", "Numerical"], default=["MCQ"])
        
        chapters = [ch.get("chapter_name") for ch in st.session_state.syllabus_tree.get("chapters", [])]
        selected_ch = st.multiselect("Target Chapters", chapters, default=chapters)
        
        if st.button("🔥 Generate Question Bank", disabled=not (selected_ch and api_key)):
            with st.spinner(f"Generating {num_q} questions bounded strictly by selected syllabus topics..."):
                try:
                    questions = generate_question_bank(
                        num_questions=num_q,
                        question_types=q_types,
                        selected_chapters=selected_ch,
                        syllabus_tree=st.session_state.syllabus_tree,
                        pyq_profile=st.session_state.pyq_profile or {},
                        indexed_resources=st.session_state.indexed_resources or {},
                        api_key=api_key
                    )
                    st.session_state.generated_questions = questions
                    st.success(f"Generated {len(questions)} questions successfully!")
                except Exception as e:
                    st.error(f"❌ Gemini API Error during question generation: {str(e)}")
    
    with col2:
        st.subheader("Preview & Export Question Pool")
        if st.session_state.generated_questions:
            questions = st.session_state.generated_questions
            st.json(questions, expanded=False)
            
            # Export Buttons
            csv_data = export_to_csv(questions)
            pdf_data = export_to_pdf(questions, st.session_state.subject_name)
            
            exp_col1, exp_col2 = st.columns(2)
            with exp_col1:
                st.download_button(
                    label="📥 Download CSV Question Bank",
                    data=csv_data,
                    file_name="question_bank.csv",
                    mime="text/csv"
                )
            with exp_col2:
                st.download_button(
                    label="📄 Download Printable PDF Test Paper",
                    data=bytes(pdf_data),
                    file_name="question_bank.pdf",
                    mime="application/pdf"
                )
    
    st.divider()
    if st.button("🔄 Start New Question Bank Project"):
        st.session_state.stage = 1
        st.session_state.generated_questions = []
        st.rerun()
