from __future__ import annotations

from pathlib import Path
from datetime import date
import os
import re
import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "data"
st.set_page_config(page_title="Engineering Degree OS", page_icon="🎓", layout="wide")

# ---------- Data loading and compatibility ----------
FILES = {
    "semesters": "semesters.csv",
    "courses": "courses.csv",
    "calendar": "academic_calendar.csv",
    "assessments": "assessments.csv",
    "scores": "scores.csv",
    "checklist": "plan_checklist.csv",
    "university": "university_syllabus.csv",
}

DEFAULTS = {
    "semesters": pd.DataFrame([
        {"semester": n, "status": "Not Started", "total_credits": 0, "completed_credits": 0}
        for n in range(1, 9)
    ]),
    "courses": pd.DataFrame(columns=["semester", "course_code", "course_name", "credits", "syllabus", "status"]),
    "calendar": pd.DataFrame(columns=["academic_year", "semester", "date", "event_type", "title"]),
    "assessments": pd.DataFrame(columns=["semester", "course_code", "assessment_type", "date", "max_marks", "status"]),
    "scores": pd.DataFrame(columns=["semester", "course_code", "assessment_type", "score", "max_marks", "grade"]),
    "checklist": pd.DataFrame(columns=["category", "item", "target_date", "status", "notes"]),
    "university": pd.DataFrame(columns=["section", "detail", "value", "source_reference"]),
}

ALIASES = {
    "semester": ["semester", "semester_number", "sem", "term"],
    "status": ["status", "completion_status", "course_status"],
    "total_credits": ["total_credits", "credits_total"],
    "completed_credits": ["completed_credits", "earned_credits"],
    "course_code": ["course_code", "code", "subject_code"],
    "course_name": ["course_name", "name", "subject", "subject_name"],
    "credits": ["credits", "credit", "credit_points"],
    "syllabus": ["syllabus", "syllabus_topics", "topics", "units", "course_content"],
    "date": ["date", "event_date", "assessment_date", "target_date"],
    "event_type": ["event_type", "type", "category"],
    "title": ["title", "event_name", "event", "name"],
    "assessment_type": ["assessment_type", "type", "assessment"],
    "max_marks": ["max_marks", "maximum_marks", "out_of", "total_marks"],
    "score": ["score", "marks", "obtained_marks"],
    "grade": ["grade", "letter_grade"],
    "academic_year": ["academic_year", "year"],
    "category": ["category", "task_category"],
    "item": ["item", "task", "activity", "description"],
    "target_date": ["target_date", "due_date", "date"],
    "notes": ["notes", "remarks", "description"],
    "section": ["section", "topic", "area"],
    "detail": ["detail", "description"],
    "value": ["value", "requirement"],
    "source_reference": ["source_reference", "source", "reference", "url"],
}

def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    return df

def normalize(df: pd.DataFrame, dataset: str) -> pd.DataFrame:
    df = clean_columns(df)
    needed = {
        "semesters": ["semester", "status", "total_credits", "completed_credits"],
        "courses": ["semester", "course_code", "course_name", "credits", "syllabus", "status"],
        "calendar": ["date", "event_type", "title", "semester", "academic_year"],
        "assessments": ["semester", "course_code", "assessment_type", "date", "max_marks", "status"],
        "scores": ["semester", "course_code", "assessment_type", "score", "max_marks", "grade"],
        "checklist": ["category", "item", "target_date", "status", "notes"],
        "university": ["section", "detail", "value", "source_reference"],
    }[dataset]
    for target in needed:
        if target not in df.columns:
            for alias in ALIASES.get(target, [target]):
                if alias in df.columns:
                    df[target] = df[alias]
                    break
        if target not in df.columns:
            df[target] = ""
    return df

@st.cache_data
def read_csv_cached(path: str, modified: float):
    return pd.read_csv(path)

def load_data():
    data = {}
    for key, filename in FILES.items():
        path = DATA_DIR / filename
        if path.exists():
            try:
                df = read_csv_cached(str(path), path.stat().st_mtime)
            except Exception as exc:
                st.warning(f"Could not read {filename}: {exc}. Showing an empty dataset for this section.")
                df = DEFAULTS[key].copy()
        else:
            df = DEFAULTS[key].copy()
        data[key] = normalize(df, key)
    return data

def save_data(key: str, df: pd.DataFrame):
    DATA_DIR.mkdir(exist_ok=True)
    df.to_csv(DATA_DIR / FILES[key], index=False)
    st.cache_data.clear()

data = load_data()

