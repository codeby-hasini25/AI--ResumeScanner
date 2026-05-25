import streamlit as st
import PyPDF2
import json
from openai import OpenAI

# ==========================================
# PAGE SETTINGS
# ==========================================
st.set_page_config(
    page_title="AI Resume ATS Scanner",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI Resume ATS Scanner")

# ==========================================
# OPENAI CLIENT
# ==========================================
from openai import OpenAI

client = OpenAI(
    api_key=
)

# ==========================================
# AI FUNCTION
# ==========================================
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


# ==========================================
# PDF TEXT EXTRACTION
# ==========================================
def extract_pdf(file):

    reader = PyPDF2.PdfReader(file)

    all_text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            all_text += page_text

    return all_text


# ==========================================
# TWO COLUMN LAYOUT
# ==========================================
left, right = st.columns([1, 1])

# ==========================================
# LEFT COLUMN
# ==========================================
with left:

    st.subheader("Upload Resume")

    # Upload PDF
    resume_file = st.file_uploader(
        "PDF Resume",
        type=["pdf"]
    )

    # Job role
    job_role = st.text_input(
        "Target Job Role",
        placeholder="e.g. Data Scientist"
    )

    # Job description
    job_desc = st.text_area(
        "Paste Job Description (Optional)",
        height=150
    )

    # Scan button
    scan_btn = st.button(
        "Scan Resume",
        use_container_width=True
    )


# ==========================================
# RIGHT COLUMN
# ==========================================
with right:

    if scan_btn:

        # Validation
        if not resume_file:
            st.error("Please upload a PDF resume!")

        elif not job_role:
            st.error("Please enter target job role!")

        else:

            with st.spinner("Scanning Resume..."):

                # ==================================
                # EXTRACT TEXT
                # ==================================
                resume_text = extract_pdf(resume_file)

                # ==================================
                # BUILD AI PROMPT
                # ==================================
                prompt = f"""
                You are an ATS and HR expert.

                Analyze this resume for the role:
                {job_role}

                Job Description:
                {job_desc}

                Resume Text:
                {resume_text[:3000]}

                Return ONLY valid JSON with:

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

                # ==================================
                # CALL AI
                # ==================================
                raw = ask_ai(prompt).strip()

                # ==================================
                # CLEAN RESPONSE
                # ==================================
                if "```" in raw:

                    raw = raw.split("```")[1]

                    if raw.startswith("json"):
                        raw = raw[4:]

                # ==================================
                # PARSE JSON
                # ==================================
                result = json.loads(raw)

                # ==================================
                # ATS SCORE
                # ==================================
                score = result["ats_score"]

                # Score color
                if score >= 75:
                    color = "green"

                elif score >= 50:
                    color = "orange"

                else:
                    color = "red"

                # ==================================
                # SCORE CARD
                # ==================================
                st.markdown(
                    f"""
                    <div style="
                        text-align:center;
                        padding:25px;
                        background:#1a1a2e;
                        border-radius:15px;
                        border:3px solid {color};
                        margin-bottom:20px;
                    ">

                        <h1 style="
                            color:{color};
                            font-size:70px;
                            margin:0;
                        ">
                            {score}
                        </h1>

                        <h3 style="color:white;">
                            ATS Score / 100
                        </h3>

                        <p style="
                            color:white;
                            font-size:18px;
                        ">
                            {result["overall_rating"]}
                        </p>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # ==================================
                # SUMMARY
                # ==================================
                st.info(result["summary"])

                # ==================================
                # RESULT COLUMNS
                # ==================================
                c1, c2 = st.columns(2)

                # LEFT RESULT COLUMN
                with c1:

                    st.success("Strengths")

                    for s in result["strengths"]:
                        st.write("• " + s)

                    st.error("Weaknesses")

                    for w in result["weaknesses"]:
                        st.write("• " + w)

                # RIGHT RESULT COLUMN
                with c2:

                    st.warning("Missing Keywords")

                    for k in result["missing_keywords"]:
                        st.write("• " + k)

                    st.info("Improvement Tips")

                    for t in result["improvement_tips"]:
                        st.write("• " + t)