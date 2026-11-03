import os
from pathlib import Path
from datetime import date, timedelta
import pandas as pd
import streamlit as st

try:
    from google import genai
except ImportError:
    genai = None

APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title="My Engineering Degree OS", page_icon="🎓", layout="wide")

FILES = {
    "semesters": "semesters.csv",
    "courses": "courses.csv",
    "calendar": "academic_calendar.csv",
    "assessments": "assessments.csv",
    "scores": "scores.csv",
    "plan": "plan_checklist.csv",
    "syllabus": "university_syllabus.csv",
}

DEFAULTS = {
    "semesters": pd.DataFrame([
        {"semester": i, "status": "Completed" if i < 3 else ("In Progress" if i == 3 else "Not Started"),
         "total_credits": [22,23,24,24,24,24,22,20][i-1],
         "completed_credits": [22,23,12,0,0,0,0,0][i-1]}
        for i in range(1, 9)
    ]),
    "courses": pd.DataFrame([
        [1,"MA101","Engineering Mathematics I",4,"Matrices; Calculus; Differential equations","Completed"],
        [1,"PH101","Engineering Physics",4,"Waves; Optics; Semiconductors","Completed"],
        [1,"CS101","Programming in C",4,"Algorithms; Control statements; Arrays; Functions","Completed"],
        [2,"MA201","Engineering Mathematics II",4,"Differential equations; Laplace transforms","Completed"],
        [2,"EC201","Basic Electronics",3,"Diodes; Transistors; Logic gates","Completed"],
        [2,"CS201","Python Programming",4,"Data types; Functions; OOP; Files","Completed"],
        [3,"CS301","Data Structures",4,"Stacks; Queues; Trees; Graphs","In Progress"],
        [3,"CS302","Database Management Systems",4,"ER model; SQL; Normalization; Transactions","In Progress"],
        [3,"CS303","Digital Design and Computer Organization",4,"Number systems; Logic gates; Adders; CPU organization","Not Started"],
        [4,"CS401","Operating Systems",4,"Processes; Synchronization; Memory management; File systems","Not Started"],
        [4,"CS402","Computer Networks",4,"OSI model; TCP/IP; Routing; Transport layer","Not Started"],
        [4,"CS403","Design and Analysis of Algorithms",4,"Complexity; Greedy; Dynamic programming; Graph algorithms","Not Started"],
        [5,"CS501","Software Engineering",4,"Development models; Requirements; Testing; Maintenance","Not Started"],
        [5,"CS502","Web Technologies",4,"HTML; CSS; JavaScript; APIs","Not Started"],
        [5,"CS503","Theory of Computation",4,"Automata; Regular expressions; Grammars; Turing machines","Not Started"],
        [6,"CS601","Artificial Intelligence",4,"Search; Knowledge representation; Machine learning basics","Not Started"],
        [6,"CS602","Compiler Design",4,"Lexical analysis; Parsing; Semantic analysis; Code generation","Not Started"],
        [6,"CS603","Cloud Computing",3,"Virtualization; Service models; Deployment models","Not Started"],
        [7,"CS701","Machine Learning",4,"Regression; Classification; Clustering; Model evaluation","Not Started"],
        [7,"CS702","Major Project I",6,"Problem definition; Literature review; Design; Prototype","Not Started"],
        [7,"CS703","Professional Elective",3,"Topics depend on selected elective","Not Started"],
        [8,"CS801","Major Project II",10,"Implementation; Testing; Documentation; Presentation","Not Started"],
        [8,"CS802","Internship",6,"Industry experience; Report; Evaluation","Not Started"],
        [8,"CS803","Professional Practice",2,"Ethics; Communication; Career preparation","Not Started"],
    ], columns=["semester","course_code","course_name","credits","syllabus","status"]),
    "calendar": pd.DataFrame([
        ["2026-27",3,"2026-11-14","Holiday","College holiday (sample)"],
        ["2026-27",3,"2026-11-20","Academic","Last working day (sample)"],
        ["2026-27",3,"2026-12-01","Academic","Semester examination period begins (sample)"],
        ["2026-27",4,"2027-01-14","Holiday","Festival holiday (sample)"],
    ], columns=["academic_year","semester","date","event_type","title"]),
    "assessments": pd.DataFrame([
        [3,"CS301","IA1","2026-11-10",30,"Planned"],
        [3,"CS302","IA1","2026-11-12",30,"Planned"],
        [3,"CS303","Assignment","2026-11-18",10,"Planned"],
        [3,"CS301","Lab Evaluation","2026-11-24",25,"Planned"],
        [3,"CS302","Project Review","2026-12-02",20,"Planned"],
        [3,"CS301","End Semester Exam","2026-12-15",100,"Planned"],
        [4,"CS401","IA1","2027-03-10",30,"Planned"],
    ], columns=["semester","course_code","assessment_type","date","max_marks","status"]),
    "scores": pd.DataFrame([
        [1,"MA101","End Semester",82,100,"A"],
        [1,"PH101","End Semester",76,100,"B+"],
        [1,"CS101","End Semester",88,100,"A"],
        [2,"MA201","End Semester",79,100,"B+"],
        [2,"EC201","End Semester",84,100,"A"],
        [2,"CS201","End Semester",91,100,"A+"],
    ], columns=["semester","course_code","assessment_type","score","max_marks","grade"]),
    "plan": pd.DataFrame([
        ["Semester Preparation","Download current syllabus","2026-11-03","Done","Check the official university portal"],
        ["Assessments","Prepare for IA1 - Data Structures","2026-11-09","In Progress","Revise stacks, queues, trees and graphs"],
        ["Projects","Choose mini-project problem statement","2026-11-12","Not Started","Discuss ideas with the project team"],
        ["Documents","Organize marksheets and certificates","2026-12-01","Not Started","Keep digital and hard copies"],
        ["Skills","Complete one aptitude mock test","2026-11-15","Not Started","Review incorrect answers"],
        ["Internship/Placement","Update resume","2026-12-10","Not Started","Add current skills and projects"],
    ], columns=["category","item","target_date","status","notes"]),
    "syllabus": pd.DataFrame([
        ["Programme","Engineering degree programme","8 semesters","Use this field to enter the official university/programme name."],
        ["Expected credits","Refer to official regulations","Not specified","Enter the verified credit requirement from the university source."],
    ], columns=["section","detail","value","source_reference"]),
}

