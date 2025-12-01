#!/usr/bin/env python
"""
Setup script untuk Kitab Imam Mazhab RAG AI
Jalankan script ini untuk inisialisasi awal sistem
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check Python version"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"❌ Python 3.10+ required. You have {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    dirs = [
        "data/knowledge_base",
        "data/chroma_db",
        "logs"
    ]
    
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {d}")


def setup_env():
    """Setup environment file"""
    print("\n⚙️ Setting up environment...")
    
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        print("  ⚠️ .env file already exists")
        return True
    
    if env_example.exists():
        import shutil
        shutil.copy(env_example, env_file)
        print("  ✅ Created .env from .env.example")
        print("  ⚠️ Please edit .env and add your API keys!")
        return True
    
    print("  ❌ .env.example not found")
    return False


def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"
        ])
        print("  ✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Error installing dependencies: {e}")
        return False


def initialize_rag():
    """Initialize RAG engine with knowledge base"""
    print("\n🧠 Initializing RAG engine...")
    
    try:
        from core.rag_engine import KitabMazhabRAG
        
        rag = KitabMazhabRAG()
        
        kb_path = Path("data/knowledge_base/kitab_mazhab.json")
        if kb_path.exists():
            doc_count = rag.load_knowledge_base(str(kb_path))
            print(f"  ✅ Loaded {doc_count} documents into vector store")
            return True
        else:
            print(f"  ⚠️ Knowledge base not found at {kb_path}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error initializing RAG: {e}")
        return False


def test_groq_connection():
    """Test Groq API connection"""
    print("\n🔌 Testing Groq API connection...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        print("  ⚠️ GROQ_API_KEY not configured in .env")
        return False
    
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        
        # Simple test
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Assalamualaikum"}],
            max_tokens=50
        )
        
        print("  ✅ Groq API connection successful")
        return True
        
    except Exception as e:
        print(f"  ❌ Groq API error: {e}")
        return False


def test_waha_connection():
    """Test WAHA API connection"""
    print("\n📱 Testing WAHA connection...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_url = os.getenv("WAHA_API_URL")
    if not api_url:
        print("  ⚠️ WAHA_API_URL not configured in .env")
        return False
    
    try:
        from integrations.waha_client import WAHAClient
        client = WAHAClient()
        sessions = client.get_sessions()
        
        print(f"  ✅ WAHA connection successful")
        print(f"  📋 Found {len(sessions)} session(s):")
        for s in sessions:
            status_emoji = "🟢" if s.status == "WORKING" else "🔴"
            print(f"      {status_emoji} {s.name}: {s.status}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ WAHA connection error: {e}")
        return False


def print_summary(results: dict):
    """Print setup summary"""
    print("\n" + "="*50)
    print("📊 SETUP SUMMARY")
    print("="*50)
    
    for step, success in results.items():
        emoji = "✅" if success else "❌"
        print(f"  {emoji} {step}")
    
    all_success = all(results.values())
    
    print("\n" + "="*50)
    if all_success:
        print("🎉 Setup completed successfully!")
        print("\nTo start the server, run:")
        print("  python app.py")
        print("\nOr for development:")
        print("  python app.py --debug")
    else:
        print("⚠️ Some steps failed. Please check the errors above.")
        print("\nCommon fixes:")
        print("  1. Make sure .env file has correct API keys")
        print("  2. Check internet connection for API tests")
        print("  3. Ensure WAHA server is running")
    print("="*50)


def main():
    """Main setup function"""
    print("="*50)
    print("🕌 KITAB IMAM MAZHAB RAG AI - SETUP")
    print("="*50)
    
    results = {}
    
    # Check Python version
    results["Python Version"] = check_python_version()
    if not results["Python Version"]:
        return
    
    # Create directories
    create_directories()
    results["Directories"] = True
    
    # Setup env
    results["Environment"] = setup_env()
    
    # Install dependencies
    results["Dependencies"] = install_dependencies()
    
    if not results["Dependencies"]:
        print_summary(results)
        return
    
    # Initialize RAG
    results["RAG Engine"] = initialize_rag()
    
    # Test connections (optional, may fail if not configured)
    results["Groq API"] = test_groq_connection()
    results["WAHA Connection"] = test_waha_connection()
    
    print_summary(results)


if __name__ == "__main__":
    main()
