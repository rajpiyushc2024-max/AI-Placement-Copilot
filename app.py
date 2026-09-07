import os
import streamlit as st

from parser import extract_text
from prompts import SYSTEM_PROMPT
from llm import analyze_cv
from report import create_report


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Placement Copilot",
    page_icon="🎯",
    layout="wide"
)


# ============================================================
# SIDEBAR CONFIGURATION
# ============================================================

with st.sidebar:
    env_key = os.getenv("GROQ_API_KEY", "")
    if not env_key and hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
        env_key = st.secrets["GROQ_API_KEY"]
    groq_api_key_input = st.text_input(
        "Groq API Key",
        value=env_key,
        type="password",
        help="Enter your Groq API key, set GROQ_API_KEY in .env, or add it to Streamlit secrets."
    )

    if groq_api_key_input:
        st.success("API Key detected ✅")
    else:
        st.warning("⚠️ No API Key found.")
        st.markdown("[Get free Groq API key](https://console.groq.com/keys)")

    st.divider()
    st.markdown("### ℹ️ About")
    st.markdown(
        "**AI Placement Copilot** evaluates candidate CVs against job descriptions "
        "using Groq's high-speed LPU inference engine."
    )


# ============================================================
# HEADER
# ============================================================

st.title("🎯 AI Placement Copilot")

st.write(
    "Upload your CV, provide a Job Description, and get "
    "an AI-powered analysis of your job alignment."
)

st.divider()


# ============================================================
# INPUT SECTION
# ============================================================

col1, col2 = st.columns(2)


# -----------------------------
# CV Upload
# -----------------------------

with col1:

    st.subheader("📄 Upload Your CV")

    cv_file = st.file_uploader(
        "Upload your CV",
        type=["pdf", "docx"],
        help="Supported formats: PDF and DOCX"
    )

    if cv_file:

        st.success(
            f"Uploaded: {cv_file.name}"
        )


# -----------------------------
# Job Description
# -----------------------------

with col2:

    st.subheader("💼 Job Description")

    jd_text = st.text_area(
        "Paste the Job Description",
        height=220,
        placeholder=(
            "Paste the complete Job Description here..."
        )
    )


st.divider()


# ============================================================
# ANALYZE BUTTON
# ============================================================

analyze_button = st.button(
    "🚀 Analyze My CV",
    type="primary",
    use_container_width=True
)


# ============================================================
# ANALYSIS
# ============================================================