def load_table(key):
    path = DATA_DIR / FILES[key]
    if not path.exists():
        DEFAULTS[key].to_csv(path, index=False)
    try:
        return pd.read_csv(path)
    except Exception as exc:
        st.error(f"Could not read {FILES[key]}: {exc}")
        return DEFAULTS[key].copy()

def save_table(key, df):
    df.to_csv(DATA_DIR / FILES[key], index=False)

def safe_date(series):
    return pd.to_datetime(series, errors="coerce").dt.date

tables = {k: load_table(k) for k in FILES}
sem = tables["semesters"]
courses = tables["courses"]
calendar = tables["calendar"]
assessments = tables["assessments"]
scores = tables["scores"]
plan = tables["plan"]

st.sidebar.title("🎓 Degree OS")
st.sidebar.caption("Your 1st–8th semester command center")
page = st.sidebar.radio("Navigate", [
    "Dashboard", "Semesters 1-8", "Courses & Syllabus", "University Syllabus",
    "Academic / Leave Calendar", "Internal Assessments", "Status Tracker",
    "Scorecard", "Plan & Checklist", "Ask Degree AI", "Data Admin"
])
st.sidebar.divider()
st.sidebar.caption("Prototype data is editable. Replace sample dates, courses and marks with verified university information.")

def metric_row(items):
    cols = st.columns(len(items))
    for col, (label, value, help_text) in zip(cols, items):
        col.metric(label, value, help=help_text)

