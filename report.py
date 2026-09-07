from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)


def safe_text(value):
    """Convert any value into text suitable for a PDF."""
    if value is None:
        return ""

    if isinstance(value, list):
        return ", ".join(str(item) for item in value)

    if isinstance(value, dict):
        return ", ".join(
            f"{key}: {value}"
            for key, value in value.items()
        )

    return str(value)


def create_report(analysis, candidate_name="Candidate"):
    """
    Create a PDF report from the AI analysis.

    Returns:
        BytesIO: PDF file in memory.
    """

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleCustom",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=22,
        leading=26,
        spaceAfter=10,
    )

    subtitle_style = ParagraphStyle(
        "SubtitleCustom",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=11,
        leading=15,
        spaceAfter=20,
    )

    heading_style = ParagraphStyle(
        "HeadingCustom",
        parent=styles["Heading2"],
        fontSize=15,
        leading=19,
        spaceBefore=12,
        spaceAfter=8,
    )

    body_style = ParagraphStyle(
        "BodyCustom",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=14,
        spaceAfter=5,
    )

    small_style = ParagraphStyle(
        "SmallCustom",
        parent=styles["BodyText"],
        fontSize=8.5,
        leading=12,
    )

    story = []

    # ========================================================
    # TITLE
    # ========================================================

    story.append(
        Paragraph(
            "AI Placement Copilot",
            title_style
        )
    )

    story.append(
        Paragraph(
            "CV–Job Description Alignment Report",
            subtitle_style
        )
    )

    story.append(
        Paragraph(
            f"<b>Candidate:</b> {safe_text(candidate_name)}",
            body_style
        )
    )

    story.append(Spacer(1, 8))

    # ========================================================
    # OVERALL SCORE
    # ========================================================

    score = analysis.get(
        "overall_score",
        0
    )

    verdict = analysis.get(
        "verdict",
        "Not specified"
    )

    story.append(
        Paragraph(
            "Overall Match",
            heading_style
        )
    )

    score_table = Table(
        [
            [
                Paragraph(
                    f"<b>{safe_text(score)}%</b>",
                    ParagraphStyle(
                        "Score",
                        parent=body_style,
                        fontSize=22,
                        alignment=TA_CENTER,
                    )
                ),
                Paragraph(
                    f"<b>{safe_text(verdict)}</b>",
                    ParagraphStyle(
                        "Verdict",
                        parent=body_style,
                        fontSize=13,
                        alignment=TA_CENTER,
                    )
                ),
            ]
        ],
        colWidths=[
            70 * mm,
            90 * mm,
        ],
    )

    score_table.setStyle(
        TableStyle(
            [
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    12,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    12,
                ),
            ]
        )
    )

    story.append(score_table)

    # ========================================================
    # SCORE BREAKDOWN
    # ========================================================

    story.append(
        Paragraph(
            "Score Breakdown",
            heading_style
        )
    )

    scores = analysis.get(
        "score_breakdown",
        {}
    )

    score_data = [
        ["Category", "Score"],
        [
            "Technical Skills",
            f"{scores.get('technical_skills', 0)}%"
        ],
        [
            "Functional Skills",
            f"{scores.get('functional_skills', 0)}%"
        ],
        [
            "Experience",
            f"{scores.get('experience', 0)}%"
        ],
        [
            "Projects",
            f"{scores.get('projects', 0)}%"
        ],
        [
            "Education",
            f"{scores.get('education', 0)}%"
        ],
    ]

    score_breakdown_table = Table(
        score_data,
        colWidths=[
            110 * mm,
            50 * mm,
        ],
    )

    score_breakdown_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "ALIGN",
                    (1, 1),
                    (1, -1),
                    "CENTER",
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.append(score_breakdown_table)

    # ========================================================
    # LIST SECTION HELPER
    # ========================================================

    def add_list_section(title, items):

        story.append(
            Paragraph(
                title,
                heading_style
            )
        )

        if not items:

            story.append(
                Paragraph(
                    "No information available.",
                    body_style
                )
            )

            return

        if not isinstance(items, list):

            items = [items]

        for item in items:

            story.append(
                Paragraph(
                    f"• {safe_text(item)}",
                    body_style
                )
            )

    # ========================================================
    # SKILL MATCH
    # ========================================================

    add_list_section(
        "Strong Matches",
        analysis.get(
            "strong_matches",
            []
        )
    )

    add_list_section(
        "Partial Matches",
        analysis.get(
            "partial_matches",
            []
        )
    )

    add_list_section(
        "Skill Gaps",
        analysis.get(
            "skill_gaps",
            []
        )
    )

    # ========================================================
    # BEST PROJECT
    # ========================================================

    project = analysis.get(
        "best_project",
        {}
    )

    story.append(
        Paragraph(
            "Best Project for This Job",
            heading_style
        )
    )

    if isinstance(project, dict):

        story.append(
            Paragraph(
                f"<b>{safe_text(project.get('name', 'Not specified'))}</b>",
                body_style
            )
        )

        story.append(
            Paragraph(
                f"<b>Relevance:</b> "
                f"{safe_text(project.get('relevance', 0))}%",
                body_style
            )
        )

        story.append(
            Paragraph(
                f"<b>Why it matches:</b> "
                f"{safe_text(project.get('reason', ''))}",
                body_style
            )
        )

        skills = project.get(
            "skills_demonstrated",
            []
        )

        if isinstance(skills, list):

            for skill in skills:

                story.append(
                    Paragraph(
                        f"• {safe_text(skill)}",
                        body_style
                    )
                )

    # ========================================================
    # EXPERIENCE
    # ========================================================

    add_list_section(
        "Experience to Highlight",
        analysis.get(
            "experience_to_highlight",
            []
        )
    )

    # ========================================================
    # CV RECOMMENDATIONS
    # ========================================================

    add_list_section(
        "CV Recommendations",
        analysis.get(
            "cv_recommendations",
            []
        )
    )

    # ========================================================
    # LEARNING RECOMMENDATIONS
    # ========================================================

    add_list_section(
        "Skills to Learn",
        analysis.get(
            "learning_recommendations",
            []
        )
    )

    # ========================================================
    # 7-DAY PLAN
    # ========================================================

    story.append(
        Paragraph(
            "7-Day Preparation Plan",
            heading_style
        )
    )

    seven_day_plan = analysis.get(
        "seven_day_plan",
        []
    )

    if isinstance(seven_day_plan, list):

        for index, day in enumerate(
            seven_day_plan,
            start=1
        ):

            if isinstance(day, dict):

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

                story.append(
                    Paragraph(
                        f"<b>Day {day_number}: "
                        f"{safe_text(focus)}</b>",
                        body_style
                    )
                )

                if isinstance(tasks, list):

                    for task in tasks:

                        story.append(
                            Paragraph(
                                f"• {safe_text(task)}",
                                small_style
                            )
                        )

            else:

                story.append(
                    Paragraph(
                        f"<b>Day {index}</b>",
                        body_style
                    )
                )

                story.append(
                    Paragraph(
                        f"• {safe_text(day)}",
                        small_style
                    )
                )

    # ========================================================
    # INTERVIEW QUESTIONS
    # ========================================================

    story.append(
        PageBreak()
    )

    story.append(
        Paragraph(
            "Interview Questions",
            heading_style
        )
    )

    questions = analysis.get(
        "interview_questions",
        {}
    )

    if isinstance(questions, dict):

        categories = {
            "hr": "HR Questions",
            "technical": "Technical Questions",
            "cv_based": "CV-Based Questions",
            "project_based": "Project Questions",
            "behavioral": "Behavioral Questions",
        }

        for key, title in categories.items():

            story.append(
                Paragraph(
                    title,
                    ParagraphStyle(
                        f"{key}Heading",
                        parent=styles["Heading3"],
                        fontSize=11,
                        leading=14,
                        spaceBefore=8,
                        spaceAfter=5,
                    )
                )
            )

            question_list = questions.get(
                key,
                []
            )

            if isinstance(
                question_list,
                list
            ):

                for number, question in enumerate(
                    question_list,
                    start=1
                ):

                    story.append(
                        Paragraph(
                            f"{number}. "
                            f"{safe_text(question)}",
                            small_style
                        )
                    )

    # ========================================================
    # FOOTER
    # ========================================================

    story.append(
        Spacer(1, 20)
    )

    story.append(
        Paragraph(
            "Generated by AI Placement Copilot",
            ParagraphStyle(
                "Footer",
                parent=small_style,
                alignment=TA_CENTER,
            )
        )
    )

    # ========================================================
    # BUILD PDF
    # ========================================================

    document.build(
        story
    )

    buffer.seek(0)

    return buffer