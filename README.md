# My Engineering Degree OS

A CSV-powered Streamlit command center for tracking an engineering degree from Semester 1 to Semester 8.

## Features
- Dashboard with semester, credit and progress summaries
- Eight-semester overview
- Courses and syllabus topics filtered by semester
- University syllabus reference page
- Academic / leave calendar
- Internal assessments
- Course status tracker
- Scorecard with clearly labelled prototype percentage (not official CGPA)
- Editable Plan & Checklist with due-soon and overdue counts
- Local, data-grounded Ask Degree AI chatbot with a safe fallback
- Data Admin editor for all CSV tables

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Install dependencies:
   `python -m pip install -r requirements.txt`
4. Start the app:
   `python -m streamlit run app.py`

## Project structure
```text
engineering-degree-os/
├── app.py
├── requirements.txt
├── README.md
└── data/
    ├── semesters.csv
    ├── courses.csv
    ├── academic_calendar.csv
    ├── assessments.csv
    ├── scores.csv
    ├── plan_checklist.csv
    └── university_syllabus.csv
```

## Important data note
The included records are demonstration/sample data based on the assignment brief. Replace course names, dates, marks, credits, academic calendar entries and syllabus references with verified information from your own university. The app does not invent an official SGPA/CGPA formula.

## Deploy
Push the complete folder to a GitHub repository. In Streamlit Community Cloud, create an app using the repository, branch and `app.py` as the entry point. Do not upload API keys or secrets.
