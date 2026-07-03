import streamlit as st
import pickle
import pdfplumber
import re

st.set_page_config(

    page_title="AI Resume Analyzer",

    page_icon="🤖",

    layout="wide"

)

from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

def calculate_score(text):

    score = 0
    text = text.lower()


    # Contact Information Score (Max 10)
    if re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text):
        score += 5


    if re.search(r"\b\d{10}\b", text):
        score += 5


        # Professional Links Score (Max 5)

        links_score = 0

        if "linkedin.com" in text:
            links_score += 2


        if "github.com" in text:
            links_score += 2


        if "portfolio" in text or "portfolio:" in text or "behance.net" in text:
            links_score += 1


        score += links_score

    education_keywords = [
        "education",
        "qualification",
        "academic",
        "scholastic"
    ]

    skills_keywords = [
        "skills",
        "technical skills",
        "core competencies",
        "competencies",
        "technical expertise"
    ]

    project_keywords = [
        "project",
        "projects",
        "academic project",
        "personal project"
    ]

    experience_keywords = [
        "experience",
        "work experience",
        "employment",
        "career",
        "professional experience"
    ]

    certification_keywords = [
        "certification",
        "certifications",
        "certificate",
        "licenses",
        "training"
    ]

    if any(keyword in text for keyword in education_keywords):

        if any(degree in text for degree in [
            "phd",
            "doctorate",
            "master",
            "m.tech",
            "mba"
        ]):
            score += 15


        elif any(degree in text for degree in [
            "bachelor",
            "b.tech",
            "bca",
            "b.sc",
            "ba",
            "bcom"
        ]):
            score += 12


        elif any(degree in text for degree in [
            "diploma",
            "12th",
            "higher secondary"
        ]):
            score += 8


        else:
            score += 5


    found_skills = extract_skills(text)

    if len(found_skills) >= 12:
        score += 30


    elif len(found_skills) >= 8:
        score += 22


    elif len(found_skills) >= 5:
        score += 15


    elif len(found_skills) >= 2:
        score += 8


    project_count = text.count("project")

    if project_count >= 4:
        score += 25
    elif project_count == 3:
        score += 20
    elif project_count == 2:
        score += 15
    elif project_count == 1:
        score += 8


    if any(keyword in text for keyword in experience_keywords):

        if any(keyword in text for keyword in experience_keywords):

            if any(word in text for word in [
                "5 years", "6 years", "7 years", "8 years", "9 years", "10 years"
            ]):
                score += 25

            elif any(word in text for word in [
                "2 years", "3 years", "4 years"
            ]):
                score += 18

            elif any(word in text for word in [
                "intern", "internship", "6 months", "3 months", "1 month", "fresher"
            ]):
                score += 12

            else:
                score += 5


    cert_count = (
            text.count("certification") +
            text.count("certifications") +
            text.count("certificate")
    )

    if cert_count >= 3:
        score += 10


    elif cert_count >= 1:
        score += 5


    return score
def get_suggestions(text):

    suggestions = []

    text = text.lower()

    if not any(k in text for k in ["education", "qualification", "academic", "scholastic"]):
        suggestions.append("Add education details.")

    if not any(k in text for k in ["skills", "technical skills", "competencies"]):
        suggestions.append("Add a dedicated technical skills section.")

    if not any(k in text for k in ["project", "projects"]):

        if any(k in text for k in ["experience", "work experience", "employment"]):
            suggestions.append("Add major projects or key achievements from your work experience.")

        else:
            suggestions.append("Add projects to showcase practical experience.")

    if not any(k in text for k in ["experience", "work experience", "employment"]):
        suggestions.append("Add work experience.")

    if not any(k in text for k in ["certification", "certifications", "certificate"]):
        suggestions.append("Add certifications if you have any.")

    if not suggestions:
        suggestions.append("Excellent resume! No major improvements needed.")

    return suggestions


