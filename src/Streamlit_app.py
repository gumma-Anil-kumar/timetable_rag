import os
import streamlit as st
from timetable_rag import TimetableRAG

# =====================================================
# PAGE CONFIG — must be first Streamlit call
# =====================================================

st.set_page_config(
    page_title="AI Timetable Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =====================================================
# LOAD & INDEX RAG (cached — runs only once)
# =====================================================

@st.cache_resource
def load_rag():
    rag = TimetableRAG()

    # Only index if not already indexed
    teacher_count   = rag.teacher_collection.count()
    timetable_count = rag.timetable_collection.count()

    if teacher_count == 0 or timetable_count == 0:
        rag.load_timetable_json("../data/cse_timetable.json")
        rag.load_timetable_json("../data/ece_timetable.json")
        rag.load_timetable_json("../data/eee_timetable.json")
        rag.load_timetable_json("../data/mech_timetable.json")
        rag.extract_teachers_from_pdf("../data/teacher_biodata.pdf")
        rag.index_teachers()
        rag.index_timetables()

    return rag

rag = load_rag()

# =====================================================
# CSS
# =====================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; }

.stApp { background: #0b1a2e !important; color: #e8e4dc !important; }

section[data-testid="stSidebar"] {
    background: #0d1f38 !important;
    border-right: 1px solid rgba(201,168,76,0.2) !important;
}
section[data-testid="stSidebar"] * { color: #e8e4dc !important; }

.main-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(1.8rem, 4vw, 2.8rem);
    font-weight: 700;
    background: linear-gradient(135deg, #e8c97a, #c9a84c, #fff6dd);
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center; margin-bottom: 0.3rem;
}
.college-badge {
    text-align: center; display: block;
    font-size: 11px; letter-spacing: 0.12em; text-transform: uppercase;
    color: #e8c97a; margin-bottom: 0.5rem;
}
.subtitle { text-align: center; color: #8a9ab8; font-size: 0.95rem; margin-bottom: 1rem; }
.gold-line {
    width: 70px; height: 2px;
    background: linear-gradient(90deg, transparent, #c9a84c, transparent);
    margin: 0 auto 1.2rem;
}
.stats-row {
    display: flex; justify-content: center; gap: 10px;
    flex-wrap: wrap; margin-bottom: 1.2rem;
}
.stat-pill {
    background: #122040; border: 1px solid rgba(201,168,76,0.2);
    border-radius: 10px; padding: 8px 16px; font-size: 12px;
    color: #e8e4dc; display: inline-flex; align-items: center; gap: 8px;
}
.stat-label { color: #8a9ab8; font-size: 10px; }
.stat-val   { font-weight: 500; }
.live-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: #22c55e; display: inline-block; margin-right: 4px;
}

/* Chat bubbles */
.user-msg {
    background: linear-gradient(135deg, #1a2e52, #1e3566);
    border: 1px solid rgba(201,168,76,0.25);
    border-radius: 14px 14px 4px 14px;
    padding: 12px 16px; margin: 6px 0 6px 15%;
    color: #e8e4dc; font-size: 14px; line-height: 1.6;
}
.bot-msg {
    background: #122040;
    border: 1px solid rgba(201,168,76,0.15);
    border-radius: 14px 14px 14px 4px;
    padding: 12px 16px; margin: 6px 15% 6px 0;
    color: #e8e4dc; font-size: 14px; line-height: 1.7;
    white-space: pre-wrap;
}
.msg-label { font-size: 10px; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 3px; }
.user-label { color: #c9a84c; text-align: right; }
.bot-label  { color: #8a9ab8; }

.chat-container {
    background: #0f2040; border: 1px solid rgba(201,168,76,0.18);
    border-radius: 16px; padding: 16px;
    min-height: 380px; max-height: 500px; overflow-y: auto;
    margin-bottom: 1rem;
}
.empty-chat { text-align: center; padding: 4rem 1rem; color: #4a5a72; }
.empty-icon { font-size: 3rem; margin-bottom: 1rem; }
.empty-title { color: #c9a84c; font-size: 1rem; margin-bottom: 0.4rem; }
.empty-sub   { font-size: 0.8rem; }

/* Input */
.stTextInput > div > div > input {
    background: #0f2040 !important;
    border: 1px solid rgba(201,168,76,0.25) !important;
    border-radius: 12px !important;
    color: #e8e4dc !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
}
.stTextInput > div > div > input:focus {
    border-color: #c9a84c !important;
    box-shadow: 0 0 0 3px rgba(201,168,76,0.1) !important;
}

/* All buttons gold by default */
.stButton > button {
    background: linear-gradient(135deg, #c9a84c, #e8c97a) !important;
    border: none !important; border-radius: 10px !important;
    color: #0b1a2e !important; font-weight: 600 !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(201,168,76,0.35) !important;
}

/* Sidebar buttons — dark style */
div[data-testid="stSidebar"] .stButton > button {
    background: #122040 !important;
    border: 1px solid rgba(201,168,76,0.2) !important;
    border-radius: 8px !important; color: #8a9ab8 !important;
    font-weight: 400 !important; font-size: 12px !important;
    text-align: left !important; margin-bottom: 3px !important;
    transform: none !important; box-shadow: none !important;
}
div[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(201,168,76,0.1) !important;
    color: #e8c97a !important;
    border-color: #c9a84c !important;
    transform: none !important; box-shadow: none !important;
}

.sb-section {
    font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase;
    color: #c9a84c; padding: 8px 0 6px;
    border-bottom: 1px solid rgba(201,168,76,0.15); margin-bottom: 8px;
}

.footer {
    text-align: center; color: #4a5a72; font-size: 11px;
    letter-spacing: 0.04em; padding: 1rem 0;
    border-top: 1px solid rgba(201,168,76,0.1); margin-top: 1rem;
}

#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }
div[data-testid="stDecoration"] { display: none; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# SESSION STATE
# =====================================================

if "history" not in st.session_state:
    st.session_state.history = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = ""

# =====================================================
# SIDEBAR
# =====================================================

QUICK = [
    ("📋", "Who teaches DBMS?"),
    ("👨‍🏫", "Who is class incharge of ECE-A?"),
    ("📅", "Which is scheduled for CSE-A Monday period 1?"),
    ("🔍", "Give me Dr. Sanjay Pillai timetable"),
    ("👥", "What is the strength of CSE-A?"),
    ("🕐", "Who is free on Monday period 3?"),
    ("📍", "Who is teaching ECE-A Monday period 1?"),
    ("📧", "All teacher details with emails"),
]

with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding:1rem 0 0.8rem;'>
        <div style='font-size:2.5rem'>🎓</div>
        <div style='font-family:Playfair Display,serif; font-size:1.1rem; font-weight:700;
                    background:linear-gradient(135deg,#e8c97a,#c9a84c);
                    -webkit-background-clip:text; background-clip:text;
                    -webkit-text-fill-color:transparent;'>
            Timetable Assistant
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sb-section">⚡ Quick Questions</div>', unsafe_allow_html=True)

    for icon, q in QUICK:
        if st.button(f"{icon}  {q}", key=f"sb_{q}"):
            st.session_state.pending_question = q
            st.rerun()

    st.markdown('<div class="sb-section" style="margin-top:1rem">📚 Data Sources</div>', unsafe_allow_html=True)
    try:
        tc = rag.teacher_collection.count()
        tt = rag.timetable_collection.count()
        st.markdown(f"""
        <div style="font-size:11px; color:#8a9ab8; line-height:2">
            👨‍🏫 Teachers indexed: <b style="color:#e8c97a">{tc}</b><br>
            📅 Timetable entries: <b style="color:#e8c97a">{tt}</b><br>
            🤖 LLM: <b style="color:#e8c97a">Groq Llama 3.1</b><br>
            🗄️ Vector DB: <b style="color:#e8c97a">ChromaDB</b><br>
            <span class="live-dot"></span> Status: <span style="color:#22c55e">Online</span>
        </div>
        """, unsafe_allow_html=True)
    except:
        pass

# =====================================================
# MAIN AREA
# =====================================================

st.markdown('<span class="college-badge">⬡ Sri Venkateswara College of Engineering & Technology</span>', unsafe_allow_html=True)
st.markdown('<h1 class="main-title">🎓 AI Timetable Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Ask questions about timetables, teachers, rooms, sections and schedules</p>', unsafe_allow_html=True)
st.markdown('<div class="gold-line"></div>', unsafe_allow_html=True)

st.markdown("""
<div class="stats-row">
    <div class="stat-pill">📅 <div><div class="stat-label">Data</div><div class="stat-val">Timetable RAG</div></div></div>
    <div class="stat-pill">🔍 <div><div class="stat-label">Search</div><div class="stat-val">Semantic + ChromaDB</div></div></div>
    <div class="stat-pill">🤖 <div><div class="stat-label">LLM</div><div class="stat-val">Groq Llama 3.1</div></div></div>
    <div class="stat-pill"><span class="live-dot"></span><div><div class="stat-label">Status</div><div class="stat-val">Online</div></div></div>
</div>
""", unsafe_allow_html=True)

# ── Chat history ──────────────────────────────────────
chat_html = '<div class="chat-container">'

if not st.session_state.history:
    chat_html += """
    <div class="empty-chat">
        <div class="empty-icon">🎓</div>
        <div class="empty-title">Ready to answer your questions</div>
        <div class="empty-sub">Ask about teachers, classes, schedules or rooms<br>or click a quick question on the left</div>
    </div>
    """
else:
    for role, content in st.session_state.history:
        if role == "user":
            chat_html += f'<div class="msg-label user-label">You</div><div class="user-msg">{content}</div>'
        else:
            safe = content.replace("<", "&lt;").replace(">", "&gt;")
            chat_html += f'<div class="msg-label bot-label">🤖 Assistant</div><div class="bot-msg">{safe}</div>'

chat_html += "</div>"
st.markdown(chat_html, unsafe_allow_html=True)

# ── Input row ─────────────────────────────────────────
col1, col2, col3 = st.columns([7, 1, 1])

with col1:
    user_input = st.text_input(
        label="Question",
        placeholder="Ask your timetable question...",
        value=st.session_state.pending_question,
        key="chat_input",
        label_visibility="collapsed",
    )

with col2:
    send = st.button("Send ↗", use_container_width=True)

with col3:
    if st.button("🗑 Clear", use_container_width=True):
        st.session_state.history = []
        st.session_state.pending_question = ""
        st.rerun()

# ── Handle send ───────────────────────────────────────
question = user_input.strip() if user_input else ""

if (send and question) or (st.session_state.pending_question and not send):
    # Clear pending so it doesn't re-fire
    st.session_state.pending_question = ""

    if question:
        with st.spinner("🔍 Searching timetable data..."):
            try:
                answer = rag.ask(question)
            except Exception as e:
                answer = f"⚠️ Error: {str(e)}"

        st.session_state.history.append(("user", question))
        st.session_state.history.append(("assistant", answer))
        st.rerun()

# ── Footer ────────────────────────────────────────────
st.markdown("""
<div class="footer">
    AI Timetable Assistant &nbsp;·&nbsp; Powered by RAG + Groq Llama 3.1 &nbsp;·&nbsp; SVCET
</div>
""", unsafe_allow_html=True)