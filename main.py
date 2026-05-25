import streamlit as st
import PyPDF2
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

st.set_page_config(
    page_title="AI Resume Scanner",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI Resume Scanner")

def ask_ai(prompt):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content

def extract_pdf(file):

    reader = PyPDF2.PdfReader(file)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text

    return text

left, right = st.columns([1, 1])

with left:

    st.subheader("Upload Resume")

    resume_file = st.file_uploader(
        "PDF Resume",
        type=["pdf"]
    )

    job_role = st.text_input(
        "Target Job Role",
        placeholder="e.g. Data Scientist"
    )

    job_desc = st.text_area(
        "Paste Job Description (Optional)",
        height=150
    )

    scan_btn = st.button(
        "Scan Resume",
        use_container_width=True
    )

with right:

    if scan_btn:

        if not resume_file:

            st.error("Please upload a PDF resume!")

        elif not job_role:

            st.error("Please enter target job role!")

        else:

            with st.spinner("Scanning resume..."):

                resume_text = extract_pdf(resume_file)

                prompt = f"""
                You are an ATS and HR expert.

                Analyze the following resume for the role: {job_role}

                Resume Text:
                {resume_text[:3000]}

                Job Description:
                {job_desc}

                Return ONLY valid JSON in this format:

                {{
                    "ats_score": 0,
                    "overall_rating": "",
                    "strengths": [],
                    "weaknesses": [],
                    "missing_keywords": [],
                    "improvement_tips": [],
                    "summary": ""
                }}
                """

                raw = ask_ai(prompt).strip()

                if "```json" in raw:

                    raw = raw.replace("```json", "")
                    raw = raw.replace("```", "")

                elif "```" in raw:

                    raw = raw.replace("```", "")

                try:

                    result = json.loads(raw)

                except Exception as e:

                    st.error("Invalid AI response")
                    st.code(raw)
                    st.stop()

                score = result["ats_score"]

                if score >= 75:
                    color = "green"

                elif score >= 50:
                    color = "orange"

                else:
                    color = "red"

                st.markdown(
                    f"""
                    <div style="
                        text-align:center;
                        padding:20px;
                        background:#1a1a2e;
                        border-radius:15px;
                        border:3px solid {color};
                    ">

                    <h1 style="
                        color:{color};
                        font-size:70px;
                        margin-bottom:0;
                    ">
                        {score}
                    </h1>

                    <p style="color:white;font-size:20px;">
                        ATS Score / 100
                    </p>

                    <p style="color:white;">
                        {result['overall_rating']}
                    </p>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.subheader("📌 Summary")
                st.info(result["summary"])

                st.subheader("✅ Strengths")

                for item in result["strengths"]:
                    st.write("•", item)

                st.subheader("❌ Weaknesses")

                for item in result["weaknesses"]:
                    st.write("•", item)

                st.subheader("🔑 Missing Keywords")

                for item in result["missing_keywords"]:
                    st.write("•", item)

                st.subheader("💡 Improvement Tips")

                for item in result["improvement_tips"]:
                    st.write("•", item)