def extract_skills(text):
    skills_list = [

        # Programming
        "python",
        "java",
        "c++",
        "c#",
        "sql",
        "html",
        "css",
        "javascript",
        "php",
        # Soft Skills
        "leadership",
        "communication",
        "problem solving",
        "troubleshooting",
        "time management",
        "teamwork",
        "technical supervision",
        "mentoring",

        # Engineering
        "preventive maintenance",
        "corrective maintenance",
        "electrical safety",
        "maintenance planning",
        "technical reports",

        # General
        "microsoft excel",
        "documentation",

        # Frameworks
        "django",
        "flask",
        "react",
        "angular",
        "node.js",

        # AI / Data Science
        "machine learning",
        "deep learning",
        "pandas",
        "numpy",
        "tensorflow",
        "keras",

        # Tools
        "git",
        "linux",
        "docker",

        # Electrical Engineering
        "electrical maintenance",
        "power systems",
        "power system",
        "substation",
        "transformer",
        "transformers",
        "relay",
        "relays",
        "switchgear",
        "fault analysis",
        "power electronics",
        "electrical engineering",
        "circuit breaker",
        "circuit breakers",
        "safety compliance",

        # Mechanical
        "autocad",
        "solidworks",
        "cnc",
        "hvac",

        # Civil
        "staad pro",
        "quantity surveying",
        "site supervision",

        # HR
        "recruitment",
        "payroll",

        # Finance
        "tally",
        "gst",
        "sap",
    ]

    found_skills = []

    text = text.lower()

    for skill in skills_list:
        if skill in text:

            if skill == "microsoft excel":
                found_skills.append("Microsoft Excel")
            else:
                found_skills.append(skill.title())

    cleaned_skills = []

    for skill in found_skills:
        singular = skill.rstrip("sS")

        if singular not in [x.rstrip("sS") for x in cleaned_skills]:
            cleaned_skills.append(skill)

    return cleaned_skills
def create_pdf_report(prediction, skills, score, suggestions):

    buffer = BytesIO()

    pdf = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("<b>AI Resume Analyzer</b>", styles["Title"]))
    story.append(Paragraph("<br/>", styles["Normal"]))

    story.append(Paragraph(f"<b>Predicted Category:</b> {prediction}", styles["Normal"]))
    story.append(Paragraph(f"<b>Resume Score:</b> {score}/100", styles["Normal"]))

    if score >= 90:
        rating = "⭐⭐⭐⭐⭐ Excellent"

    elif score >= 75:
        rating = "⭐⭐⭐⭐ Good"

    elif score >= 60:
        rating = "⭐⭐⭐ Average"

    elif score >= 40:
        rating = "⭐⭐ Needs Improvement"

    else:
        rating = "⭐ Poor Resume"

    story.append(Paragraph(f"<b>Resume Rating:</b> {rating}", styles["Normal"]))
    story.append(Paragraph("<br/>", styles["Normal"]))

    story.append(Paragraph("<b>Skills Found:</b>", styles["Heading2"]))

    for skill in skills:
        story.append(Paragraph(f"• {skill}", styles["Normal"]))

    story.append(Paragraph("<br/>", styles["Normal"]))
    story.append(Paragraph("<b>Suggestions:</b>", styles["Heading2"]))

    for suggestion in suggestions:
        story.append(Paragraph(f"• {suggestion}", styles["Normal"]))

    pdf.build(story)

    buffer.seek(0)
    return buffer

st.markdown("""
<style>

.stApp {
    background-color:#050505;
}

.block-container {

    padding-top:2rem;

    padding-left:3rem;

    padding-right:3rem;

}


.header {

    background:

    radial-gradient(circle at top,#3a3000,#050505 70%);


    padding:35px;


    border-radius:20px;


    text-align:center;


    color:white;


    border:2px solid #FFD700;


    box-shadow:

    0 0 15px #FFD700,

    inset 0 0 30px rgba(255,215,0,0.25);

}



.header h1 {


    font-size:55px;


    font-weight:900;


    letter-spacing:3px;


    color:#FFD700;


    text-shadow:


    0 0 10px #FFD700,

    0 0 25px #FFD700;


}



.header h4 {


    font-size:25px;


    color:white;


}



.header p {


    font-size:18px;


    color:#ddd;


}

</style>


<div class="header">

<div class="header-content">

<div class="robot">
🤖
</div>

<div>

<h1>AI RESUME ANALYZER</h1>

<h4>AI-Powered Resume Screening System</h4>

<p>
Analyze resumes intelligently using Artificial Intelligence.
</p>

</div>

</div>

</div>

""", unsafe_allow_html=True)

model = pickle.load(
    open("resume_model.pkl", "rb")
)

vectorizer = pickle.load(
    open("tfidf_vectorizer.pkl", "rb")
)

st.markdown("""

<style>

[data-testid="stFileUploader"] {

    background:#0b0b0b;

    padding:20px;

    border-radius:18px;

    border:2px solid #39ff14;

    box-shadow:0 0 12px #39ff14;

}


[data-testid="stFileUploader"] label {

    color:white;

    font-size:18px;

    font-weight:bold;

}


</style>

""", unsafe_allow_html=True)



uploaded_file = st.file_uploader(

    "📄 Upload Resume PDF",

    type=["pdf"]

)