def next_event(df, label_col="title"):
    if df.empty or "date" not in df:
        return "No data"
    tmp = df.copy()
    tmp["_date"] = safe_date(tmp["date"])
    upcoming = tmp[tmp["_date"].notna() & (tmp["_date"] >= date.today())].sort_values("_date")
    if upcoming.empty:
        return "No upcoming event"
    row = upcoming.iloc[0]
    return f"{row['_date'].strftime('%d %b %Y')} · {row.get(label_col, 'Event')}"

def completion_percent(df):
    total = pd.to_numeric(df.get("total_credits", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()
    done = pd.to_numeric(df.get("completed_credits", pd.Series(dtype=float)), errors="coerce").fillna(0).sum()
    return (done / total * 100) if total else 0

if page == "Dashboard":
    st.title("My Engineering Degree OS")
    st.write("A single place to plan, track and review your engineering degree journey.")
    current = sem[sem["status"].astype(str).str.lower().eq("in progress")]
    current_sem = int(current.iloc[0]["semester"]) if not current.empty else "Not set"
    pct = completion_percent(sem)
    completed_credits = pd.to_numeric(sem["completed_credits"], errors="coerce").fillna(0).sum()
    total_credits = pd.to_numeric(sem["total_credits"], errors="coerce").fillna(0).sum()
    score_pct = (pd.to_numeric(scores["score"], errors="coerce").sum() /
                 pd.to_numeric(scores["max_marks"], errors="coerce").sum() * 100) if not scores.empty and pd.to_numeric(scores["max_marks"], errors="coerce").sum() else 0
    metric_row([
        ("Current semester", current_sem, "Based on semester status"),
        ("Degree progress", f"{pct:.1f}%", "Completed credits / total planned credits"),
        ("Credits completed", f"{completed_credits:g} / {total_credits:g}", "Based on semesters.csv"),
        ("Prototype score %", f"{score_pct:.1f}%", "Simple aggregate score; not official CGPA"),
    ])
    st.subheader("Coming up")
    c1, c2 = st.columns(2)
    c1.info("**Next assessment**\n\n" + next_event(assessments, "assessment_type"))
    c2.info("**Next holiday / academic event**\n\n" + next_event(calendar))
    st.subheader("Semester progress")
    progress = sem.copy()
    progress["progress"] = (pd.to_numeric(progress["completed_credits"], errors="coerce").fillna(0) /
                            pd.to_numeric(progress["total_credits"], errors="coerce").replace(0, pd.NA).fillna(1) * 100)
    st.bar_chart(progress.set_index(progress["semester"].astype(str))["progress"])
    st.caption("Progress is calculated from completed credits. Sample records are provided for demonstration.")
    st.subheader("Priority checklist")
    if not plan.empty:
        p = plan.copy()
        p["_date"] = safe_date(p["target_date"])
        p = p[p["status"].astype(str).str.lower() != "done"].sort_values("_date")
        st.dataframe(p.drop(columns=["_date"]), use_container_width=True, hide_index=True)
    else:
        st.write("No checklist items yet.")

elif page == "Semesters 1-8":
    st.title("Semesters 1–8")
    st.write("Review the sample credit allocation and academic progress across all eight semesters.")
    st.caption("Credit figures are demonstration values, not verified university requirements.")
    cols = st.columns(2)
    for idx, row in sem.sort_values("semester").reset_index(drop=True).iterrows():
        with cols[idx % 2]:
            total = float(row.get("total_credits", 0) or 0)
            done = float(row.get("completed_credits", 0) or 0)
            progress = min(done / total, 1.0) if total else 0
            st.markdown(f"### Semester {int(row['semester'])}")
            st.progress(progress, text=f"{done:g} / {total:g} credits · {row['status']}")
            st.caption(f"{len(courses[courses['semester'] == row['semester']])} courses")
            st.divider()

elif page == "Courses & Syllabus":
    st.title("Courses & Syllabus")
    semester = st.selectbox("Select semester", sorted(courses["semester"].dropna().unique().tolist()), format_func=lambda x: f"Semester {int(x)}")
    filtered = courses[courses["semester"] == semester]
    st.dataframe(filtered[["course_code","course_name","credits","syllabus","status"]], use_container_width=True, hide_index=True)
    st.caption("Syllabus topics are sample summaries. Replace them with the official course syllabus.")

elif page == "University Syllabus":
    st.title("University Syllabus")
    st.write("Programme-level syllabus reference. Enter only verified university details.")
    st.dataframe(tables["syllabus"], use_container_width=True, hide_index=True)
    st.info(
    "**Academic data notice:** This prototype currently uses sample "
    "academic information. University-specific regulations, credit "
    "requirements and CGPA calculations will be added once verified "
    "against the official university syllabus and regulations."
)
    st.markdown("**Official source/reference:** Add the university syllabus URL, regulation document title, academic year and page/section in Data Admin.")

elif page == "Academic / Leave Calendar":
    st.title("Academic / Leave Calendar")
    if not calendar.empty:
        c1, c2 = st.columns(2)
        years = ["All"] + sorted(calendar["academic_year"].dropna().astype(str).unique().tolist())
        year = c1.selectbox("Academic year", years)
        sems = ["All"] + sorted(calendar["semester"].dropna().unique().tolist())
        selected_sem = c2.selectbox("Semester", sems, format_func=lambda x: x if x == "All" else f"Semester {int(x)}")
        view = calendar.copy()
        if year != "All": view = view[view["academic_year"].astype(str) == year]
        if selected_sem != "All": view = view[view["semester"] == selected_sem]
        st.dataframe(view.sort_values("date"), use_container_width=True, hide_index=True)
    else:
        st.info("No calendar events added yet.")

elif page == "Internal Assessments":
    st.title("Internal Assessments")
    if not assessments.empty:
        sem_filter = st.selectbox("Semester", ["All"] + sorted(assessments["semester"].dropna().unique().tolist()), format_func=lambda x: x if x == "All" else f"Semester {int(x)}")
        view = assessments.copy()
        if sem_filter != "All": view = view[view["semester"] == sem_filter]
        st.dataframe(view.sort_values("date"), use_container_width=True, hide_index=True)
    else:
        st.info("No assessments added yet.")

elif page == "Status Tracker":
    st.title("Status Tracker")
    semester = st.selectbox("Choose semester", sorted(courses["semester"].dropna().unique().tolist()), format_func=lambda x: f"Semester {int(x)}")
    view = courses[courses["semester"] == semester].copy()
    counts = view["status"].value_counts()
    metric_row([
        ("Not started", int(counts.get("Not Started", 0)), "Courses not yet started"),
        ("In progress", int(counts.get("In Progress", 0)), "Courses currently underway"),
        ("Completed", int(counts.get("Completed", 0)), "Completed courses"),
    ])
    done = int(counts.get("Completed", 0))
    st.progress(done / len(view) if len(view) else 0, text=f"{done} of {len(view)} courses completed")
    st.dataframe(view[["course_code","course_name","status"]], use_container_width=True, hide_index=True)

elif page == "Scorecard":
    st.title("Scorecard")
    if not scores.empty:
        s = scores.copy()
        s["score"] = pd.to_numeric(s["score"], errors="coerce")
        s["max_marks"] = pd.to_numeric(s["max_marks"], errors="coerce")
        total_max = s["max_marks"].sum()
        percentage = s["score"].sum() / total_max * 100 if total_max else 0
        metric_row([
            ("Prototype score percentage", f"{percentage:.2f}%", "Total score / total maximum marks × 100"),
            ("Assessments recorded", len(s), "Rows in scores.csv"),
            ("Marks obtained", f"{s['score'].sum():g}", "Sum of available scores"),
        ])
        st.dataframe(s, use_container_width=True, hide_index=True)
        st.bar_chart(s.groupby("semester")["score"].mean())
    else:
        st.info("No scores recorded yet.")
    st.warning("This is a simple prototype percentage, not an official university SGPA/CGPA. Add the verified university formula before using an official GPA calculation.")

elif page == "Plan & Checklist":
    st.title("Plan & Checklist")
    st.write("Your degree execution panel: tasks, deadlines, status and notes.")
    editable = plan.copy()
    # DateColumn requires a date/datetime dtype, but CSV data is loaded as strings.
    # Convert before opening the editor; convert back to ISO strings when saving.
    editable["target_date"] = pd.to_datetime(editable["target_date"], errors="coerce").dt.date
    edited = st.data_editor(editable, use_container_width=True, num_rows="dynamic", hide_index=True,
        column_config={
            "category": st.column_config.SelectboxColumn(options=["Semester Preparation","Assessments","Labs","Projects","Documents","Skills","Internship/Placement"]),
            "status": st.column_config.SelectboxColumn(options=["Not Started","In Progress","Done"]),
            "target_date": st.column_config.DateColumn(format="YYYY-MM-DD"),
        }, key="plan_editor")
    if st.button("Save checklist", type="primary"):
        edited_to_save = edited.copy()
        edited_to_save["target_date"] = pd.to_datetime(edited_to_save["target_date"], errors="coerce").dt.strftime("%Y-%m-%d")
        save_table("plan", edited_to_save)
        st.success("Checklist saved to data/plan_checklist.csv.")
        st.rerun()
    today = date.today()
    dates = safe_date(edited["target_date"]) if not edited.empty else pd.Series(dtype=object)
    status = edited["status"].astype(str).str.lower() if not edited.empty else pd.Series(dtype=str)
    done = int(status.eq("done").sum())
    due_soon = int(((dates >= today) & (dates <= today + timedelta(days=7)) & ~status.eq("done")).sum()) if len(dates) else 0
    overdue = int(((dates < today) & ~status.eq("done")).sum()) if len(dates) else 0
    metric_row([("Total items", len(edited), "Checklist rows"),("Done",done,"Completed items"),("Due soon",due_soon,"Due within 7 days"),("Overdue",overdue,"Past target date and not done")])
    if len(dates):
        st.subheader("This week")
        week = edited[(dates >= today) & (dates <= today + timedelta(days=7))]
        st.dataframe(week, use_container_width=True, hide_index=True)

elif page == "Ask Degree AI":
    st.title("Ask Degree AI")
    st.write("Ask questions about your loaded courses, dates, marks and checklist. Answers are grounded in the CSV data.")
    question = st.chat_input("Example: What courses are incomplete in Semester 3?")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("source"): st.caption("Data area: " + msg["source"])
    def answer_question(q):
        ql = q.lower()
        if "incomplete" in ql or "left" in ql or "pending course" in ql:
            import re
            match = re.search(r"sem(?:ester)?\s*(\d+)", ql)
            sem_no = int(match.group(1)) if match else None
            df = courses.copy()
            if sem_no: df = df[df["semester"] == sem_no]
            df = df[df["status"].astype(str).str.lower() != "completed"]
            if df.empty: return "No incomplete courses found in the selected data.", "Courses"
            return "Incomplete courses:\n" + "\n".join(f"- {r.course_code}: {r.course_name} ({r.status})" for r in df.itertuples()), "Courses"
        if "next" in ql and ("assessment" in ql or "ia" in ql or "exam" in ql):
            return "Next assessment: " + next_event(assessments, "assessment_type"), "Assessments"
        if "holiday" in ql or "leave" in ql:
            return "Next calendar event: " + next_event(calendar), "Calendar"
        if "topic" in ql or "syllabus" in ql:
            matches = courses[courses.apply(lambda r: str(r["course_name"]).lower() in ql or str(r["course_code"]).lower() in ql, axis=1)]
            if not matches.empty:
                r = matches.iloc[0]
                return f"{r['course_name']} ({r['course_code']}) topics: {r['syllabus']}", "Courses"
        if "checklist" in ql or "task" in ql or "plan" in ql:
            pending = plan[plan["status"].astype(str).str.lower() != "done"]
            if pending.empty: return "All checklist items are marked Done.", "Plan"
            return "Pending checklist items:\n" + "\n".join(f"- {r.item} — {r.status} (target: {r.target_date})" for r in pending.itertuples()), "Plan"
        if "status" in ql and ("semester" in ql or "sem" in ql):
            return "\n".join(f"Semester {int(r.semester)}: {r.status}" for r in sem.itertuples()), "Semesters"
        if "cgpa" in ql or "gpa formula" in ql or "regulation" in ql or "eligibility" in ql:
            return "I cannot verify that from the current Degree OS data.", "Safety fallback"
        return None, None

    def answer_with_gemini(q):
        """Use Gemini only as a fallback, grounded strictly in the loaded CSV tables."""
        api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
        if not api_key or genai is None:
            return "I cannot verify that from the current Degree OS data.", "Local data / Gemini not configured"

        data_context = "\n\n".join([
            "SEMESTERS:\n" + sem.to_csv(index=False),
            "COURSES:\n" + courses.to_csv(index=False),
            "ASSESSMENTS:\n" + assessments.to_csv(index=False),
            "ACADEMIC CALENDAR:\n" + calendar.to_csv(index=False),
            "SCORES:\n" + scores.to_csv(index=False),
            "PLAN AND CHECKLIST:\n" + plan.to_csv(index=False),
            "UNIVERSITY SYLLABUS:\n" + tables["syllabus"].to_csv(index=False),
        ])
        prompt = f"""You are Ask Degree AI inside an engineering student academic dashboard.
Answer the user's question using ONLY the Degree OS data provided below.
Do not use outside knowledge, assumptions, or invented facts.
If the answer is not directly supported by the data, reply with exactly:
I cannot verify that from the current Degree OS data.
Never invent official university regulations, dates, credit requirements, eligibility rules, SGPA or CGPA formulas.
Be concise and clearly distinguish sample records from verified official information.

DEGREE OS DATA:
{data_context}

USER QUESTION: {q}
"""
        try:
            client = genai.Client(api_key=api_key)
            result = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            answer = (result.text or "").strip()
            if not answer:
                return "I cannot verify that from the current Degree OS data.", "Safety fallback"
            return answer, "Gemini · grounded in loaded Degree OS data"
        except Exception:
            return "I cannot verify that from the current Degree OS data.", "Gemini unavailable; safe fallback"

    if question:
        st.session_state.chat_history.append({"role":"user","content":question})
        response, source = answer_question(question)
        if response is None:
            response, source = answer_with_gemini(question)
        st.session_state.chat_history.append({"role":"assistant","content":response,"source":source})
        st.rerun()
    st.caption("Answers use loaded Degree OS data. Gemini is optional; if it is unavailable, the app uses the safe fallback. Official university rules and GPA formulas are never guessed.")

elif page == "Data Admin":
    st.title("Data Admin")
    st.write("Edit the CSV-backed tables here. Changes are saved to the project's data folder.")
    labels = {
        "semesters":"Semesters", "courses":"Courses", "calendar":"Academic calendar",
        "assessments":"Assessments", "scores":"Scores", "plan":"Plan & checklist", "syllabus":"University syllabus"
    }
    selected = st.selectbox("Choose data table", list(labels), format_func=lambda x: labels[x])
    edited = st.data_editor(tables[selected], use_container_width=True, num_rows="dynamic", hide_index=True, key=f"admin_{selected}")
    if st.button("Save table", type="primary"):
        save_table(selected, edited)
        st.success(f"{FILES[selected]} saved.")
        st.rerun()
    st.info("Use verified university information. Never add API keys or passwords to CSV files or GitHub.")
