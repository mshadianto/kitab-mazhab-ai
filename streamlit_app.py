"""
Kitab Imam Mazhab RAG AI - Streamlit Web App
Akses langsung via browser tanpa perlu WhatsApp
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from dotenv import load_dotenv

# Load environment variables
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
        padding: 1rem;
        background: linear-gradient(135deg, #1e5128 0%, #4e9f3d 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .bot-message {
        background-color: #f1f8e9;
        border-left: 4px solid #4caf50;
    }
    .mazhab-card {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem;
        text-align: center;
    }
    .stButton > button {
        width: 100%;
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


def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🕌 Kitab Imam Mazhab AI</h1>
        <p>Asisten Pembelajaran Fiqih Empat Mazhab</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/c4/Al-Fatihah.svg/200px-Al-Fatihah.svg.png", width=100)
        
        st.markdown("### 📚 Empat Mazhab")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🟢 Hanafi", use_container_width=True):
                st.session_state.selected_mazhab = "Hanafi"
            if st.button("🔵 Syafi'i", use_container_width=True):
                st.session_state.selected_mazhab = "Syafi'i"
        with col2:
            if st.button("🟡 Maliki", use_container_width=True):
                st.session_state.selected_mazhab = "Maliki"
            if st.button("🟣 Hanbali", use_container_width=True):
                st.session_state.selected_mazhab = "Hanbali"
        
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
        
        if st.button("🔄 Reset Percakapan", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chat_history = []
            st.rerun()
        
        st.markdown("---")
        st.markdown("""
        ### ℹ️ Tentang
        
        Aplikasi ini menggunakan:
        - **RAG** (Retrieval-Augmented Generation)
        - **Groq Llama 3.3 70B**
        - **ChromaDB** Vector Store
        
        Dibuat untuk memudahkan umat mempelajari ilmu fiqih empat mazhab.
        """)
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "agent_initialized" not in st.session_state:
        st.session_state.agent_initialized = False
    
    # Initialize agent
    if not st.session_state.agent_initialized:
        with st.spinner("🔄 Memuat sistem AI..."):
            try:
                initialize_rag()
                st.session_state.agent = initialize_agent()
                st.session_state.agent_initialized = True
            except Exception as e:
                st.error(f"❌ Gagal memuat AI: {str(e)}")
                st.info("Pastikan GROQ_API_KEY sudah diset di file .env")
                return
    
    # Main chat area
    st.markdown("### 💬 Tanya Jawab")
    
    # Display chat messages
    chat_container = st.container()
    
    with chat_container:
        if not st.session_state.messages:
            # Welcome message
            st.markdown("""
            <div class="chat-message bot-message">
                <strong>🤖 Asisten:</strong><br><br>
                Assalamu'alaikum warahmatullahi wabarakatuh 🙏<br><br>
                Saya adalah <strong>Asisten Kitab Imam Mazhab</strong>, siap membantu Anda mempelajari empat mazhab fiqih Islam:<br><br>
                📚 <strong>Mazhab Hanafi</strong> - Imam Abu Hanifah<br>
                📚 <strong>Mazhab Maliki</strong> - Imam Malik<br>
                📚 <strong>Mazhab Syafi'i</strong> - Imam Syafi'i<br>
                📚 <strong>Mazhab Hanbali</strong> - Imam Ahmad bin Hanbal<br><br>
                Silakan ajukan pertanyaan Anda! 🤲
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
                    st.markdown(f"""
                    <div class="chat-message bot-message">
                        <strong>🤖 Asisten:</strong><br>{msg["content"]}
                    </div>
                    """, unsafe_allow_html=True)
    
    # Check for pending question from sidebar
    if "pending_question" in st.session_state and st.session_state.pending_question:
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
    
    col1, col2 = st.columns([6, 1])
    
    with col1:
        user_input = st.text_input(
            "Ketik pertanyaan Anda:",
            key="user_input",
            placeholder="Contoh: Siapa Imam Syafi'i?",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("Kirim 📤", use_container_width=True)
    
    # Process input
    if send_button and user_input:
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
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <p>
            "Barangsiapa yang dikehendaki Allah kebaikan padanya, maka Allah akan memahamkannya dalam urusan agama."<br>
            <em>(HR. Bukhari & Muslim)</em>
        </p>
        <p>🕌 Kitab Imam Mazhab AI - Dibuat dengan ❤️ untuk kemudahan umat</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()