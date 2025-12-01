"""
Kitab Imam Mazhab RAG AI - Streamlit Web App
Akses langsung via browser tanpa perlu WhatsApp
Supports Streamlit Cloud secrets
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st

# Set environment variables from Streamlit secrets BEFORE importing other modules
if hasattr(st, 'secrets'):
    if 'GROQ_API_KEY' in st.secrets:
        os.environ['GROQ_API_KEY'] = st.secrets['GROQ_API_KEY']
    if 'WAHA_API_URL' in st.secrets:
        os.environ['WAHA_API_URL'] = st.secrets['WAHA_API_URL']
    if 'WAHA_SESSION' in st.secrets:
        os.environ['WAHA_SESSION'] = st.secrets['WAHA_SESSION']
    if 'WAHA_API_KEY' in st.secrets:
        os.environ['WAHA_API_KEY'] = st.secrets['WAHA_API_KEY']

# Load from .env if available (local development)
from dotenv import load_dotenv
load_dotenv()

# Page config
st.set_page_config(
    page_title="Kitab Imam Mazhab AI",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, #1e5128 0%, #4e9f3d 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
    }
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        line-height: 1.6;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .bot-message {
        background-color: #f1f8e9;
        border-left: 4px solid #4caf50;
    }
    .stButton > button {
        width: 100%;
        border-radius: 8px;
    }
    .example-btn {
        font-size: 0.85rem;
    }
    .footer {
        text-align: center;
        color: #666;
        font-size: 0.9rem;
        padding: 1rem;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def initialize_rag():
    """Initialize RAG engine (cached)"""
    from core.rag_engine import KitabMazhabRAG
    
    rag = KitabMazhabRAG()
    kb_path = Path(__file__).parent / "data" / "knowledge_base" / "kitab_mazhab.json"
    
    if kb_path.exists():
        rag.load_knowledge_base(str(kb_path))
    
    return rag


@st.cache_resource
def initialize_agent():
    """Initialize AI agent (cached)"""
    from core.agent import KitabMazhabAgent
    return KitabMazhabAgent()


def get_response(agent, message: str, history: list) -> str:
    """Get response from agent"""
    try:
        response = agent.process_message(message, history)
        return response.answer
    except Exception as e:
        return f"Maaf, terjadi kesalahan: {str(e)}"


def check_api_key():
    """Check if GROQ_API_KEY is configured"""
    api_key = os.getenv('GROQ_API_KEY', '')
    if not api_key or api_key == 'your_groq_api_key_here':
        return False
    return True


def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🕌 Kitab Imam Mazhab AI</h1>
        <p>Asisten Pembelajaran Fiqih Empat Mazhab</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check API key
    if not check_api_key():
        st.error("⚠️ GROQ_API_KEY belum dikonfigurasi!")
        st.info("""
        **Untuk Streamlit Cloud:**
        1. Buka Settings → Secrets
        2. Tambahkan:
        ```
        GROQ_API_KEY = "gsk_xxxxxxxxxxxx"
        ```
        
        **Untuk Local:**
        1. Buat file `.env`
        2. Tambahkan: `GROQ_API_KEY=gsk_xxxxxxxxxxxx`
        
        Dapatkan API key di [console.groq.com](https://console.groq.com)
        """)
        return
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 📚 Empat Mazhab")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🟢 Hanafi", use_container_width=True):
                st.session_state.pending_question = "Jelaskan tentang mazhab Hanafi dan Imam Abu Hanifah"
            if st.button("🔵 Syafi'i", use_container_width=True):
                st.session_state.pending_question = "Jelaskan tentang mazhab Syafi'i dan Imam Syafi'i"
        with col2:
            if st.button("🟡 Maliki", use_container_width=True):
                st.session_state.pending_question = "Jelaskan tentang mazhab Maliki dan Imam Malik"
            if st.button("🟣 Hanbali", use_container_width=True):
                st.session_state.pending_question = "Jelaskan tentang mazhab Hanbali dan Imam Ahmad bin Hanbal"
        
        st.markdown("---")
        
        st.markdown("### 💡 Contoh Pertanyaan")
        
        example_questions = [
            "Siapa pendiri mazhab Syafi'i?",
            "Rukun wudhu menurut Hanafi?",
            "Perbedaan posisi tangan shalat",
            "Kitab rujukan mazhab Maliki",
            "Apa yang membatalkan puasa?",
            "Rukun nikah dalam Islam"
        ]
        
        for q in example_questions:
            if st.button(f"📝 {q}", key=f"ex_{q}", use_container_width=True):
                st.session_state.pending_question = q
        
        st.markdown("---")
        
        if st.button("🔄 Reset Percakapan", type="secondary", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chat_history = []
            st.rerun()
        
        st.markdown("---")
        st.markdown("""
        ### ℹ️ Tentang
        
        Aplikasi ini menggunakan:
        - 🧠 **RAG** (Retrieval-Augmented Generation)
        - 🦙 **Groq Llama 3.3 70B**
        - 📊 **ChromaDB** Vector Store
        
        Dibuat untuk memudahkan umat mempelajari ilmu fiqih empat mazhab.
        """)
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "agent_initialized" not in st.session_state:
        st.session_state.agent_initialized = False
    
    if "pending_question" not in st.session_state:
        st.session_state.pending_question = None
    
    # Initialize agent
    if not st.session_state.agent_initialized:
        with st.spinner("🔄 Memuat sistem AI... (pertama kali mungkin agak lama)"):
            try:
                initialize_rag()
                st.session_state.agent = initialize_agent()
                st.session_state.agent_initialized = True
                st.success("✅ Sistem AI siap!")
            except Exception as e:
                st.error(f"❌ Gagal memuat AI: {str(e)}")
                st.info("Pastikan GROQ_API_KEY sudah benar di Secrets")
                return
    
    # Main chat area
    st.markdown("### 💬 Tanya Jawab Fiqih")
    
    # Display chat messages
    chat_container = st.container()
    
    with chat_container:
        if not st.session_state.messages:
            # Welcome message
            st.markdown("""
            <div class="chat-message bot-message">
                <strong>🤖 Asisten:</strong><br><br>
                <strong>Assalamu'alaikum warahmatullahi wabarakatuh</strong> 🙏<br><br>
                Saya adalah <strong>Asisten Kitab Imam Mazhab</strong>, siap membantu Anda mempelajari empat mazhab fiqih Islam:<br><br>
                📚 <strong>Mazhab Hanafi</strong> - Imam Abu Hanifah<br>
                📚 <strong>Mazhab Maliki</strong> - Imam Malik<br>
                📚 <strong>Mazhab Syafi'i</strong> - Imam Syafi'i<br>
                📚 <strong>Mazhab Hanbali</strong> - Imam Ahmad bin Hanbal<br><br>
                <em>Silakan ajukan pertanyaan Anda atau pilih contoh di sidebar! 🤲</em>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>👤 Anda:</strong><br>{msg["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Format response with proper line breaks
                    content = msg["content"].replace('\n', '<br>')
                    st.markdown(f"""
                    <div class="chat-message bot-message">
                        <strong>🤖 Asisten:</strong><br>{content}
                    </div>
                    """, unsafe_allow_html=True)
    
    # Check for pending question from sidebar
    if st.session_state.pending_question:
        question = st.session_state.pending_question
        st.session_state.pending_question = None
        
        # Add to messages
        st.session_state.messages.append({"role": "user", "content": question})
        st.session_state.chat_history.append({"role": "user", "content": question})
        
        # Get response
        with st.spinner("🤔 Sedang berpikir..."):
            response = get_response(
                st.session_state.agent,
                question,
                st.session_state.chat_history
            )
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        st.rerun()
    
    # Chat input
    st.markdown("---")
    
    # Use chat_input for better UX
    user_input = st.chat_input("Ketik pertanyaan Anda di sini...")
    
    # Process input
    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Get response
        with st.spinner("🤔 Sedang berpikir..."):
            response = get_response(
                st.session_state.agent,
                user_input,
                st.session_state.chat_history
            )
        
        # Add assistant message
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        st.rerun()
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>
            "Barangsiapa yang dikehendaki Allah kebaikan padanya,<br>
            maka Allah akan memahamkannya dalam urusan agama."<br>
            <em>(HR. Bukhari & Muslim)</em>
        </p>
        <p>🕌 Kitab Imam Mazhab AI - Dibuat dengan ❤️ untuk kemudahan umat</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()