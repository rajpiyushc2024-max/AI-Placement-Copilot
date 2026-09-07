import os
import json
import re
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


def get_groq_client(api_key=None):
    env_path = Path(__file__).resolve().parent / ".env"
    load_dotenv(
        dotenv_path=env_path,
        override=True
    )
    key = api_key or os.getenv("GROQ_API_KEY")
    if not key:
        try:
            import streamlit as st
            if "GROQ_API_KEY" in st.secrets:
                key = st.secrets["GROQ_API_KEY"]
        except Exception:
            pass

    if not key:
        raise ValueError(
            "GROQ_API_KEY is missing. Please create a .env file with your GROQ_API_KEY (see .env.example), provide it in the sidebar, or set it in your environment/secrets."
        )
    return Groq(api_key=key)


# ============================================================
# ANALYZE CV
# ============================================================

def analyze_cv(
    cv_text,
    jd_text,
    system_prompt,
    api_key=None
):

    user_prompt = f"""
Analyze the candidate CV against the Job Description.

IMPORTANT:
- Return ONLY a JSON object.
- Do NOT return <think>.
- Do NOT return reasoning.
- Do NOT return markdown.
- Do NOT return ```json.
- Start directly with {{.
- End directly with }}.

CANDIDATE CV
============

{cv_text}


JOB DESCRIPTION
===============

{jd_text}
"""


    # ========================================================
    # CALL QWEN
    # ========================================================

    client = get_groq_client(api_key=api_key)

    response = client.chat.completions.create(

        model="qwen/qwen3.6-27b",

        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],

        # Non-thinking mode
        reasoning_effort="none",

        # Do not return reasoning
        reasoning_format="hidden",

        # Force JSON output
        response_format={
            "type": "json_object"
        },

        temperature=0.2,

        max_completion_tokens=3000
    )


    # ========================================================
    # GET MODEL RESPONSE
    # ========================================================

    content = response.choices[0].message.content


    if not content:
        raise ValueError(
            "Qwen returned an empty response."
        )


    content = content.strip()


    # ========================================================
    # FALLBACK 1 — REMOVE THINK TAGS
    # ========================================================

    if "<think>" in content:

        content = re.sub(
            r"<think>.*?</think>",
            "",
            content,
            flags=re.DOTALL
        )

        content = content.strip()


    # ========================================================
    # FALLBACK 2 — REMOVE MARKDOWN JSON
    # ========================================================

    if content.startswith("```json"):

        content = content[
            len("```json"):
        ]


    elif content.startswith("```"):

        content = content[
            len("```"):
        ]


    if content.endswith("```"):

        content = content[
            :-len("```")
        ]


    content = content.strip()


    # ========================================================
    # PARSE JSON
    # ========================================================

    try:

        analysis = json.loads(
            content
        )

        return analysis


    except json.JSONDecodeError:

        # ====================================================
        # FALLBACK 3 — FIND JSON OBJECT
        # ====================================================

        start = content.find("{")
        end = content.rfind("}")

        if start != -1 and end != -1:

            json_text = content[
                start:end + 1
            ]

            try:

                return json.loads(
                    json_text
                )

            except json.JSONDecodeError:

                pass


        # ====================================================
        # FINAL ERROR
        # ====================================================

        raise ValueError(
            "Qwen returned invalid JSON.\n\n"
            f"Model response:\n{content}"
        )