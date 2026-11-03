"""
Engineering Degree OS
An academic planning, tracking, and AI guidance platform for engineering students.
Built with Streamlit, Pandas, and the Google GenAI SDK.
"""

import os
import time
import datetime
from pathlib import Path
from typing import Dict, Tuple, Optional

import pandas as pd
import streamlit as st

# Attempt official Google GenAI SDK import
try:
    from google import genai
    from google.genai import types
    from google.genai.errors import APIError
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


# ==========================================
# 1. APPLICATION CONFIGURATION & STYLES
# ==========================================

st.set_page_config(
    page_title="Engineering Degree OS",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom SaaS styling: Clean slate, navy, teal accents, rounded cards
st.markdown(
    """
    <style>
    /* Global styles */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }
    
    /* Metrics and Cards */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1.1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        margin-bottom: 0.8rem;
    }
    .metric-label {
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #0f172a;
        margin-top: 0.2rem;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #475569;
        margin-top: 0.2rem;
    }

    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-completed { background-color: #dcfce7; color: #166534; }
    .badge-progress { background-color: #e0f2fe; color: #075985; }
    .badge-pending { background-color: #f1f5f9; color: #475569; }
    .badge-urgent { background-color: #fee2e2; color: #991b1b; }
    .badge-warning { background-color: #fef3c7; color: #92400e; }

    /* Clean Card Layout */
    .os-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .os-card-header {
        font-size: 1.05rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.5rem;
    }

    /* Source tag */
    .source-tag {
        font-size: 0.75rem;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 6px;
    }
    .source-gemini { background: #e0e7ff; color: #3730a3; border: 1px solid #c7d2fe; }
    .source-local { background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================
# 2. DATA LAYER (CSV PERSISTENCE)
# ==========================================

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Default data initializers for fresh checkouts or deployments
DEFAULT_DATA = {
    "semesters.csv": pd.DataFrame([
        {"semester_number": 1, "semester_name": "Semester 1", "status": "Completed", "completed_credits": 20, "total_credits": 20},
        {"semester_number": 2, "semester_name": "Semester 2", "status": "Completed", "completed_credits": 21, "total_credits": 21},
        {"semester_number": 3, "semester_name": "Semester 3", "status": "Completed", "completed_credits": 22, "total_credits": 22},
        {"semester_number": 4, "semester_name": "Semester 4", "status": "In Progress", "completed_credits": 14, "total_credits": 22},
        {"semester_number": 5, "semester_name": "Semester 5", "status": "Not Started", "completed_credits": 0, "total_credits": 21},
        {"semester_number": 6, "semester_name": "Semester 6", "status": "Not Started", "completed_credits": 0, "total_credits": 20},
        {"semester_number": 7, "semester_name": "Semester 7", "status": "Not Started", "completed_credits": 0, "total_credits": 18},
        {"semester_number": 8, "semester_name": "Semester 8", "status": "Not Started", "completed_credits": 0, "total_credits": 16},
    ]),
    "courses.csv": pd.DataFrame([
        {"course_code": "CS201", "course_name": "Data Structures & Algorithms", "semester": 3, "credits": 4, "status": "Completed", "syllabus_topics": "Arrays, Stacks, Queues, Linked Lists, Trees, Graphs, Sorting, Dynamic Programming"},
        {"course_code": "CS202", "course_name": "Computer Organization & Architecture", "semester": 3, "credits": 4, "status": "Completed", "syllabus_topics": "Instruction Sets, ALU, Pipelining, Cache Memory, Multicores"},
        {"course_code": "CS203", "course_name": "Discrete Mathematics", "semester": 3, "credits": 3, "status": "Completed", "syllabus_topics": "Set Theory, Logic, Relations, Graph Theory, Combinatorics"},
        {"course_code": "CS301", "course_name": "Operating Systems", "semester": 4, "credits": 4, "status": "In Progress", "syllabus_topics": "Processes, Threads, CPU Scheduling, Deadlocks, Memory Management, File Systems"},
        {"course_code": "CS302", "course_name": "Database Management Systems", "semester": 4, "credits": 4, "status": "In Progress", "syllabus_topics": "ER Model, Relational Algebra, SQL, Normalization, ACID, Indexing"},
        {"course_code": "CS303", "course_name": "Design & Analysis of Algorithms", "semester": 4, "credits": 4, "status": "In Progress", "syllabus_topics": "Divide & Conquer, Greedy, DP, Backtracking, Branch & Bound, NP-Completeness"},
        {"course_code": "CS304", "course_name": "Software Engineering", "semester": 4, "credits": 3, "status": "In Progress", "syllabus_topics": "SDLC, Agile, Requirement Analysis, Design Patterns, Testing"},
        {"course_code": "CS305", "course_name": "Operating Systems Laboratory", "semester": 4, "credits": 2, "status": "Completed", "syllabus_topics": "Linux Shell Scripts, POSIX System Calls, Thread Synchronization"},
        {"course_code": "CS401", "course_name": "Computer Networks", "semester": 5, "credits": 4, "status": "Not Started", "syllabus_topics": "OSI Reference, TCP/IP, Routing Algorithms, Flow Control, DNS, HTTP"},
        {"course_code": "CS402", "course_name": "Theory of Computation", "semester": 5, "credits": 3, "status": "Not Started", "syllabus_topics": "Automata, Regular Expressions, Context-Free Grammars, Turing Machines"},
    ]),
    "academic_calendar.csv": pd.DataFrame([
        {"date": "2026-03-25", "event_name": "Internal Assessment Test 1", "event_type": "Exam", "description": "Units 1 & 2 for all Sem 4 subjects"},
        {"date": "2026-04-10", "event_name": "Mini-Project Mid-Review", "event_type": "Academic", "description": "Review of architecture and schema definition"},
        {"date": "2026-04-14", "event_name": "Ambedkar Jayanti", "event_type": "Holiday", "description": "University declared holiday"},
        {"date": "2026-05-05", "event_name": "Internal Assessment Test 2", "event_type": "Exam", "description": "Units 3 & 4 evaluation"},
        {"date": "2026-05-25", "event_name": "Semester Practical Examinations", "event_type": "Exam", "description": "Lab assessments by external examiners"},
        {"date": "2026-06-08", "event_name": "End Semester University Theory Exams", "event_type": "Exam", "description": "Semester 4 final theoretical examination"},
    ]),
    "assessments.csv": pd.DataFrame([
        {"assessment_id": "IA1-CS301", "course_code": "CS301", "assessment_type": "Internal Assessment 1", "date": "2026-03-25", "max_marks": 50, "status": "Upcoming"},
        {"assessment_id": "IA1-CS302", "course_code": "CS302", "assessment_type": "Internal Assessment 1", "date": "2026-03-26", "max_marks": 50, "status": "Upcoming"},
        {"assessment_id": "IA1-CS303", "course_code": "CS303", "assessment_type": "Internal Assessment 1", "date": "2026-03-27", "max_marks": 50, "status": "Upcoming"},
        {"assessment_id": "PR-CS304", "course_code": "CS304", "assessment_type": "Agile Sprint Review 1", "date": "2026-04-02", "max_marks": 25, "status": "Upcoming"},
        {"assessment_id": "LAB-CS305", "course_code": "CS305", "assessment_type": "Lab Quiz & Shell Evaluation", "date": "2026-03-10", "max_marks": 25, "status": "Completed"},
    ]),
    "scores.csv": pd.DataFrame([
        {"course_code": "CS201", "assessment_name": "End Semester Examination", "marks_obtained": 88, "max_marks": 100, "semester": 3},
        {"course_code": "CS202", "assessment_name": "End Semester Examination", "marks_obtained": 82, "max_marks": 100, "semester": 3},
        {"course_code": "CS203", "assessment_name": "End Semester Examination", "marks_obtained": 91, "max_marks": 100, "semester": 3},
        {"course_code": "CS305", "assessment_name": "Lab Quiz & Shell Evaluation", "marks_obtained": 23, "max_marks": 25, "semester": 4},
    ]),
    "plan_checklist.csv": pd.DataFrame([
        {"task_id": "TSK-01", "category": "Academic Prep", "task_name": "Solve Process Scheduling Numerical Problems", "target_date": "2026-03-20", "status": "Pending", "notes": "FCFS, SJF, Round Robin with Gantt charts"},
        {"task_id": "TSK-02", "category": "Assignment", "task_name": "Submit DBMS SQL Schema Design", "target_date": "2026-03-22", "status": "Pending", "notes": "Normalize database relations to 3NF/BCNF"},
        {"task_id": "TSK-03", "category": "Project", "task_name": "Streamlit Prototype Setup for Degree OS", "target_date": "2026-03-15", "status": "Completed", "notes": "Setup repository structure and basic routing"},
        {"task_id": "TSK-04", "category": "Self-Study", "task_name": "Review Dynamic Programming Knapsack Variations", "target_date": "2026-03-24", "status": "In Progress", "notes": "0/1 Knapsack, Unbounded Knapsack, Tabulation"},
    ]),
    "university_syllabus.csv": pd.DataFrame([
        {"regulation": "R2022 Autonomous", "branch": "Computer Science & Engineering", "source_url_or_ref": "University Academic Council Ref #AC/2022/CS-Rev3", "status_type": "Verified Academic Framework", "notes": "Standard 160-credit engineering degree template. Curriculum conforms to National Model Syllabus."},
        {"regulation": "R2022 Autonomous", "branch": "Computer Science & Engineering", "source_url_or_ref": "Sample Institutional Template", "status_type": "Sample Data Prototype", "notes": "All internal assessment marks, target dates, and percentages are simulation data for project demonstration."}
    ])
}

def load_data(filename: str) -> pd.DataFrame:
    """Load dataframe from CSV, initializing with defaults if missing."""
    file_path = DATA_DIR / filename
    if not file_path.exists():
        # Fallback to current working directory if present
        root_path = Path(filename)
        if root_path.exists():
            return pd.read_csv(root_path)
        # Create from defaults
        df = DEFAULT_DATA.get(filename, pd.DataFrame())
        df.to_csv(file_path, index=False)
        return df.copy()
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        st.error(f"Error loading {filename}: {e}")
        return DEFAULT_DATA.get(filename, pd.DataFrame()).copy()

def save_data(filename: str, df: pd.DataFrame) -> bool:
    """Save dataframe to CSV in the data directory."""
    try:
        file_path = DATA_DIR / filename
        df.to_csv(file_path, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving {filename}: {e}")
        return False

def get_all_datasets() -> Dict[str, pd.DataFrame]:
    """Retrieve all datasets in a dictionary."""
    return {
        "semesters": load_data("semesters.csv"),
        "courses": load_data("courses.csv"),
        "academic_calendar": load_data("academic_calendar.csv"),
        "assessments": load_data("assessments.csv"),
        "scores": load_data("scores.csv"),
        "plan_checklist": load_data("plan_checklist.csv"),
        "university_syllabus": load_data("university_syllabus.csv"),
    }


# ==========================================
# 3. GEMINI AI GROUNDING & RETRY CLIENT
# ==========================================

def get_gemini_client() -> Optional[object]:
    """Instantiate Google GenAI client securely from Streamlit secrets."""
    if not GENAI_AVAILABLE:
        return None
    api_key = st.secrets.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception:
        return None

def build_grounded_academic_context(data_dict: Dict[str, pd.DataFrame]) -> str:
    """Convert structured academic data into a compact context string."""
    context_sections = []
    
    # 1. Semesters
    sem_lines = []
    for _, row in data_dict["semesters"].iterrows():
        sem_lines.append(f"- Sem {row.get('semester_number')}: {row.get('status')} ({row.get('completed_credits')}/{row.get('total_credits')} credits)")
    context_sections.append("SEMESTER RECORDS:\n" + "\n".join(sem_lines))
    
    # 2. Courses
    crs_lines = []
    for _, row in data_dict["courses"].iterrows():
        crs_lines.append(f"- {row.get('course_code')} ({row.get('course_name')}) [Sem {row.get('semester')}]: {row.get('status')}, Credits: {row.get('credits')}. Topics: {row.get('syllabus_topics')}")
    context_sections.append("COURSES & SYLLABUS TOPICS:\n" + "\n".join(crs_lines))
    
    # 3. Calendar
    cal_lines = []
    for _, row in data_dict["academic_calendar"].iterrows():
        cal_lines.append(f"- {row.get('date')} [{row.get('event_type')}]: {row.get('event_name')} - {row.get('description')}")
    context_sections.append("ACADEMIC & LEAVE CALENDAR:\n" + "\n".join(cal_lines))
    
    # 4. Assessments
    asn_lines = []
    for _, row in data_dict["assessments"].iterrows():
        asn_lines.append(f"- {row.get('course_code')} | {row.get('assessment_type')} | Date: {row.get('date')} | Max: {row.get('max_marks')} | Status: {row.get('status')}")
    context_sections.append("INTERNAL ASSESSMENTS:\n" + "\n".join(asn_lines))
    
    # 5. Scores
    scr_lines = []
    for _, row in data_dict["scores"].iterrows():
        scr_lines.append(f"- {row.get('course_code')} ({row.get('assessment_name')}): {row.get('marks_obtained')}/{row.get('max_marks')} (Sem {row.get('semester')})")
    context_sections.append("RECORDED ASSESSMENT SCORES (PROTOTYPE SAMPLE):\n" + "\n".join(scr_lines))
    
    # 6. Checklist
    chk_lines = []
    for _, row in data_dict["plan_checklist"].iterrows():
        chk_lines.append(f"- [{row.get('status')}] {row.get('task_name')} ({row.get('category')}) Due: {row.get('target_date')}. Notes: {row.get('notes')}")
    context_sections.append("TASKS & CHECKLIST:\n" + "\n".join(chk_lines))

    # 7. University syllabus
    syl_lines = []
    for _, row in data_dict["university_syllabus"].iterrows():
        syl_lines.append(f"- {row.get('regulation')} | {row.get('branch')} | Status: {row.get('status_type')} | Ref: {row.get('source_url_or_ref')}")
    context_sections.append("UNIVERSITY REGULATION / SYLLABUS REFERENCE:\n" + "\n".join(syl_lines))

    return "\n\n".join(context_sections)

def generate_local_rule_based_response(query: str, data_dict: Dict[str, pd.DataFrame]) -> str:
    """Deterministic, grounded local fallback when Gemini is unreachable."""
    q = query.lower()
    
    if "incomplete" in q or "pending" in q:
        if "sem" in q or "semester" in q:
            # find semester number
            for s in range(1, 9):
                if str(s) in q:
                    courses = data_dict["courses"]
                    sem_crs = courses[(courses["semester"] == s) & (courses["status"] != "Completed")]
                    if not sem_crs.empty:
                        items = [f"• **{r['course_code']}**: {r['course_name']} ({r['status']})" for _, r in sem_crs.iterrows()]
                        return f"Incomplete courses in Semester {s} based on Degree OS records:\n\n" + "\n".join(items)
                    return f"All courses recorded for Semester {s} are marked as Completed."
        # Generic pending tasks
        pending_tasks = data_dict["plan_checklist"][data_dict["plan_checklist"]["status"] != "Completed"]
        if not pending_tasks.empty:
            items = [f"• **{r['task_name']}** ({r['category']}) - Due: {r['target_date']}" for _, r in pending_tasks.iterrows()]
            return "Here are your pending checklist tasks from Degree OS:\n\n" + "\n".join(items)

    if "assessment" in q or "exam" in q or "test" in q:
        upcoming_asn = data_dict["assessments"][data_dict["assessments"]["status"] == "Upcoming"]
        if not upcoming_asn.empty:
            first_asn = upcoming_asn.iloc[0]
            crs = data_dict["courses"][data_dict["courses"]["course_code"] == first_asn["course_code"]]
            syllabus = crs.iloc[0]["syllabus_topics"] if not crs.empty else "Refer to course syllabus"
            return (
                f"Your next scheduled assessment is **{first_asn['assessment_type']}** for **{first_asn['course_code']}** "
                f"on **{first_asn['date']}** (Max marks: {first_asn['max_marks']}).\n\n"
                f"**Relevant course topics to prepare:** {syllabus}"
            )

    if "progress" in q or "status" in q or "credits" in q:
        completed_sem = data_dict["semesters"][data_dict["semesters"]["status"] == "Completed"]
        curr_sem = data_dict["semesters"][data_dict["semesters"]["status"] == "In Progress"]
        curr_num = curr_sem.iloc[0]["semester_number"] if not curr_sem.empty else "N/A"
        tot_credits = data_dict["semesters"]["completed_credits"].sum()
        return (
            f"**Academic Progress Summary:**\n"
            f"• Current Active Semester: **Semester {curr_num}**\n"
            f"• Completed Semesters: {len(completed_sem)} of 8\n"
            f"• Verified Sample Credits Earned: **{tot_credits}**\n"
            f"*(Note: All data shown originates from local Degree OS sample datasets.)*"
        )

    if "data structures" in q:
        crs = data_dict["courses"][data_dict["courses"]["course_code"] == "CS201"]
        if not crs.empty:
            return f"**CS201 (Data Structures & Algorithms) topics:**\n{crs.iloc[0]['syllabus_topics']}"

    return "I cannot verify that from the current Degree OS data."

def query_gemini_with_backoff(
    client: object,
    model_name: str,
    system_instruction: str,
    user_prompt: str,
    max_retries: int = 3
) -> Tuple[str, str]:
    """Execute Gemini request with retry on 503 errors and structured grounding."""
    backoff = 1.5
    for attempt in range(max_retries):
        try:
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2,
            )
            response = client.models.generate_content(
                model=model_name,
                contents=user_prompt,
                config=config,
            )
            if response and response.text:
                return response.text.strip(), "Gemini AI"
            return "I cannot verify that from the current Degree OS data.", "Gemini AI"
        except APIError as e:
            err_str = str(e)
            # Detect 503 or transient overload
            if "503" in err_str or getattr(e, "code", None) == 503:
                if attempt < max_retries - 1:
                    time.sleep(backoff * (2 ** attempt))
                    continue
                return (
                    f"Gemini service is currently overloaded (503). Retried {max_retries} times.",
                    "Error"
                )
            # Quota or auth issue
            if "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
                return "Gemini API quota exceeded for your project key. Switched to safe mode.", "Error"
            if "API_KEY_INVALID" in err_str or "invalid" in err_str.lower():
                return "The configured GEMINI_API_KEY is invalid. Please check your secrets.", "Error"
            return f"Gemini API request error: {err_str}", "Error"
        except Exception as e:
            return f"Unexpected connection error: {str(e)}", "Error"

    return "I cannot verify that from the current Degree OS data.", "Local Fallback"


# ==========================================
# 4. SHARED UI HELPER COMPONENTS
# ==========================================

def render_section_header(title: str, subtitle: str, badge_text: Optional[str] = None):
    """Render consistent header across all 11 sections."""
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown(f"### {title}")
        st.markdown(f"<p style='color: #64748b; margin-top:-0.5rem; margin-bottom:1rem;'>{subtitle}</p>", unsafe_allow_html=True)
    with col2:
        if badge_text:
            st.markdown(f"<div style='text-align: right;'><span class='badge badge-progress'>{badge_text}</span></div>", unsafe_allow_html=True)
    st.markdown("---")

def get_status_badge(status: str) -> str:
    """Format status with CSS badge."""
    s = str(status).strip()
    if s == "Completed":
        return f"<span class='badge badge-completed'>{s}</span>"
    elif s in ["In Progress", "Upcoming"]:
        return f"<span class='badge badge-progress'>{s}</span>"
    elif s in ["Urgent", "Overdue"]:
        return f"<span class='badge badge-urgent'>{s}</span>"
    return f"<span class='badge badge-pending'>{s}</span>"


# ==========================================
# 5. NAVIGATION SECTIONS (1 to 11)
# ==========================================

datasets = get_all_datasets()

# Sidebar Navigation
with st.sidebar:
    st.markdown("## 🎓 Degree OS")
    st.caption("Engineering Academic Operating System")
    st.markdown("---")
    
    sections = [
        "1. Dashboard",
        "2. Semesters 1–8",
        "3. Courses & Syllabus",
        "4. University Syllabus",
        "5. Academic / Leave Calendar",
        "6. Internal Assessments",
        "7. Status Tracker",
        "8. Scorecard",
        "9. Plan & Checklist",
        "10. Ask Degree AI",
        "11. Data Admin",
    ]
    
    selected_section = st.radio("Navigation", sections, index=0)
    
    st.markdown("---")
    st.markdown("#### ⚙️ AI Engine Status")
    configured_key = st.secrets.get("GEMINI_API_KEY", "")
    if GENAI_AVAILABLE and configured_key:
        st.success("Gemini API: Ready")
    elif not GENAI_AVAILABLE:
        st.warning("google-genai SDK not installed")
    else:
        st.info("API Key not set in secrets.toml (Fallback active)")
        
    st.caption("Engineering Degree OS • v2.5 Demonstration")


# ----------------------------------------------------
# 1. DASHBOARD
# ----------------------------------------------------
if selected_section == "1. Dashboard":
    render_section_header("Academic Dashboard", "Real-time summary of degree progress, credits, and immediate priorities", "Semester 4 Active")
    
    # Metric cards calculations
    sem_df = datasets["semesters"]
    courses_df = datasets["courses"]
    scores_df = datasets["scores"]
    assessments_df = datasets["assessments"]
    cal_df = datasets["academic_calendar"]
    checklist_df = datasets["plan_checklist"]
    
    total_completed_credits = sem_df["completed_credits"].sum()
    total_degree_credits = sem_df["total_credits"].sum()
    progress_pct = int((total_completed_credits / total_degree_credits) * 100) if total_degree_credits else 0
    
    # Calculate prototype aggregate percentage
    if not scores_df.empty and "marks_obtained" in scores_df.columns and "max_marks" in scores_df.columns:
        valid_scores = scores_df[scores_df["max_marks"] > 0]
        obtained = valid_scores["marks_obtained"].sum()
        maximum = valid_scores["max_marks"].sum()
        proto_score_pct = f"{((obtained / maximum) * 100):.1f}%" if maximum > 0 else "N/A"
    else:
        proto_score_pct = "N/A"

    # Identify Next Assessment
    upcoming_asn = assessments_df[assessments_df["status"] == "Upcoming"]
    next_asn_str = f"{upcoming_asn.iloc[0]['course_code']} ({upcoming_asn.iloc[0]['date']})" if not upcoming_asn.empty else "None scheduled"

    # Identify Next Event
    next_event_str = f"{cal_df.iloc[0]['event_name']} ({cal_df.iloc[0]['date']})" if not cal_df.empty else "No upcoming events"

    # Render Top 4 KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(
            f"""<div class='metric-card'>
                <div class='metric-label'>Current Degree Progress</div>
                <div class='metric-value'>{progress_pct}%</div>
                <div class='metric-sub'>{total_completed_credits} of {total_degree_credits} verified credits</div>
            </div>""",
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""<div class='metric-card'>
                <div class='metric-label'>Active Semester</div>
                <div class='metric-value'>Semester 4</div>
                <div class='metric-sub'>Computer Science & Eng.</div>
            </div>""",
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f"""<div class='metric-card'>
                <div class='metric-label'>Sample Score Avg.</div>
                <div class='metric-value'>{proto_score_pct}</div>
                <div class='metric-sub'>*Prototype test average (Not CGPA)</div>
            </div>""",
            unsafe_allow_html=True
        )
    with col4:
        st.markdown(
            f"""<div class='metric-card'>
                <div class='metric-label'>Next Milestone</div>
                <div class='metric-value' style='font-size: 1.25rem;'>{upcoming_asn.iloc[0]['course_code'] if not upcoming_asn.empty else 'None'}</div>
                <div class='metric-sub'>{next_asn_str}</div>
            </div>""",
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Progress visual and upcoming tasks
    c_left, c_right = st.columns([3, 2])
    
    with c_left:
        st.markdown("#### 📊 Semester-by-Semester Credit Distribution")
        chart_data = sem_df.set_index("semester_name")[["completed_credits", "total_credits"]]
        st.bar_chart(chart_data, color=["#0284c7", "#cbd5e1"])
        
        st.markdown("#### 📅 Next Academic Events & Assessments")
        st.dataframe(
            cal_df.head(4)[["date", "event_type", "event_name", "description"]],
            use_container_width=True,
            hide_index=True
        )

    with c_right:
        st.markdown("#### ⚡ Priority Checklist Tasks")
        pending_tasks = checklist_df[checklist_df["status"] != "Completed"].head(5)
        if not pending_tasks.empty:
            for _, task in pending_tasks.iterrows():
                st.markdown(
                    f"""<div class='os-card' style='padding: 0.8rem; margin-bottom: 0.5rem;'>
                        <div style='display:flex; justify-content:space-between; align-items:center;'>
                            <strong>{task['task_name']}</strong>
                            {get_status_badge(task['status'])}
                        </div>
                        <div style='font-size:0.8rem; color:#64748b; margin-top:4px;'>
                            Category: {task['category']} | Target: {task['target_date']}
                        </div>
                    </div>""",
                    unsafe_allow_html=True
                )
        else:
            st.info("All priority checklist tasks are completed.")


# ----------------------------------------------------
# 2. SEMESTERS 1–8
# ----------------------------------------------------
elif selected_section == "2. Semesters 1–8":
    render_section_header("Semesters 1–8", "Comprehensive 8-semester curriculum breakdown, status, and credit completion")
    
    sem_df = datasets["semesters"]
    courses_df = datasets["courses"]
    
    cols = st.columns(4)
    for idx, row in sem_df.iterrows():
        col = cols[idx % 4]
        with col:
            s_num = int(row["semester_number"])
            s_courses = courses_df[courses_df["semester"] == s_num]
            comp_credits = int(row["completed_credits"])
            tot_credits = int(row["total_credits"])
            pct = int((comp_credits / tot_credits) * 100) if tot_credits else 0
            
            st.markdown(
                f"""<div class='os-card'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div class='os-card-header'>{row['semester_name']}</div>
                        {get_status_badge(row['status'])}
                    </div>
                    <div style='font-size: 0.85rem; color: #475569; margin-bottom: 0.5rem;'>
                        Courses Enrolled: <strong>{len(s_courses)}</strong>
                    </div>
                    <div style='font-size: 0.85rem; color: #475569;'>
                        Credits: <strong>{comp_credits} / {tot_credits}</strong> ({pct}%)
                    </div>
                </div>""",
                unsafe_allow_html=True
            )
            st.progress(pct / 100)
            st.markdown("<div style='margin-bottom: 1.2rem;'></div>", unsafe_allow_html=True)


# ----------------------------------------------------
# 3. COURSES & SYLLABUS
# ----------------------------------------------------
elif selected_section == "3. Courses & Syllabus":
    render_section_header("Courses & Syllabus", "Detailed modular topic breakdown for each curriculum course")
    
    courses_df = datasets["courses"]
    
    filter_col1, filter_col2 = st.columns([1, 2])
    with filter_col1:
        sem_list = sorted(courses_df["semester"].unique().tolist())
        chosen_sem = st.selectbox("Select Semester", ["All"] + sem_list, index=0)
    with filter_col2:
        search_query = st.text_input("Search Course Code, Title, or Topic keyword", "")

    filtered_courses = courses_df.copy()
    if chosen_sem != "All":
        filtered_courses = filtered_courses[filtered_courses["semester"] == chosen_sem]
    if search_query.strip():
        q = search_query.lower()
        filtered_courses = filtered_courses[
            filtered_courses["course_code"].str.lower().str.contains(q) |
            filtered_courses["course_name"].str.lower().str.contains(q) |
            filtered_courses["syllabus_topics"].str.lower().str.contains(q)
        ]

    st.markdown(f"**Showing {len(filtered_courses)} course(s)**")

    for _, c in filtered_courses.iterrows():
        with st.expander(f"{c['course_code']} - {c['course_name']} (Semester {c['semester']} | {c['credits']} Credits)"):
            c1, c2 = st.columns([3, 1])
            with c1:
                st.markdown("**Syllabus & Core Modules:**")
                topics = [t.strip() for t in str(c['syllabus_topics']).split(",") if t.strip()]
                for t in topics:
                    st.markdown(f"• {t}")
            with c2:
                st.markdown(f"**Status:** {get_status_badge(c['status'])}", unsafe_allow_html=True)
                st.markdown(f"**Course Code:** `{c['course_code']}`")
                st.markdown(f"**Credits Assigned:** {c['credits']}")


# ----------------------------------------------------
# 4. UNIVERSITY SYLLABUS
# ----------------------------------------------------
elif selected_section == "4. University Syllabus":
    render_section_header("University Syllabus & Governance", "Statutory syllabus framework, regulations, and source references")
    
    st.info("ℹ️ **Verification Standard:** Information marked 'Verified Academic Framework' follows standard institutional regulation norms. All student tracking data represents a prototype simulation.")
    
    syl_df = datasets["university_syllabus"]
    st.dataframe(syl_df, use_container_width=True, hide_index=True)
    
    st.markdown("#### Regulation Highlights")
    st.markdown(
        """
        - **Curriculum Model:** Autonomous Outcome-Based Education (OBE) system.
        - **Minimum Degree Credits:** 160 credits required across 8 semesters.
        - **Grading Disclaimer:** Grade Point Averages (SGPA/CGPA) are governed solely by official University Controller of Examinations grade cards. Prototype percentage aggregates inside Degree OS are diagnostic tools only.
        """
    )


# ----------------------------------------------------
# 5. ACADEMIC / LEAVE CALENDAR
# ----------------------------------------------------
elif selected_section == "5. Academic / Leave Calendar":
    render_section_header("Academic & Leave Calendar", "Institutional schedules, internal assessments, milestones, and holidays")
    
    cal_df = datasets["academic_calendar"].copy()
    
    col_filter, col_metrics = st.columns([1, 2])
    with col_filter:
        event_types = ["All"] + sorted(cal_df["event_type"].unique().tolist())
        selected_type = st.selectbox("Filter Event Type", event_types)
    
    if selected_type != "All":
        cal_df = cal_df[cal_df["event_type"] == selected_type]
        
    st.dataframe(cal_df, use_container_width=True, hide_index=True)


# ----------------------------------------------------
# 6. INTERNAL ASSESSMENTS
# ----------------------------------------------------
elif selected_section == "6. Internal Assessments":
    render_section_header("Internal Assessments", "Continuous internal evaluations, target dates, and preparation checklists")
    
    asn_df = datasets["assessments"].copy()
    
    col1, col2 = st.columns(2)
    upcoming_count = len(asn_df[asn_df["status"] == "Upcoming"])
    completed_count = len(asn_df[asn_df["status"] == "Completed"])
    with col1:
        st.markdown(
            f"""<div class='metric-card'>
                <div class='metric-label'>Upcoming Assessments</div>
                <div class='metric-value'>{upcoming_count}</div>
            </div>""", unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""<div class='metric-card'>
                <div class='metric-label'>Completed Assessments</div>
                <div class='metric-value'>{completed_count}</div>
            </div>""", unsafe_allow_html=True
        )
        
    st.markdown("#### Scheduled Assessment Timeline")
    st.dataframe(asn_df, use_container_width=True, hide_index=True)


# ----------------------------------------------------
# 7. STATUS TRACKER
# ----------------------------------------------------
elif selected_section == "7. Status Tracker":
    render_section_header("Status Tracker", "Detailed catalog of completed, in-progress, and pending courses")
    
    crs_df = datasets["courses"]
    
    t_comp, t_prog, t_pend = st.tabs(["Completed Courses", "In Progress Courses", "Not Started"])
    
    with t_comp:
        comp_df = crs_df[crs_df["status"] == "Completed"]
        st.dataframe(comp_df[["course_code", "course_name", "semester", "credits"]], use_container_width=True, hide_index=True)
    with t_prog:
        prog_df = crs_df[crs_df["status"] == "In Progress"]
        st.dataframe(prog_df[["course_code", "course_name", "semester", "credits", "syllabus_topics"]], use_container_width=True, hide_index=True)
    with t_pend:
        pend_df = crs_df[crs_df["status"] == "Not Started"]
        st.dataframe(pend_df[["course_code", "course_name", "semester", "credits"]], use_container_width=True, hide_index=True)


# ----------------------------------------------------
# 8. SCORECARD
# ----------------------------------------------------
elif selected_section == "8. Scorecard":
    render_section_header("Scorecard", "Sample performance marks records and diagnostic distributions")
    
    st.warning("⚠️ **Important Evaluation Policy:** The percentage shown below is an internal prototype assessment score for demonstration and planning purposes. It does not constitute an official university SGPA/CGPA transcript.")
    
    scores_df = datasets["scores"].copy()
    if not scores_df.empty:
        scores_df["percentage"] = ((scores_df["marks_obtained"] / scores_df["max_marks"]) * 100).round(1)
        
        c1, c2 = st.columns([2, 1])
        with c1:
            st.dataframe(scores_df, use_container_width=True, hide_index=True)
        with c2:
            st.markdown("#### Score Proportions")
            st.bar_chart(scores_df.set_index("course_code")["percentage"], color="#0284c7")
    else:
        st.info("No recorded score records available.")


# ----------------------------------------------------
# 9. PLAN & CHECKLIST
# ----------------------------------------------------
elif selected_section == "9. Plan & Checklist":
    render_section_header("Plan & Checklist", "Interactive task management, study milestones, and deliverable targets")
    
    chk_df = datasets["plan_checklist"]
    
    st.markdown("Edit your tasks directly in the interactive table below. Click **Save Checklist Changes** to persist your edits to CSV.")
    
    edited_df = st.data_editor(
        chk_df,
        num_rows="dynamic",
        use_container_width=True,
        key="checklist_editor"
    )
    
    if st.button("💾 Save Checklist Changes", type="primary"):
        if save_data("plan_checklist.csv", edited_df):
            st.success("Checklist saved successfully!")
            datasets["plan_checklist"] = edited_df


# ----------------------------------------------------
# 10. ASK DEGREE AI
# ----------------------------------------------------
elif selected_section == "10. Ask Degree AI":
    render_section_header("Ask Degree AI", "Grounded academic assistant powered by your Degree OS data and Gemini")
    
    # Model configuration selector (per requirement 2)
    with st.expander("🛠️ Assistant Engine Configuration", expanded=False):
        c_mod, c_info = st.columns([2, 3])
        with c_mod:
            # gemini-2.5-flash is current high-speed model
            chosen_model = st.selectbox(
                "Configured Gemini Model",
                ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-1.5-flash"],
                index=0
            )
        with c_info:
            api_key_configured = bool(st.secrets.get("GEMINI_API_KEY", "").strip())
            if api_key_configured and GENAI_AVAILABLE:
                st.success("Google GenAI client active with authenticated secret key.")
            elif not GENAI_AVAILABLE:
                st.error("google-genai library is missing. Run: pip install google-genai")
            else:
                st.warning("GEMINI_API_KEY secret not found. Local grounded fallback is serving answers.")

    # Initialize session state chat history
    if "degree_ai_messages" not in st.session_state:
        st.session_state["degree_ai_messages"] = [
            {
                "role": "assistant",
                "content": "Hello! I am Degree AI, your academic assistant for Engineering Degree OS. Ask me about your courses, syllabus modules, next assessments, pending checklist tasks, or semester progress.",
                "source": "Degree OS System"
            }
        ]

    # Sample query prompts for convenience
    st.markdown("**Suggested questions:**")
    prompt_cols = st.columns(3)
    sample_q1 = "Which courses are incomplete in Semester 4?"
    sample_q2 = "What is my next assessment and what should I prepare?"
    sample_q3 = "What topics are included in Data Structures?"
    
    suggested_clicked = None
    if prompt_cols[0].button(f"📌 {sample_q1}", use_container_width=True):
        suggested_clicked = sample_q1
    if prompt_cols[1].button(f"📌 {sample_q2}", use_container_width=True):
        suggested_clicked = sample_q2
    if prompt_cols[2].button(f"📌 {sample_q3}", use_container_width=True):
        suggested_clicked = sample_q3

    # Display chat conversation history
    for msg in st.session_state["degree_ai_messages"]:
        with st.chat_message(msg["role"]):
            if msg.get("source") and msg["role"] == "assistant":
                badge_class = "source-gemini" if "Gemini" in msg["source"] else "source-local"
                st.markdown(f"<span class='source-tag {badge_class}'>Source: {msg['source']}</span>", unsafe_allow_html=True)
            st.markdown(msg["content"])

    # Chat Input handler
    user_input = st.chat_input("Ask a question about your academic degree data...")
    if suggested_clicked:
        user_input = suggested_clicked

    if user_input:
        # Display user message
        st.session_state["degree_ai_messages"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Build grounded system instruction
        system_context = build_grounded_academic_context(datasets)
        system_instruction = f"""
You are the embedded AI academic advisor inside the application 'Engineering Degree OS'.

SAFETY & GROUNDING CONSTRAINTS:
1. You must answer questions ONLY using the verified context from the application's loaded CSV data provided below.
2. If the user asks about something not present in the data, or requires unverified personal academic records, answer EXACTLY:
   "I cannot verify that from the current Degree OS data."
3. Do not invent university rules, regulations, exam dates, credits, CGPA formulas, or eligibility criteria.
4. Clearly identify sample data as sample data when discussing marks or assessments.
5. Do not present prototype percentages as official SGPA or CGPA.
6. Maintain an encouraging, concise, and structured tone suitable for an engineering student.

CURRENT DEGREE OS ACADEMIC CONTEXT:
{system_context}
"""

        # Response Generation with fallback
        with st.chat_message("assistant"):
            gemini_client = get_gemini_client()
            
            if gemini_client:
                with st.spinner("Analyzing Degree OS records via Gemini..."):
                    answer_text, source_tag = query_gemini_with_backoff(
                        client=gemini_client,
                        model_name=chosen_model,
                        system_instruction=system_instruction,
                        user_prompt=user_input
                    )
                    # If error occurred with Gemini, fall back smoothly to local parser
                    if source_tag == "Error":
                        st.caption("Gemini unavailable, executing grounded local analysis...")
                        answer_text = generate_local_rule_based_response(user_input, datasets)
                        source_tag = "Local CSV Grounded Fallback"
            else:
                with st.spinner("Analyzing Degree OS records locally..."):
                    answer_text = generate_local_rule_based_response(user_input, datasets)
                    source_tag = "Local CSV Grounded Fallback"

            badge_class = "source-gemini" if "Gemini" in source_tag else "source-local"
            st.markdown(f"<span class='source-tag {badge_class}'>Source: {source_tag}</span>", unsafe_allow_html=True)
            st.markdown(answer_text)

            # Store in session state
            st.session_state["degree_ai_messages"].append({
                "role": "assistant",
                "content": answer_text,
                "source": source_tag
            })


# ----------------------------------------------------
# 11. DATA ADMIN
# ----------------------------------------------------
elif selected_section == "11. Data Admin":
    render_section_header("Data Admin", "Direct management and editing of all foundational CSV datasets")
    
    st.markdown("Select any table to view or edit raw records. Modifications persist immediately to the application CSV storage.")
    
    table_choice = st.selectbox(
        "Select Table to Administer",
        [
            "semesters.csv",
            "courses.csv",
            "academic_calendar.csv",
            "assessments.csv",
            "scores.csv",
            "plan_checklist.csv",
            "university_syllabus.csv",
        ]
    )
    
    curr_df = load_data(table_choice)
    
    edited_data = st.data_editor(
        curr_df,
        num_rows="dynamic",
        use_container_width=True,
        key=f"admin_editor_{table_choice}"
    )
    
    col_save, col_reload = st.columns([1, 4])
    with col_save:
        if st.button(f"💾 Save {table_choice}", type="primary"):
            if save_data(table_choice, edited_data):
                st.success(f"{table_choice} saved successfully!")
                # Refresh local in-memory dataset
                key_name = table_choice.replace(".csv", "")
                datasets[key_name] = edited_data
    with col_reload:
        if st.button("🔄 Reload from Disk"):
            st.rerun()