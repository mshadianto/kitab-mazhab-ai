"""
🕌 KITAB IMAM MAZHAB AI - INTERACTIVE LEARNING PLATFORM
Super engaging learning experience with gamification
"""

import os
import sys
import json
import random
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st

# Set secrets before imports
if hasattr(st, 'secrets'):
    for key in ['GROQ_API_KEY', 'WAHA_API_URL', 'WAHA_SESSION', 'WAHA_API_KEY']:
        if key in st.secrets:
            os.environ[key] = st.secrets[key]

from dotenv import load_dotenv
load_dotenv()

# Page config
st.set_page_config(
    page_title="Kitab Imam Mazhab AI",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CUSTOM CSS - MODERN UI
# =====================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Poppins:wght@300;400;500;600;700&display=swap');
    
    :root {
        --primary: #1e5128;
        --secondary: #4e9f3d;
        --accent: #d8e9a8;
        --gold: #ffd700;
        --dark: #191a19;
    }
    
    .stApp {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Header Styles */
    .hero-header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 50%, #2d6a4f 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(30, 81, 40, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .hero-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: shimmer 3s infinite linear;
    }
    
    @keyframes shimmer {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .hero-header h1 {
        font-family: 'Amiri', serif;
        font-size: 2.8rem;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        position: relative;
    }
    
    .hero-header .arabic {
        font-family: 'Amiri', serif;
        font-size: 1.6rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    
    /* Stats Cards */
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: transform 0.3s ease;
        margin-bottom: 0.5rem;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
    }
    
    .stat-card.gold {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    .stat-card.green {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    
    .stat-card.orange {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
    }
    
    .stat-label {
        font-size: 0.85rem;
        opacity: 0.9;
    }
    
    /* Mazhab Cards */
    .mazhab-card {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        cursor: pointer;
        border: 3px solid transparent;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .mazhab-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.2);
    }
    
    .mazhab-card.hanafi { border-color: #4caf50; background: linear-gradient(135deg, #f8fff8 0%, #e8f5e9 100%); }
    .mazhab-card.maliki { border-color: #ff9800; background: linear-gradient(135deg, #fffaf0 0%, #fff3e0 100%); }
    .mazhab-card.syafii { border-color: #2196f3; background: linear-gradient(135deg, #f0f8ff 0%, #e3f2fd 100%); }
    .mazhab-card.hanbali { border-color: #9c27b0; background: linear-gradient(135deg, #faf0ff 0%, #f3e5f5 100%); }
    
    .mazhab-icon {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    
    .mazhab-card h3 {
        margin: 0;
        color: var(--dark);
        font-size: 1.2rem;
    }
    
    .mazhab-card .imam {
        color: #666;
        font-size: 0.85rem;
        margin-top: 0.3rem;
    }
    
    .followers-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.7rem;
        display: inline-block;
        margin-top: 0.8rem;
    }
    
    /* Chat Messages */
    .chat-message {
        padding: 1rem 1.5rem;
        border-radius: 20px;
        margin: 0.8rem 0;
        animation: slideIn 0.3s ease;
        line-height: 1.6;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 20%;
        border-bottom-right-radius: 5px;
    }
    
    .bot-message {
        background: white;
        color: #333;
        border: 1px solid #e0e0e0;
        margin-right: 20%;
        border-bottom-left-radius: 5px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* Quiz Styles */
    .quiz-card {
        background: linear-gradient(135deg, #1e5128 0%, #4e9f3d 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 30px rgba(30, 81, 40, 0.3);
    }
    
    .quiz-question {
        font-size: 1.2rem;
        margin-bottom: 1rem;
        line-height: 1.6;
    }
    
    .quiz-meta {
        display: flex;
        justify-content: space-between;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* Achievement Badge */
    .achievement {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: linear-gradient(135deg, #ffd700 0%, #ffaa00 100%);
        color: #333;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        box-shadow: 0 3px 10px rgba(255, 215, 0, 0.4);
        margin: 0.2rem;
    }
    
    /* Progress Bar */
    .progress-container {
        background: #e0e0e0;
        border-radius: 10px;
        height: 12px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #4caf50, #8bc34a);
        border-radius: 10px;
        transition: width 0.5s ease;
    }
    
    /* Daily Challenge */
    .daily-challenge {
        background: linear-gradient(135deg, #ff6b6b 0%, #feca57 100%);
        padding: 1.2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 1rem;
        position: relative;
        overflow: hidden;
    }
    
    .daily-challenge h4 {
        margin: 0 0 0.5rem 0;
    }
    
    .daily-challenge p {
        margin: 0;
        font-size: 0.9rem;
        opacity: 0.95;
    }
    
    /* Level Badge */
    .level-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.8rem 1.5rem;
        border-radius: 25px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        font-size: 0.9rem;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #666;
        font-size: 0.9rem;
        margin-top: 2rem;
        border-top: 1px solid #eee;
    }
    
    .footer .arabic-quote {
        font-family: 'Amiri', serif;
        font-size: 1.2rem;
        color: var(--primary);
        margin-bottom: 0.5rem;
    }
    
    /* Comparison Table */
    .comparison-table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
        font-size: 0.9rem;
    }
    
    .comparison-table th {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        color: white;
        padding: 0.8rem;
        text-align: left;
    }
    
    .comparison-table td {
        padding: 0.8rem;
        border-bottom: 1px solid #eee;
    }
    
    .comparison-table tr:hover {
        background: #f5f5f5;
    }
    
    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Mode buttons */
    .stButton > button {
        border-radius: 10px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# DATA
# =====================================================
QUIZ_DATA = [
    {
        "question": "Siapakah pendiri Mazhab Hanafi?",
        "options": ["Imam Malik", "Imam Abu Hanifah", "Imam Syafi'i", "Imam Ahmad bin Hanbal"],
        "correct": 1,
        "explanation": "Imam Abu Hanifah Nu'man bin Tsabit (80-150 H) adalah pendiri Mazhab Hanafi, mazhab fiqih tertua.",
        "difficulty": "easy",
        "points": 10
    },
    {
        "question": "Mazhab mana yang paling banyak dianut di Indonesia?",
        "options": ["Hanafi", "Maliki", "Syafi'i", "Hanbali"],
        "correct": 2,
        "explanation": "Mazhab Syafi'i adalah mazhab mayoritas di Indonesia, Malaysia, dan Asia Tenggara.",
        "difficulty": "easy",
        "points": 10
    },
    {
        "question": "Berapa jumlah rukun wudhu menurut Mazhab Syafi'i?",
        "options": ["4 rukun", "5 rukun", "6 rukun", "7 rukun"],
        "correct": 2,
        "explanation": "Mazhab Syafi'i menetapkan 6 rukun wudhu: niat, membasuh wajah, membasuh tangan, mengusap kepala, membasuh kaki, dan tertib.",
        "difficulty": "medium",
        "points": 20
    },
    {
        "question": "Apa kitab fiqih utama dalam Mazhab Maliki?",
        "options": ["Al-Umm", "Al-Muwaththa'", "Al-Hidayah", "Al-Mughni"],
        "correct": 1,
        "explanation": "Al-Muwaththa' adalah kitab karya Imam Malik yang menjadi rujukan utama Mazhab Maliki.",
        "difficulty": "medium",
        "points": 20
    },
    {
        "question": "Dalam Mazhab Hanafi, bagaimana posisi tangan saat shalat?",
        "options": ["Di dada", "Di bawah pusar", "Dilepas di samping", "Di atas pusar"],
        "correct": 1,
        "explanation": "Mazhab Hanafi menganjurkan meletakkan tangan di bawah pusar saat shalat.",
        "difficulty": "medium",
        "points": 20
    },
    {
        "question": "Siapa murid Imam Syafi'i yang menjadi pendiri mazhab tersendiri?",
        "options": ["Imam Bukhari", "Imam Ahmad bin Hanbal", "Imam Muslim", "Imam Nasa'i"],
        "correct": 1,
        "explanation": "Imam Ahmad bin Hanbal adalah murid Imam Syafi'i yang kemudian mendirikan Mazhab Hanbali.",
        "difficulty": "hard",
        "points": 30
    },
    {
        "question": "Apa gelar yang diberikan kepada Imam Malik?",
        "options": ["Al-Imam Al-A'zham", "Nashir al-Sunnah", "Imam Dar al-Hijrah", "Imam Ahl al-Sunnah"],
        "correct": 2,
        "explanation": "Imam Malik diberi gelar 'Imam Dar al-Hijrah' (Imam Negeri Hijrah) karena beliau tidak pernah meninggalkan Madinah.",
        "difficulty": "hard",
        "points": 30
    },
    {
        "question": "Menurut Mazhab Syafi'i, apakah bersentuhan kulit dengan lawan jenis membatalkan wudhu?",
        "options": ["Tidak membatalkan", "Membatalkan secara mutlak", "Membatalkan jika dengan syahwat", "Makruh saja"],
        "correct": 1,
        "explanation": "Dalam Mazhab Syafi'i, bersentuhan kulit dengan lawan jenis (bukan mahram) membatalkan wudhu secara mutlak.",
        "difficulty": "hard",
        "points": 30
    },
    {
        "question": "Di negara mana Mazhab Hanbali paling dominan?",
        "options": ["Indonesia", "Mesir", "Arab Saudi", "Turki"],
        "correct": 2,
        "explanation": "Mazhab Hanbali adalah mazhab resmi di Arab Saudi dan dominan di wilayah Teluk.",
        "difficulty": "easy",
        "points": 10
    },
    {
        "question": "Apa nama kitab ushul fiqih pertama yang disusun secara sistematis?",
        "options": ["Al-Umm", "Al-Risalah", "Al-Muwaththa'", "Al-Musnad"],
        "correct": 1,
        "explanation": "Al-Risalah karya Imam Syafi'i adalah kitab ushul fiqih pertama yang disusun secara sistematis.",
        "difficulty": "hard",
        "points": 30
    }
]

ACHIEVEMENTS = {
    "first_question": {"name": "Penanya Pertama", "icon": "🌟", "desc": "Ajukan pertanyaan pertama"},
    "quiz_master": {"name": "Master Quiz", "icon": "🏆", "desc": "Jawab 5 quiz dengan benar"},
    "explorer": {"name": "Penjelajah", "icon": "🧭", "desc": "Pelajari semua 4 mazhab"},
    "scholar": {"name": "Cendekiawan", "icon": "📚", "desc": "Raih 100 poin"},
    "streak_3": {"name": "Konsisten", "icon": "🔥", "desc": "3 hari streak"},
    "perfect_quiz": {"name": "Sempurna", "icon": "💯", "desc": "5 quiz benar berturut"}
}

MAZHAB_INFO = {
    "hanafi": {"name": "Mazhab Hanafi", "imam": "Imam Abu Hanifah", "icon": "🟢", "color": "#4caf50", "followers": "~500 juta", "regions": "Turki, Pakistan, India"},
    "maliki": {"name": "Mazhab Maliki", "imam": "Imam Malik", "icon": "🟡", "color": "#ff9800", "followers": "~350 juta", "regions": "Afrika Utara & Barat"},
    "syafii": {"name": "Mazhab Syafi'i", "imam": "Imam Syafi'i", "icon": "🔵", "color": "#2196f3", "followers": "~500 juta", "regions": "Indonesia, Malaysia, Mesir"},
    "hanbali": {"name": "Mazhab Hanbali", "imam": "Imam Ahmad", "icon": "🟣", "color": "#9c27b0", "followers": "~50 juta", "regions": "Arab Saudi, Qatar"}
}

# =====================================================
# HELPER FUNCTIONS
# =====================================================
def init_session_state():
    defaults = {
        "messages": [], "chat_history": [], "agent_initialized": False,
        "points": 0, "level": 1, "quiz_correct": 0, "quiz_total": 0,
        "achievements": [], "mazhab_explored": [], "current_mode": "chat",
        "streak": 1, "last_visit": datetime.now().strftime("%Y-%m-%d"),
        "quiz_index": 0, "quiz_answered": False, "daily_challenge_done": False,
        "questions_asked": 0, "pending_question": None, "consecutive_correct": 0
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    today = datetime.now().strftime("%Y-%m-%d")
    if st.session_state.last_visit != today:
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        if st.session_state.last_visit == yesterday:
            st.session_state.streak += 1
            if st.session_state.streak >= 3 and "streak_3" not in st.session_state.achievements:
                st.session_state.achievements.append("streak_3")
        else:
            st.session_state.streak = 1
        st.session_state.last_visit = today
        st.session_state.daily_challenge_done = False


def add_points(points):
    st.session_state.points += points
    new_level = (st.session_state.points // 100) + 1
    if new_level > st.session_state.level:
        st.session_state.level = new_level
        st.balloons()
    if st.session_state.points >= 100 and "scholar" not in st.session_state.achievements:
        st.session_state.achievements.append("scholar")


def check_achievements():
    if len(st.session_state.mazhab_explored) >= 4 and "explorer" not in st.session_state.achievements:
        st.session_state.achievements.append("explorer")
    if st.session_state.quiz_correct >= 5 and "quiz_master" not in st.session_state.achievements:
        st.session_state.achievements.append("quiz_master")
    if st.session_state.consecutive_correct >= 5 and "perfect_quiz" not in st.session_state.achievements:
        st.session_state.achievements.append("perfect_quiz")


def get_level_title(level):
    titles = {1: "Mubtadi'", 2: "Talib", 3: "Muta'allim", 4: "Fadhil", 5: "Alim", 6: "Faqih", 7: "Mufti", 8: "Mujtahid", 9: "Imam", 10: "Syaikhul Islam"}
    return titles.get(level, f"Level {level}")


@st.cache_resource
def initialize_rag():
    from core.rag_engine import KitabMazhabRAG
    rag = KitabMazhabRAG()
    kb_path = Path(__file__).parent / "data" / "knowledge_base" / "kitab_mazhab.json"
    if kb_path.exists():
        rag.load_knowledge_base(str(kb_path))
    return rag


@st.cache_resource  
def initialize_agent():
    from core.agent import KitabMazhabAgent
    return KitabMazhabAgent()


def get_response(agent, message, history):
    try:
        response = agent.process_message(message, history)
        return response.answer
    except Exception as e:
        return f"Maaf, terjadi kesalahan: {str(e)}"


# =====================================================
# UI COMPONENTS
# =====================================================
def render_header():
    st.markdown("""
    <div class="hero-header">
        <h1>🕌 Kitab Imam Mazhab AI</h1>
        <p class="arabic">بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيم</p>
        <p>Platform Pembelajaran Fiqih Interaktif</p>
    </div>
    """, unsafe_allow_html=True)


def render_stats():
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{st.session_state.points}</div><div class="stat-label">⭐ Poin</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card gold"><div class="stat-number">{st.session_state.level}</div><div class="stat-label">📈 Level</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card green"><div class="stat-number">{st.session_state.streak}🔥</div><div class="stat-label">Streak</div></div>', unsafe_allow_html=True)
    with c4:
        acc = (st.session_state.quiz_correct / max(st.session_state.quiz_total, 1)) * 100
        st.markdown(f'<div class="stat-card orange"><div class="stat-number">{acc:.0f}%</div><div class="stat-label">📊 Akurasi</div></div>', unsafe_allow_html=True)


def render_sidebar():
    st.markdown(f'<div class="level-badge">⭐ {get_level_title(st.session_state.level)}</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("### 🏆 Achievements")
    if st.session_state.achievements:
        for ach_id in st.session_state.achievements:
            if ach_id in ACHIEVEMENTS:
                ach = ACHIEVEMENTS[ach_id]
                st.markdown(f'<div class="achievement">{ach["icon"]} {ach["name"]}</div>', unsafe_allow_html=True)
    else:
        st.info("Mulai belajar untuk unlock! 🎯")
    
    st.markdown("---")
    st.markdown("### 📊 Progress")
    
    quiz_pct = min(st.session_state.quiz_correct / 5 * 100, 100)
    st.markdown(f"Quiz Master ({st.session_state.quiz_correct}/5)")
    st.markdown(f'<div class="progress-container"><div class="progress-bar" style="width:{quiz_pct}%"></div></div>', unsafe_allow_html=True)
    
    points_pct = st.session_state.points % 100
    st.markdown(f"Next Level ({points_pct}/100)")
    st.markdown(f'<div class="progress-container"><div class="progress-bar" style="width:{points_pct}%"></div></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(f"""
    ### 📈 Stats
    - 💬 Pertanyaan: {st.session_state.questions_asked}
    - 🧠 Quiz: {st.session_state.quiz_total}
    - 📚 Mazhab: {len(st.session_state.mazhab_explored)}/4
    """)


def render_chat_mode():
    st.markdown("### 💬 Tanya Jawab Fiqih")
    
    if not os.getenv('GROQ_API_KEY') or os.getenv('GROQ_API_KEY') == 'your_groq_api_key_here':
        st.error("⚠️ GROQ_API_KEY belum dikonfigurasi!")
        st.info("Tambahkan di Settings → Secrets:\n```\nGROQ_API_KEY = \"gsk_xxx\"\n```")
        return
    
    if not st.session_state.agent_initialized:
        with st.spinner("🔄 Memuat AI..."):
            try:
                initialize_rag()
                st.session_state.agent = initialize_agent()
                st.session_state.agent_initialized = True
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                return
    
    # Quick questions
    st.markdown("##### 💡 Pertanyaan Cepat")
    qc = st.columns(3)
    quick_q = ["Siapa Imam Syafi'i?", "Rukun wudhu Hanafi?", "Beda posisi tangan shalat"]
    for i, q in enumerate(quick_q):
        with qc[i]:
            if st.button(f"📝 {q}", key=f"q_{i}", use_container_width=True):
                st.session_state.pending_question = q
    
    st.markdown("---")
    
    # Chat display
    if not st.session_state.messages:
        st.markdown("""
        <div class="chat-message bot-message">
            <strong>🤖 Assalamu'alaikum!</strong><br>
            Saya siap membantu mempelajari fiqih empat mazhab. Silakan bertanya! 🤲
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.messages[-8:]:
            css = "user-message" if msg["role"] == "user" else "bot-message"
            icon = "👤" if msg["role"] == "user" else "🤖"
            content = msg["content"].replace('\n', '<br>')
            st.markdown(f'<div class="chat-message {css}"><strong>{icon}</strong> {content}</div>', unsafe_allow_html=True)
    
    # Handle pending question
    if st.session_state.pending_question:
        q = st.session_state.pending_question
        st.session_state.pending_question = None
        process_question(q)
    
    # Input
    user_input = st.chat_input("Ketik pertanyaan...")
    if user_input:
        process_question(user_input)


def process_question(question):
    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.chat_history.append({"role": "user", "content": question})
    st.session_state.questions_asked += 1
    
    if st.session_state.questions_asked == 1 and "first_question" not in st.session_state.achievements:
        st.session_state.achievements.append("first_question")
    
    with st.spinner("🤔 Berpikir..."):
        response = get_response(st.session_state.agent, question, st.session_state.chat_history)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    add_points(5)
    check_achievements()
    st.rerun()


def render_quiz_mode():
    st.markdown("### 🧠 Quiz Fiqih")
    
    if not st.session_state.daily_challenge_done:
        st.markdown("""
        <div class="daily-challenge">
            <h4>🎯 Tantangan Harian</h4>
            <p>Jawab 3 quiz benar untuk +50 bonus poin!</p>
        </div>
        """, unsafe_allow_html=True)
    
    quiz = QUIZ_DATA[st.session_state.quiz_index % len(QUIZ_DATA)]
    diff_icon = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}
    
    st.markdown(f"""
    <div class="quiz-card">
        <div class="quiz-meta">
            <span>{diff_icon[quiz['difficulty']]} {quiz['difficulty'].upper()}</span>
            <span>💎 {quiz['points']} poin</span>
        </div>
        <div class="quiz-question">{quiz['question']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.quiz_answered:
        for i, opt in enumerate(quiz['options']):
            if st.button(f"{chr(65+i)}. {opt}", key=f"opt_{i}", use_container_width=True):
                st.session_state.quiz_answered = True
                st.session_state.quiz_total += 1
                
                if i == quiz['correct']:
                    st.session_state.quiz_correct += 1
                    st.session_state.consecutive_correct += 1
                    add_points(quiz['points'])
                    st.success(f"✅ Benar! +{quiz['points']} poin")
                    
                    if st.session_state.quiz_correct % 3 == 0 and not st.session_state.daily_challenge_done:
                        st.session_state.daily_challenge_done = True
                        add_points(50)
                        st.balloons()
                        st.success("🎉 Tantangan Harian Selesai! +50 poin!")
                else:
                    st.session_state.consecutive_correct = 0
                    st.error(f"❌ Salah! Jawaban: {quiz['options'][quiz['correct']]}")
                
                st.info(f"📖 {quiz['explanation']}")
                check_achievements()
                st.rerun()
    else:
        if st.button("➡️ Lanjut", use_container_width=True):
            st.session_state.quiz_index += 1
            st.session_state.quiz_answered = False
            st.rerun()
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    c1.metric("✅ Benar", st.session_state.quiz_correct)
    c2.metric("📊 Total", st.session_state.quiz_total)


def render_explore_mode():
    st.markdown("### 📚 Jelajahi Empat Mazhab")
    
    cols = st.columns(2)
    for i, (key, info) in enumerate(MAZHAB_INFO.items()):
        with cols[i % 2]:
            check = "✅" if key in st.session_state.mazhab_explored else ""
            st.markdown(f"""
            <div class="mazhab-card {key}">
                <div class="mazhab-icon">{info['icon']}</div>
                <h3>{info['name']} {check}</h3>
                <p class="imam">{info['imam']}</p>
                <div class="followers-badge">👥 {info['followers']}</div>
                <p style="font-size:0.75rem; color:#888; margin-top:0.5rem;">📍 {info['regions']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Pelajari {info['name']}", key=f"ex_{key}", use_container_width=True):
                if key not in st.session_state.mazhab_explored:
                    st.session_state.mazhab_explored.append(key)
                    add_points(15)
                st.session_state.pending_question = f"Jelaskan tentang {info['name']} dan {info['imam']}"
                st.session_state.current_mode = "chat"
                check_achievements()
                st.rerun()


def render_compare_mode():
    st.markdown("### ⚖️ Perbandingan Mazhab")
    
    topics = ["Posisi tangan shalat", "Usap kepala wudhu", "Basmalah & amin", "Qunut subuh", "Batalnya wudhu"]
    
    cols = st.columns(2)
    for i, t in enumerate(topics):
        with cols[i % 2]:
            if st.button(f"⚖️ {t}", key=f"cmp_{i}", use_container_width=True):
                st.session_state.pending_question = f"Bandingkan {t.lower()} menurut empat mazhab"
                st.session_state.current_mode = "chat"
                add_points(10)
                st.rerun()
    
    st.markdown("---")
    st.markdown("#### 📊 Ringkasan Perbandingan")
    
    st.markdown("""
    | Aspek | Hanafi | Maliki | Syafi'i | Hanbali |
    |-------|--------|--------|---------|---------|
    | Tangan Shalat | Bawah pusar | Dilepas | Di dada | Di dada |
    | Usap Kepala | 1/4 | Seluruh | Sebagian | Seluruh |
    | Basmalah | Pelan | Tidak | Keras | Pelan |
    | Qunut Subuh | Tidak | Sunnah | Sunnah | Tidak |
    """)


# =====================================================
# MAIN
# =====================================================
def main():
    init_session_state()
    check_achievements()
    
    with st.sidebar:
        render_sidebar()
        st.markdown("---")
        if st.button("🔄 Reset", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()
    
    render_header()
    render_stats()
    
    st.markdown("### 🎯 Mode Belajar")
    m1, m2, m3, m4 = st.columns(4)
    
    modes = [("chat", "💬 Tanya Jawab", m1), ("quiz", "🧠 Quiz", m2), ("explore", "📚 Jelajah", m3), ("compare", "⚖️ Bandingkan", m4)]
    for mode_id, label, col in modes:
        with col:
            btn_type = "primary" if st.session_state.current_mode == mode_id else "secondary"
            if st.button(label, key=f"m_{mode_id}", use_container_width=True, type=btn_type):
                st.session_state.current_mode = mode_id
                st.rerun()
    
    st.markdown("---")
    
    if st.session_state.current_mode == "chat":
        render_chat_mode()
    elif st.session_state.current_mode == "quiz":
        render_quiz_mode()
    elif st.session_state.current_mode == "explore":
        render_explore_mode()
    else:
        render_compare_mode()
    
    st.markdown("""
    <div class="footer">
        <p class="arabic-quote">مَنْ يُرِدِ اللَّهُ بِهِ خَيْرًا يُفَقِّهْهُ فِي الدِّينِ</p>
        <p>"Barangsiapa dikehendaki Allah kebaikan, maka Allah pahamkan dalam agama"</p>
        <p>🕌 Kitab Imam Mazhab AI v2.0</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()