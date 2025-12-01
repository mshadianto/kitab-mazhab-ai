#!/usr/bin/env python
"""
Test script untuk memverifikasi sistem Kitab Imam Mazhab RAG AI
Jalankan tanpa WAHA untuk testing lokal
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()


def test_rag_engine():
    """Test RAG engine"""
    print("\n" + "="*50)
    print("🧠 Testing RAG Engine")
    print("="*50)
    
    from core.rag_engine import KitabMazhabRAG
    
    rag = KitabMazhabRAG()
    
    # Load knowledge base
    kb_path = Path("data/knowledge_base/kitab_mazhab.json")
    if kb_path.exists():
        doc_count = rag.load_knowledge_base(str(kb_path))
        print(f"✅ Loaded {doc_count} documents")
    else:
        print(f"❌ Knowledge base not found at {kb_path}")
        return False
    
    # Test search
    test_queries = [
        "Siapa pendiri mazhab Syafi'i?",
        "Bagaimana wudhu menurut Hanafi?",
        "Perbedaan posisi tangan shalat"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        results = rag.search(query, top_k=1)
        if results:
            print(f"   ✅ Found {len(results)} result(s)")
            print(f"   Score: {results[0].score:.3f}")
            print(f"   Preview: {results[0].content[:100]}...")
        else:
            print(f"   ⚠️ No results found")
    
    return True


def test_agent():
    """Test AI agent"""
    print("\n" + "="*50)
    print("🤖 Testing AI Agent")
    print("="*50)
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        print("⚠️ GROQ_API_KEY not configured. Skipping agent test.")
        return False
    
    from core.agent import KitabMazhabAgent
    
    try:
        agent = KitabMazhabAgent()
        print("✅ Agent initialized")
        
        # Test greeting
        print("\n📝 Testing greeting...")
        greeting = agent.get_greeting()
        print(f"   Response length: {len(greeting)} chars")
        print(f"   Preview: {greeting[:100]}...")
        
        # Test message processing
        test_messages = [
            "Siapa Imam Syafi'i?",
            "Apa rukun wudhu menurut mazhab Hanafi?"
        ]
        
        for msg in test_messages:
            print(f"\n📝 Query: {msg}")
            response = agent.process_message(msg)
            print(f"   ✅ Response received")
            print(f"   Tools used: {response.tools_used}")
            print(f"   Answer preview: {response.answer[:150]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent error: {e}")
        return False


def test_waha_client():
    """Test WAHA client connection"""
    print("\n" + "="*50)
    print("📱 Testing WAHA Client")
    print("="*50)
    
    api_url = os.getenv("WAHA_API_URL")
    if not api_url:
        print("⚠️ WAHA_API_URL not configured. Skipping WAHA test.")
        return False
    
    from integrations.waha_client import WAHAClient
    
    try:
        client = WAHAClient()
        print(f"✅ Client initialized for {api_url}")
        
        # Get sessions
        sessions = client.get_sessions()
        print(f"✅ Found {len(sessions)} session(s)")
        
        for s in sessions:
            status_emoji = "🟢" if s.status == "WORKING" else "🔴"
            print(f"   {status_emoji} {s.name}: {s.status}")
            if s.phone_number:
                print(f"      Phone: {s.phone_number}")
        
        return True
        
    except Exception as e:
        print(f"❌ WAHA error: {e}")
        return False


def test_integration():
    """Test full integration (simulated)"""
    print("\n" + "="*50)
    print("🔗 Testing Full Integration (Simulated)")
    print("="*50)
    
    # Import all components
    from core.rag_engine import get_rag_engine
    from core.agent import KitabMazhabAgent
    from integrations.waha_client import ConversationManager
    
    print("✅ All components imported successfully")
    
    # Initialize
    rag = get_rag_engine()
    kb_path = Path("data/knowledge_base/kitab_mazhab.json")
    if kb_path.exists():
        rag.load_knowledge_base(str(kb_path))
    
    conversation_mgr = ConversationManager()
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        print("⚠️ Skipping agent test (no API key)")
        return True
    
    agent = KitabMazhabAgent()
    
    # Simulate conversation
    test_conversation = [
        ("user1", "Assalamualaikum"),
        ("user1", "Siapa Imam Syafi'i?"),
        ("user2", "Bagaimana wudhu menurut Hanafi?"),
        ("user1", "Apa kitab-kitab dalam mazhab Syafi'i?")
    ]
    
    print("\n📱 Simulating conversations...")
    
    for user, message in test_conversation:
        print(f"\n[{user}]: {message}")
        
        # Get history
        history = conversation_mgr.get_history(user)
        
        # Process
        response = agent.process_message(message, history)
        
        # Update history
        conversation_mgr.add_message(user, "user", message)
        conversation_mgr.add_message(user, "assistant", response.answer)
        
        print(f"[Bot]: {response.answer[:100]}...")
    
    print("\n✅ Integration test completed")
    return True


def main():
    """Run all tests"""
    print("🕌 KITAB IMAM MAZHAB RAG AI - TEST SUITE")
    print("="*50)
    
    results = {}
    
    # Test RAG Engine
    results["RAG Engine"] = test_rag_engine()
    
    # Test Agent
    results["AI Agent"] = test_agent()
    
    # Test WAHA
    results["WAHA Client"] = test_waha_client()
    
    # Test Integration
    results["Integration"] = test_integration()
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    for test, passed in results.items():
        emoji = "✅" if passed else "❌"
        print(f"  {emoji} {test}")
    
    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    print(f"\n  Passed: {passed_count}/{total_count}")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️ Some tests failed. Check configuration.")


if __name__ == "__main__":
    main()
