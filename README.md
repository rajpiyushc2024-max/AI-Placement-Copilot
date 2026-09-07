# 🤖 AI Placement Copilot

AI-powered application that analyzes a candidate's CV against a Job Description and provides job-fit insights, skill gaps, CV recommendations, and interview preparation.

## 🚀 Features

- Upload CV in PDF/DOCX format
- Enter Job Description
- CV-JD match score
- Skill gap analysis
- CV improvement recommendations
- Learning recommendations
- 7-day preparation plan
- Interview questions
- Downloadable PDF report

## 🏗️ Architecture

```text
                    USER
                      │
              ┌───────┴────────┐
              │                │
             CV               JD
              │                │
              └───────┬────────┘
                      ▼
              Streamlit UI
                 app.py
                      │
                      ▼
              Document Parser
                parser.py
                      │
                      ▼
              CV Text + JD Text
                      │
                      ▼
                System Prompt
                prompts.py
                      │
                      ▼
              Groq API + Qwen
                 llm.py
                      │
                      ▼
              Structured JSON
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
      Match Score  Skill Gaps  Recommendations
          │           │           │
          └───────────┼───────────┘
                      ▼
              Interview Preparation
                      │
                      ▼
                 PDF Report
                 report.py