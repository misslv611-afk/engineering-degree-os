# Engineering Degree OS

A Streamlit prototype for managing engineering degree information across Semesters 1–8.

## Features
- Dashboard and semester progress
- Courses and syllabus topics
- University syllabus reference table
- Academic calendar
- Internal assessments
- Course status tracker
- Marks scorecard with basic percentage (not official CGPA)
- Study plan and checklist
- Ask Degree AI (Gemini optional; local fallback included)
- Data Admin for editing CSV data

## Run locally
```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Gemini API key (optional)
Create `.streamlit/secrets.toml`:
```toml
GEMINI_API_KEY = "paste-your-own-key-here"
```
Never commit this file. It is ignored by `.gitignore`. For Streamlit Community Cloud, add `GEMINI_API_KEY` in the app's Secrets settings.

## Data files
All editable data is in `data/`. Keep the existing CSV files when replacing app code. The app recognizes common column-name variations and supplies empty columns when a field is missing. Back up your data folder before editing.

## Important
This is an academic organizer prototype. It does not claim to know your university, regulation year, official syllabus, credit requirements, examination rules or CGPA formula. Enter and verify official information from your institution. The Scorecard percentage is only a simple percentage of the marks entered.