if analyze_button:

    # -----------------------------
    # Validate CV
    # -----------------------------

    if cv_file is None:

        st.warning(
            "⚠️ Please upload your CV first."
        )

        st.stop()


    # -----------------------------
    # Validate JD
    # -----------------------------

    if not jd_text.strip():

        st.warning(
            "⚠️ Please paste the Job Description first."
        )

        st.stop()


    try:

        # -----------------------------
        # Validate API Key
        # -----------------------------

        active_api_key = groq_api_key_input.strip() if groq_api_key_input else (
            os.getenv("GROQ_API_KEY") or (st.secrets.get("GROQ_API_KEY") if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets else None)
        )

        if not active_api_key:

            st.warning(
                "⚠️ Groq API Key is missing. Please enter your API key in the sidebar or define GROQ_API_KEY in a .env file."
            )

            st.stop()


        # ====================================================
        # STEP 1 — EXTRACT CV TEXT
        # ====================================================

        with st.spinner(
            "📄 Reading your CV..."
        ):

            cv_text = extract_text(
                cv_file
            )


        if not cv_text.strip():

            st.error(
                "❌ Could not extract text from the CV."
            )

            st.stop()


        # ====================================================
        # STEP 2 — SEND TO QWEN
        # ====================================================

        with st.spinner(
            "🤖 Qwen is analyzing your CV against the Job Description..."
        ):

            analysis = analyze_cv(
                cv_text,
                jd_text,
                SYSTEM_PROMPT,
                api_key=active_api_key
            )


        # ====================================================
        # SUCCESS
        # ====================================================
        # ====================================================
        # SUCCESS
        # ====================================================

        st.success(
            "✅ CV analysis completed successfully!"
        )


        # ====================================================
        # PDF REPORT
        # ====================================================

        pdf_file = create_report(
            analysis,
            candidate_name="Candidate"
        )

        st.download_button(
            label="📥 Download Complete PDF Report",
            data=pdf_file,
            file_name="AI_Placement_Copilot_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

        st.divider()


        # ====================================================
        # OVERALL MATCH
        # ====================================================

        st.header(
            "🎯 CV–Job Match"
        )

        score = analysis.get(
            "overall_score",
            0
        )

        verdict = analysis.get(
            "verdict",
            "Not specified"
        )

        score_col, verdict_col = st.columns(2)

        with score_col:

            st.metric(
                "Overall Match Score",
                f"{score}%"
            )

        with verdict_col:

            st.metric(
                "Overall Verdict",
                verdict
            )

        st.divider()


        # ====================================================
        # SCORE BREAKDOWN
        # ====================================================

        st.subheader(
            "📊 Score Breakdown"
        )

        scores = analysis.get(
            "score_breakdown",
            {}
        )


        col1, col2, col3, col4, col5 = st.columns(5)


        with col1:

            st.metric(
                "Technical Skills",
                f"{scores.get('technical_skills', 0)}%"
            )


        with col2:

            st.metric(
                "Functional Skills",
                f"{scores.get('functional_skills', 0)}%"
            )


        with col3:

            st.metric(
                "Experience",
                f"{scores.get('experience', 0)}%"
            )


        with col4:

            st.metric(
                "Projects",
                f"{scores.get('projects', 0)}%"
            )


        with col5:

            st.metric(
                "Education",
                f"{scores.get('education', 0)}%"
            )


        st.divider()


        # ====================================================
        # STRONG MATCHES
        # ====================================================

        st.subheader(
            "🟢 Strong Matches"
        )

        strong_matches = analysis.get(
            "strong_matches",
            []
        )


        if isinstance(
            strong_matches,
            list
        ):

            if strong_matches:

                for item in strong_matches:

                    st.write(
                        f"• {item}"
                    )

            else:

                st.info(
                    "No strong matches identified."
                )

        else:

            st.write(
                strong_matches
            )


        # ====================================================
        # PARTIAL MATCHES
        # ====================================================

        st.subheader(
            "🟡 Partial Matches"
        )

        partial_matches = analysis.get(
            "partial_matches",
            []
        )


        if isinstance(
            partial_matches,
            list
        ):

            if partial_matches:

                for item in partial_matches:

                    st.write(
                        f"• {item}"
                    )

            else:

                st.info(
                    "No partial matches identified."
                )

        else:

            st.write(
                partial_matches
            )


        # ====================================================
        # SKILL GAPS
        # ====================================================

        st.subheader(
            "🔴 Skill Gaps"
        )

        skill_gaps = analysis.get(
            "skill_gaps",
            []
        )


        if isinstance(
            skill_gaps,
            list
        ):

            if skill_gaps:

                for item in skill_gaps:

                    st.write(
                        f"• {item}"
                    )

            else:

                st.success(
                    "No major skill gaps identified."
                )

        else:

            st.write(
                skill_gaps
            )


        st.divider()


        # ====================================================
        # BEST PROJECT
        # ====================================================

        st.subheader(
            "🏆 Best Project for This Job"
        )

        project = analysis.get(
            "best_project",
            {}
        )


        if isinstance(
            project,
            dict
        ):

            project_name = project.get(
                "name",
                "Not specified"
            )

            relevance = project.get(
                "relevance",
                0
            )

            reason = project.get(
                "reason",
                "Not specified"
            )

            skills = project.get(
                "skills_demonstrated",
                []
            )

            talking_points = project.get(
                "interview_talking_points",
                []
            )


            st.markdown(
                f"### {project_name}"
            )


            st.metric(
                "Project Relevance",
                f"{relevance}%"
            )


            st.write(
                f"**Why it matches:** {reason}"
            )


            st.write(
                "**Skills Demonstrated:**"
            )


            if isinstance(
                skills,
                list
            ):

                for skill in skills:

                    st.write(
                        f"• {skill}"
                    )

            else:

                st.write(
                    skills
                )


            st.write(
                "**Interview Talking Points:**"
            )


            if isinstance(
                talking_points,
                list
            ):

                for point in talking_points:

                    st.write(
                        f"• {point}"
                    )

            else:

                st.write(
                    talking_points
                )


        else:

            st.write(
                project
            )


        st.divider()


        # ====================================================
        # EXPERIENCE TO HIGHLIGHT
        # ====================================================

        st.subheader(
            "💼 Experience to Highlight"
        )

        experience = analysis.get(
            "experience_to_highlight",
            []
        )


        if isinstance(
            experience,
            list
        ):

            for item in experience:

                st.write(
                    f"• {item}"
                )

        else:

            st.write(
                experience
            )


        st.divider()


        # ====================================================
        # CV RECOMMENDATIONS
        # ====================================================

        st.subheader(
            "✍️ CV Recommendations"
        )

        recommendations = analysis.get(
            "cv_recommendations",
            []
        )


        if isinstance(
            recommendations,
            list
        ):

            for item in recommendations:

                st.write(
                    f"• {item}"
                )

        else:

            st.write(
                recommendations
            )


        st.divider()


        # ====================================================
        # LEARNING RECOMMENDATIONS
        # ====================================================

        st.subheader(
            "📚 Skills You Should Learn"
        )

        learning = analysis.get(
            "learning_recommendations",
            []
        )


        if isinstance(
            learning,
            list
        ):

            for item in learning:

                st.write(
                    f"• {item}"
                )

        else:

            st.write(
                learning
            )


        st.divider()


        # ====================================================
        # 7-DAY PREPARATION PLAN
        # ====================================================

        st.header(
            "📅 7-Day Preparation Plan"
        )

        seven_day_plan = analysis.get(
            "seven_day_plan",
            []
        )


        if isinstance(
            seven_day_plan,
            list
        ):

            for index, day in enumerate(
                seven_day_plan,
                start=1
            ):

                # --------------------------------------------
                # Normal dictionary format
                # --------------------------------------------

                if isinstance(
                    day,
                    dict
                ):

                    day_number = day.get(
                        "day",
                        index
                    )

                    focus = day.get(
                        "focus",
                        "Preparation"
                    )

                    tasks = day.get(
                        "tasks",
                        []
                    )


                    st.markdown(
                        f"### Day {day_number}: {focus}"
                    )


                    if isinstance(
                        tasks,
                        list
                    ):

                        for task in tasks:

                            st.write(
                                f"• {task}"
                            )

                    else:

                        st.write(
                            f"• {tasks}"
                        )


                # --------------------------------------------
                # String format
                # --------------------------------------------

                else:

                    st.markdown(
                        f"### Day {index}"
                    )

                    st.write(
                        f"• {day}"
                    )


        else:

            st.write(
                seven_day_plan
            )


        st.divider()


        # ====================================================
        # INTERVIEW QUESTIONS
        # ====================================================

        st.header(
            "🎤 Interview Questions"
        )

        questions = analysis.get(
            "interview_questions",
            {}
        )


        # ----------------------------------------------------
        # HR
        # ----------------------------------------------------

        with st.expander(
            "👤 HR Questions"
        ):

            hr_questions = questions.get(
                "hr",
                []
            ) if isinstance(
                questions,
                dict
            ) else []


            if isinstance(
                hr_questions,
                list
            ):

                for question in hr_questions:

                    st.write(
                        f"• {question}"
                    )

            else:

                st.write(
                    hr_questions
                )


        # ----------------------------------------------------
        # Technical
        # ----------------------------------------------------

        with st.expander(
            "💻 Technical Questions"
        ):

            technical_questions = questions.get(
                "technical",
                []
            ) if isinstance(
                questions,
                dict
            ) else []


            if isinstance(
                technical_questions,
                list
            ):

                for question in technical_questions:

                    st.write(
                        f"• {question}"
                    )

            else:

                st.write(
                    technical_questions
                )


        # ----------------------------------------------------
        # CV Based
        # ----------------------------------------------------

        with st.expander(
            "📄 CV-Based Questions"
        ):

            cv_questions = questions.get(
                "cv_based",
                []
            ) if isinstance(
                questions,
                dict
            ) else []


            if isinstance(
                cv_questions,
                list
            ):

                for question in cv_questions:

                    st.write(
                        f"• {question}"
                    )

            else:

                st.write(
                    cv_questions
                )


        # ----------------------------------------------------
        # Project Based
        # ----------------------------------------------------

        with st.expander(
            "🏆 Project Questions"
        ):

            project_questions = questions.get(
                "project_based",
                []
            ) if isinstance(
                questions,
                dict
            ) else []


            if isinstance(
                project_questions,
                list
            ):

                for question in project_questions:

                    st.write(
                        f"• {question}"
                    )

            else:

                st.write(
                    project_questions
                )


        # ----------------------------------------------------
        # Behavioral
        # ----------------------------------------------------

        with st.expander(
            "🧠 Behavioral Questions"
        ):

            behavioral_questions = questions.get(
                "behavioral",
                []
            ) if isinstance(
                questions,
                dict
            ) else []


            if isinstance(
                behavioral_questions,
                list
            ):

                for question in behavioral_questions:

                    st.write(
                        f"• {question}"
                    )

            else:

                st.write(
                    behavioral_questions
                )


        st.divider()


        # ====================================================
        # RAW DATA — OPTIONAL DEBUGGING
        # ====================================================

        with st.expander(
            "🔧 View AI Response"
        ):

            st.json(
                analysis
            )


    # ========================================================
    # ERROR HANDLING
    # ========================================================

    except Exception as e:

        st.error(
            f"❌ Something went wrong:\n\n{e}"
        )