def as_num(value, default=0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

def safe_date(value):
    try:
        return pd.to_datetime(value, errors="coerce")
    except Exception:
        return pd.NaT

def fmt_date(value):
    d = safe_date(value)
    return d.strftime("%d %b %Y") if pd.notna(d) else "Not set"

# ---------- Styling ----------
st.markdown("""
<style>
:root { color-scheme: light; }
.block-container {padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1440px;}
.hero {padding: 1.5rem 1.7rem; border-radius: 18px; background: linear-gradient(120deg,#14213d,#254f77); color:white; margin-bottom:1rem;}
.hero h1 {font-size:2rem; margin:0 0 .35rem 0;}
.hero p {color:#e5edf7; margin:0;}
div[data-testid="stMetric"] {background:#f6f8fc; border:1px solid #e7ebf2; padding:14px; border-radius:14px;}
div[data-testid="stMetric"] label {color:#536174;}
section[data-testid="stSidebar"] {border-right:1px solid #e8edf4;}
.small-muted {color:#667085; font-size:.88rem;}
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("## 🎓 Engineering Degree OS")
st.sidebar.caption("Your academic command centre")
pages = [
    "Dashboard", "Semesters 1–8", "Courses & Syllabus", "University Syllabus",
    "Academic / Leave Calendar", "Internal Assessments", "Status Tracker",
    "Scorecard", "Plan & Checklist", "Ask Degree AI", "Data Admin"
]
page = st.sidebar.radio("Navigate", pages, label_visibility="collapsed")
st.sidebar.divider()
st.sidebar.caption("Prototype • Verify official rules and dates with your university")

def header(title, subtitle=""):
    st.title(title)
    if subtitle:
        st.caption(subtitle)

def table_or_empty(df, message="No records added yet."):
    if df is None or df.empty:
        st.info(message)
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)

def semester_number():
    sems = data["semesters"].copy()
    active = sems[sems["status"].astype(str).str.lower().isin(["in progress", "ongoing", "active", "current"])]
    if not active.empty:
        return int(as_num(active.iloc[0]["semester"], 1))
    completed = sems[sems["status"].astype(str).str.lower().eq("completed")]
    if not completed.empty:
        return min(8, int(as_num(completed["semester"].max(), 1)) + 1)
    return 1

# ---------- Pages ----------
if page == "Dashboard":
    st.markdown('<div class="hero"><h1>Engineering Degree OS</h1><p>One organized space for your semesters, courses, assessments, progress and study plan.</p></div>', unsafe_allow_html=True)
    sems, courses, assessments, scores, cal = (data[k] for k in ["semesters","courses","assessments","scores","calendar"])
    current_sem = semester_number()
    total_courses = len(courses)
    completed_courses = int(courses["status"].astype(str).str.lower().eq("completed").sum()) if total_courses else 0
    completed_credits = sum(as_num(x) for x in sems["completed_credits"])
    total_credits = sum(as_num(x) for x in sems["total_credits"])
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Current semester", f"Semester {current_sem}")
    c2.metric("Courses recorded", total_courses)
    c3.metric("Completed courses", completed_courses)
    c4.metric("Credits recorded", f"{completed_credits:g} / {total_credits:g}")

    # Colourful overall progress bar, calculated only from course statuses.
    progress = (completed_courses / total_courses) if total_courses else 0.0
    progress_pct = round(progress * 100)
    st.subheader("Overall course completion")
    st.markdown(
        f"""
        <div style="background:#e9eef5;border-radius:999px;height:22px;overflow:hidden;
                    box-shadow:inset 0 1px 3px rgba(0,0,0,.08);">
          <div role="progressbar" aria-valuenow="{progress_pct}" aria-valuemin="0"
               aria-valuemax="100"
               style="width:{progress_pct}%;height:100%;border-radius:999px;
                      background:linear-gradient(90deg,#6a5af9 0%,#2589ff 35%,#12b8a6 68%,#8bd450 100%);
                      transition:width .35s ease;">
          </div>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;
                    margin-top:7px;color:#667085;font-size:.9rem;">
          <span>{completed_courses} of {total_courses} courses completed</span>
          <strong style="color:#344054;">{progress_pct}%</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if total_courses == 0:
        st.caption("Add courses and mark their status as Completed to calculate progress.")

    st.subheader("Upcoming academic activity")
    today = pd.Timestamp(date.today())
    if not assessments.empty:
        a = assessments.copy()
        a["_date"] = a["date"].apply(safe_date)
        a = a[a["_date"].notna() & (a["_date"] >= today)].sort_values("_date")
        table_or_empty(a[["date","semester","course_code","assessment_type","max_marks","status"]].head(5), "No future assessments are recorded.")
    else:
        st.info("Add assessment dates in Internal Assessments or Data Admin.")
    st.subheader("Upcoming calendar events")
    if not cal.empty:
        c = cal.copy()
        c["_date"] = c["date"].apply(safe_date)
        c = c[c["_date"].notna() & (c["_date"] >= today)].sort_values("_date")
        table_or_empty(c[["date","event_type","title","semester"]].head(5), "No future calendar events are recorded.")
    else:
        st.info("Add official academic dates when available.")
    st.subheader("Quick access")
    x,y,z = st.columns(3)
    x.info("📚 **Courses**\n\nBrowse subjects and syllabus topics.")
    y.info("📝 **Assessments**\n\nTrack internal tests and marks.")
    z.info("🤖 **Degree AI**\n\nAsk questions using your loaded data.")

elif page == "Semesters 1–8":
    header("Semesters 1–8", "Track progress semester by semester. Credit totals are only what you enter.")
    sems = data["semesters"].copy().sort_values("semester", key=lambda s: pd.to_numeric(s, errors="coerce"))
    table_or_empty(sems)
    st.subheader("Update semester progress")
    with st.form("semester_form"):
        n = st.number_input("Semester number", 1, 8, semester_number())
        status = st.selectbox("Status", ["Not Started","In Progress","Completed","On Hold"])
        total = st.number_input("Total credits (from your verified curriculum)", min_value=0.0, step=1.0)
        done = st.number_input("Completed credits", min_value=0.0, step=1.0)
        submitted = st.form_submit_button("Save semester")
    if submitted:
        sems = sems[sems["semester"].astype(str) != str(int(n))]
        sems = pd.concat([sems, pd.DataFrame([{"semester":int(n),"status":status,"total_credits":total,"completed_credits":done}])], ignore_index=True)
        save_data("semesters", sems)
        st.success("Semester saved. Refreshing data…")
        st.rerun()

elif page == "Courses & Syllabus":
    header("Courses & Syllabus", "Browse your course list and the topics entered for each course.")
    courses = data["courses"].copy()
    if not courses.empty:
        sem_filter = st.selectbox("Filter by semester", ["All"] + sorted(courses["semester"].astype(str).unique().tolist()))
        if sem_filter != "All":
            courses = courses[courses["semester"].astype(str) == sem_filter]
        search = st.text_input("Search course name, code or topic")
        if search:
            mask = courses.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)
            courses = courses[mask]
    table_or_empty(courses[["semester","course_code","course_name","credits","status","syllabus"]] if not courses.empty else courses)

elif page == "University Syllabus":
    header("University Syllabus", "Store official curriculum details with a source reference. Unverified entries are not treated as official.")
    table_or_empty(data["university"])
    st.warning("This prototype does not assume a university, regulation year, official credit requirement or exam rule. Verify each entry against your university's official document.")

elif page == "Academic / Leave Calendar":
    header("Academic / Leave Calendar", "Use official college or university dates. Sample entries must be verified.")
    cal = data["calendar"].copy()
    if not cal.empty:
        cal["_sort"] = cal["date"].apply(safe_date)
        cal = cal.sort_values("_sort", na_position="last").drop(columns="_sort")
    table_or_empty(cal)

elif page == "Internal Assessments":
    header("Internal Assessments", "Track assessment dates, maximum marks and status.")
    table_or_empty(data["assessments"])
    st.subheader("Add assessment")
    with st.form("assessment_form"):
        sem = st.number_input("Semester", 1, 8, semester_number())
        code = st.text_input("Course code")
        typ = st.text_input("Assessment type", "IA1")
        dt = st.date_input("Assessment date")
        maximum = st.number_input("Maximum marks", min_value=0.0, step=1.0)
        status = st.selectbox("Status", ["Planned","Completed","Postponed"])
        add = st.form_submit_button("Add assessment")
    if add:
        new = {"semester":int(sem),"course_code":code.strip(),"assessment_type":typ.strip(),"date":dt.isoformat(),"max_marks":maximum,"status":status}
        save_data("assessments", pd.concat([data["assessments"],pd.DataFrame([new])],ignore_index=True))
        st.success("Assessment added.")
        st.rerun()

elif page == "Status Tracker":
    header("Status Tracker", "A combined view of course completion and semester progress.")
    st.subheader("Course status")
    table_or_empty(data["courses"][["semester","course_code","course_name","status"]] if not data["courses"].empty else data["courses"])
    st.subheader("Semester status")
    table_or_empty(data["semesters"])

elif page == "Scorecard":
    header("Scorecard", "Recorded marks and a simple percentage summary.")
    scores = data["scores"].copy()
    table_or_empty(scores)
    if not scores.empty:
        scores["_score"] = pd.to_numeric(scores["score"], errors="coerce")
        scores["_max"] = pd.to_numeric(scores["max_marks"], errors="coerce")
        valid = scores.dropna(subset=["_score","_max"])
        earned, maximum = valid["_score"].sum(), valid["_max"].sum()
        if maximum > 0:
            st.metric("Prototype score percentage", f"{earned/maximum*100:.2f}%")
            st.caption("This is a basic percentage calculated from entered marks. It is NOT an official CGPA/SGPA conversion.")
    else:
        st.info("Add your assessment marks to see a percentage summary.")

elif page == "Plan & Checklist":
    header("Plan & Checklist", "Keep track of study tasks, preparation and deadlines.")
    tasks = data["checklist"].copy()
    table_or_empty(tasks)
    st.subheader("Add a task")
    with st.form("task_form"):
        category = st.text_input("Category", "Study")
        item = st.text_input("Task")
        due = st.date_input("Target date")
        status = st.selectbox("Task status", ["Not Started","In Progress","Done"])
        notes = st.text_input("Notes")
        add_task = st.form_submit_button("Add task")
    if add_task:
        row = {"category":category,"item":item,"target_date":due.isoformat(),"status":status,"notes":notes}
        save_data("checklist",pd.concat([tasks,pd.DataFrame([row])],ignore_index=True))
        st.success("Task added.")
        st.rerun()

elif page == "Ask Degree AI":
    header("Ask Degree AI", "Answers are grounded in your CSV data. Missing information is not guessed.")
    st.caption("If Gemini is not configured or temporarily unavailable, the app uses a small local data lookup.")
    question = st.text_area("Ask about your semesters, courses, syllabus, assessments or marks", placeholder="Which courses are incomplete in Semester 3?")
    use_gemini = st.checkbox("Use Gemini when an API key is configured", value=True)
    if st.button("Get answer", type="primary") and question.strip():
        # Build a compact context from loaded CSVs only.
        context_parts = []
        for key, df in data.items():
            context_parts.append(f"{key.upper()} DATA:\n{df.head(100).to_csv(index=False)}")
        context = "\n\n".join(context_parts)
        answer = None
        api_key = None
        try:
            api_key = st.secrets.get("GEMINI_API_KEY", None)
        except Exception:
            api_key = os.getenv("GEMINI_API_KEY")
        if use_gemini and api_key:
            try:
                from google import genai
                from google.genai import types
                client = genai.Client(api_key=api_key)
                prompt = (
                    "You are Engineering Degree OS assistant. Answer ONLY from the supplied CSV data. "
                    "Do not invent official university rules, CGPA formulas, dates, credits, syllabus or eligibility. "
                    "If the answer is not present, reply exactly: I cannot verify that from the current Degree OS data.\n\n"
                    f"DATA:\n{context}\n\nQUESTION: {question}"
                )
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(temperature=0.2)
                )
                answer = response.text
            except Exception as exc:
                st.warning(f"Gemini is unavailable right now. Using local data lookup instead. ({type(exc).__name__})")
        if not answer:
            q = question.lower()
            courses = data["courses"]
            if any(k in q for k in ["incomplete","pending","not completed"]):
                result = courses[~courses["status"].astype(str).str.lower().eq("completed")]
                answer = result[["semester","course_code","course_name","status"]].to_string(index=False) if not result.empty else "No incomplete courses are recorded."
            elif "course" in q or "subject" in q:
                result = courses
                for token in re.findall(r"\b[1-8]\b", q):
                    result = result[result["semester"].astype(str) == token]
                answer = result[["semester","course_code","course_name","status","syllabus"]].to_string(index=False) if not result.empty else "I cannot verify that from the current Degree OS data."
            elif "assessment" in q or "exam" in q or "test" in q:
                result = data["assessments"]
                if not result.empty:
                    answer = result.to_string(index=False)
                else:
                    answer = "I cannot verify that from the current Degree OS data."
            elif "cgpa" in q or "sgpa" in q or "percentage" in q:
                answer = "I cannot verify an official CGPA/SGPA from the current Degree OS data. The Scorecard can show a basic percentage from entered marks only."
            elif "semester" in q or "progress" in q:
                answer = data["semesters"].to_string(index=False) if not data["semesters"].empty else "I cannot verify that from the current Degree OS data."
            else:
                answer = "I cannot verify that from the current Degree OS data."
        st.markdown("### Answer")
        st.write(answer)

elif page == "Data Admin":
    header("Data Admin", "Review and edit the CSV records used by the application.")
    st.warning("Keep a backup before editing. Do not enter private API keys into CSV files.")
    labels = {
        "semesters":"Semesters","courses":"Courses","calendar":"Academic calendar",
        "assessments":"Assessments","scores":"Scores","checklist":"Plan checklist","university":"University syllabus"
    }
    chosen = st.selectbox("Choose dataset", list(labels), format_func=lambda x: labels[x])
    edited = st.data_editor(data[chosen], num_rows="dynamic", use_container_width=True, key=f"editor_{chosen}")
    if st.button("Save dataset", type="primary"):
        save_data(chosen, edited)
        st.success(f"{FILES[chosen]} saved.")
        st.rerun()

st.sidebar.divider()
st.sidebar.caption("Engineering Degree OS • Academic data stays in your project CSV files")