if uploaded_file is not None:

    resume_text = ""

    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()

            if text:
                resume_text += text + "\n"

    st.subheader("Extracted Resume Text")
    st.text_area("", resume_text, height=200)

    if st.button("Analyze Resume"):

        resume_vector = vectorizer.transform([resume_text])

        prediction = model.predict(resume_vector)

        skills = extract_skills(resume_text)
        score = calculate_score(resume_text)

        suggestions= get_suggestions(resume_text)

        st.success("Analysis Complete!")

        st.markdown("""
        <style>

        .card {

            background:#0b0b0b;

            padding:22px;

            border-radius:18px;

            margin-bottom:20px;

            border:2px solid #39ff14;

            box-shadow:
            0 0 10px #39ff14,
            inset 0 0 10px rgba(57,255,20,0.15);

            color:white;

        }


        .title {

            font-size:18px;

            font-weight:bold;

            color:white;

        }


        .value {

            font-size:35px;

            font-weight:bold;

            color:white;

        }


        p {

    color:white;

}


.skill {

    display:inline-block;

    padding:7px 14px;

    margin:5px;

    border-radius:20px;

    border:1px solid #39ff14;

    color:white;

    background:#111;

    box-shadow:0 0 8px #39ff14;

}


.score-card {

    background:#0b0b0b;

    padding:25px;

    border-radius:18px;

    border:2px solid #39ff14;

    box-shadow:0 0 15px #39ff14;

    text-align:center;

}


.score-circle {

    width:140px;

    height:140px;

    border-radius:50%;

    margin:auto;

    display:flex;

    align-items:center;

    justify-content:center;

    font-size:40px;

    font-weight:bold;

    color:white;

    border:8px solid #39ff14;

    box-shadow:0 0 20px #39ff14;

}


.score-title {

    margin-top:15px;

    font-size:22px;

    font-weight:bold;

    color:white;

}


</style>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:

            st.markdown(f"""
            <div class="card">

            <div class="title">📂 Predicted Category</div>

            <div class="value">{prediction[0]}</div>

            </div>
            """, unsafe_allow_html=True)

            skills_html = ""

            for skill in skills:
                skills_html += f'<span class="skill">{skill}</span>'
            if not skills_html:
                skills_html = "No skills detected"

            st.markdown(f"""

            <div class="card">

            <div class="title">
            🛠 Skills Found ({len(skills)})
            </div>

            <br>

            {skills_html}

            </div>

            """, unsafe_allow_html=True)

        with col2:

            if score >= 90:
                rating = "⭐⭐⭐⭐⭐ Excellent Resume"

            elif score >= 75:
                rating = "⭐⭐⭐⭐ Good Resume"

            elif score >= 60:
                rating = "⭐⭐⭐ Average Resume"

            elif score >= 40:
                rating = "⭐⭐ Needs Improvement"

            else:
                rating = "⭐ Poor Resume"

            st.markdown(f"""

            <div class="score-card">

            <div class="score-circle">

            {score}%

            </div>

            <div class="score-title">

            📊 Resume Score

            </div>

            <br>

            <div style="font-size:22px;font-weight:bold;color:#FFD700;">

            {rating}

            </div>

            </div>

            """, unsafe_allow_html=True)

            suggestion_text = "<br>".join(
                ["• " + s for s in suggestions]
            )

            st.markdown(f"""
            <div class="card">

            <div class="title">💡 Suggestions</div>

            <p>{suggestion_text}</p>

            </div>
            """, unsafe_allow_html=True)
            report = f"""
            AI Resume Analyzer Report
            =========================

            Predicted Category:
            {prediction[0]}

            Skills Found:
            {', '.join(skills)}

            Resume Score:
            {score}/100

            Suggestions:
            """

            for suggestion in suggestions:
                report += f"\n- {suggestion}"

            pdf_report = create_pdf_report(
                prediction[0],
                skills,
                score,
                suggestions
            )

            st.markdown("""
            <style>

            .stDownloadButton button {

                width:100%;

                background:#111;

                color:white;

                border:2px solid #39ff14;

                border-radius:15px;

                padding:12px;

                font-size:18px;

                font-weight:bold;

                box-shadow:0 0 12px #39ff14;

            }

            .stDownloadButton button:hover {

                background:#39ff14;

                color:black;

            }

            </style>
            """, unsafe_allow_html=True)

            st.download_button(

                label="📄 Download PDF Report",

                data=pdf_report,

                file_name="AI_Resume_Analysis_Report.pdf",

                mime="application/pdf"

            )