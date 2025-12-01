"""
Agentic AI untuk Kitab Imam Mazhab
Menggunakan Groq API dengan kemampuan reasoning dan multi-tool
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from groq import Groq

from core.rag_engine import get_rag_engine, SearchResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ToolType(Enum):
    SEARCH_MAZHAB = "search_mazhab"
    COMPARE_MAZHAB = "compare_mazhab"
    GET_IMAM_BIO = "get_imam_bio"
    GET_FIQIH_RULING = "get_fiqih_ruling"
    LIST_KITAB = "list_kitab"


@dataclass
class Tool:
    """Tool definition for the agent"""
    name: str
    description: str
    parameters: Dict[str, Any]
    function: Callable


@dataclass
class AgentResponse:
    """Response from the agent"""
    answer: str
    sources: List[Dict[str, Any]] = field(default_factory=list)
    reasoning: str = ""
    tools_used: List[str] = field(default_factory=list)


class KitabMazhabAgent:
    """
    Agentic AI untuk menjawab pertanyaan tentang Kitab Imam Mazhab
    dengan kemampuan reasoning dan penggunaan tools
    """
    
    SYSTEM_PROMPT = """Anda adalah seorang ulama virtual yang ahli dalam empat mazhab fiqih Islam (Hanafi, Maliki, Syafi'i, dan Hanbali). 

PERAN ANDA:
- Menjawab pertanyaan tentang fiqih dan kitab-kitab imam mazhab dengan akurat
- Menjelaskan perbedaan pendapat antar mazhab dengan adil dan objektif
- Memberikan dalil dan referensi dari kitab-kitab mu'tabar
- Menggunakan bahasa yang mudah dipahami namun tetap ilmiah

PRINSIP DALAM MENJAWAB:
1. Selalu berdasarkan sumber yang valid dari konteks yang diberikan
2. Jika ada perbedaan pendapat, sebutkan semua pendapat secara adil
3. Jangan membuat fatwa atau hukum baru, hanya menjelaskan pendapat yang sudah ada
4. Jika tidak yakin atau informasi tidak ada dalam konteks, katakan dengan jujur
5. Gunakan istilah Arab dengan transliterasi dan terjemahan

FORMAT JAWABAN:
- Mulai dengan jawaban langsung
- Berikan penjelasan detail jika diperlukan
- Sebutkan sumber/referensi mazhab
- Akhiri dengan catatan penting jika ada

BAHASA:
- Gunakan Bahasa Indonesia yang baik
- Sertakan istilah Arab asli dengan transliterasi
- Jelaskan istilah teknis untuk pemula
"""

    MAZHAB_LIST = ["hanafi", "maliki", "syafii", "hanbali"]
    
    def __init__(
        self,
        groq_api_key: Optional[str] = None,
        model: str = "llama-3.3-70b-versatile"
    ):
        self.api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is required")
        
        self.model = model
        self.client = Groq(api_key=self.api_key)
        self.rag = get_rag_engine()
        
        # Initialize tools
        self.tools = self._initialize_tools()
        
        logger.info(f"KitabMazhabAgent initialized with model: {model}")
    
    def _initialize_tools(self) -> Dict[str, Tool]:
        """Initialize available tools"""
        return {
            ToolType.SEARCH_MAZHAB.value: Tool(
                name="search_mazhab",
                description="Mencari informasi umum tentang mazhab tertentu",
                parameters={
                    "query": "Kata kunci pencarian",
                    "mazhab": "Nama mazhab (opsional): hanafi, maliki, syafii, hanbali"
                },
                function=self._tool_search_mazhab
            ),
            ToolType.COMPARE_MAZHAB.value: Tool(
                name="compare_mazhab",
                description="Membandingkan pendapat antar mazhab dalam suatu masalah",
                parameters={
                    "topic": "Topik yang ingin dibandingkan"
                },
                function=self._tool_compare_mazhab
            ),
            ToolType.GET_IMAM_BIO.value: Tool(
                name="get_imam_bio",
                description="Mendapatkan biografi imam pendiri mazhab",
                parameters={
                    "mazhab": "Nama mazhab: hanafi, maliki, syafii, hanbali"
                },
                function=self._tool_get_imam_bio
            ),
            ToolType.GET_FIQIH_RULING.value: Tool(
                name="get_fiqih_ruling",
                description="Mendapatkan hukum fiqih tentang topik tertentu",
                parameters={
                    "topic": "Topik fiqih (thaharah, shalat, zakat, puasa, haji, nikah, dll)",
                    "mazhab": "Nama mazhab (opsional)"
                },
                function=self._tool_get_fiqih_ruling
            ),
            ToolType.LIST_KITAB.value: Tool(
                name="list_kitab",
                description="Mendapatkan daftar kitab rujukan mazhab",
                parameters={
                    "mazhab": "Nama mazhab: hanafi, maliki, syafii, hanbali"
                },
                function=self._tool_list_kitab
            )
        }
    
    # Tool implementations
    def _tool_search_mazhab(self, query: str, mazhab: Optional[str] = None) -> str:
        """Search general mazhab information"""
        filter_mazhab = mazhab.lower() if mazhab and mazhab.lower() in self.MAZHAB_LIST else None
        return self.rag.get_context_for_query(query, top_k=5, filter_mazhab=filter_mazhab)
    
    def _tool_compare_mazhab(self, topic: str) -> str:
        """Compare opinions across mazhabs"""
        # Search with comparison filter
        results = self.rag.search(
            f"perbandingan {topic}",
            top_k=3,
            filter_category="comparison"
        )
        
        if results:
            return "\n\n".join([r.content for r in results])
        
        # Fallback: search each mazhab
        all_results = []
        for mazhab in self.MAZHAB_LIST:
            mazhab_results = self.rag.search(topic, top_k=2, filter_mazhab=mazhab)
            if mazhab_results:
                all_results.append(f"=== MAZHAB {mazhab.upper()} ===\n{mazhab_results[0].content}")
        
        return "\n\n".join(all_results) if all_results else "Tidak ditemukan informasi perbandingan."
    
    def _tool_get_imam_bio(self, mazhab: str) -> str:
        """Get imam biography"""
        mazhab_lower = mazhab.lower()
        if mazhab_lower not in self.MAZHAB_LIST:
            return f"Mazhab tidak valid. Pilih dari: {', '.join(self.MAZHAB_LIST)}"
        
        results = self.rag.search(
            f"imam biografi {mazhab}",
            top_k=2,
            filter_mazhab=mazhab_lower,
            filter_category="imam_biography"
        )
        
        if results:
            return results[0].content
        
        # Fallback
        return self.rag.get_context_for_query(f"siapa imam pendiri mazhab {mazhab}", top_k=3)
    
    def _tool_get_fiqih_ruling(self, topic: str, mazhab: Optional[str] = None) -> str:
        """Get fiqih rulings"""
        filter_mazhab = mazhab.lower() if mazhab and mazhab.lower() in self.MAZHAB_LIST else None
        
        # Map common topics
        topic_mapping = {
            "wudhu": "thaharah wudhu",
            "sholat": "shalat",
            "salat": "shalat",
            "mandi": "thaharah mandi",
            "tayamum": "thaharah tayammum",
            "nikah": "nikah pernikahan",
            "menikah": "nikah pernikahan"
        }
        
        search_topic = topic_mapping.get(topic.lower(), topic)
        
        return self.rag.get_context_for_query(
            f"hukum {search_topic}",
            top_k=5,
            filter_mazhab=filter_mazhab
        )
    
    def _tool_list_kitab(self, mazhab: str) -> str:
        """List reference books"""
        mazhab_lower = mazhab.lower()
        if mazhab_lower not in self.MAZHAB_LIST:
            return f"Mazhab tidak valid. Pilih dari: {', '.join(self.MAZHAB_LIST)}"
        
        results = self.rag.search(
            f"kitab rujukan {mazhab}",
            top_k=2,
            filter_mazhab=mazhab_lower,
            filter_category="kitab_reference"
        )
        
        if results:
            return results[0].content
        
        return self.rag.get_context_for_query(f"kitab utama mazhab {mazhab}", top_k=3)
    
    def _determine_intent(self, message: str) -> Dict[str, Any]:
        """Determine user intent and required tools"""
        message_lower = message.lower()
        
        intent = {
            "primary_tool": None,
            "params": {},
            "is_comparison": False,
            "detected_mazhab": None,
            "detected_topic": None
        }
        
        # Detect mazhab
        for mazhab in self.MAZHAB_LIST:
            if mazhab in message_lower or mazhab.replace("i", "ie") in message_lower:
                intent["detected_mazhab"] = mazhab
                break
        
        # Detect comparison intent
        comparison_keywords = ["perbedaan", "perbandingan", "beda", "berbeda", "compare", "versus", "vs"]
        if any(kw in message_lower for kw in comparison_keywords):
            intent["is_comparison"] = True
            intent["primary_tool"] = ToolType.COMPARE_MAZHAB.value
        
        # Detect biography intent
        bio_keywords = ["siapa", "biografi", "riwayat hidup", "sejarah", "pendiri", "imam"]
        if any(kw in message_lower for kw in bio_keywords) and intent["detected_mazhab"]:
            intent["primary_tool"] = ToolType.GET_IMAM_BIO.value
        
        # Detect fiqih topics
        fiqih_topics = {
            "wudhu": ["wudhu", "wudu", "berwudhu"],
            "shalat": ["shalat", "sholat", "salat", "sembahyang"],
            "thaharah": ["thaharah", "bersuci", "mandi wajib", "tayammum", "najis"],
            "zakat": ["zakat", "sedekah wajib"],
            "puasa": ["puasa", "shaum", "saum", "ramadhan"],
            "haji": ["haji", "umrah", "ihram", "thawaf", "sa'i"],
            "nikah": ["nikah", "pernikahan", "menikah", "wali", "mahar"],
            "muamalah": ["jual beli", "riba", "muamalah", "perdagangan"]
        }
        
        for topic, keywords in fiqih_topics.items():
            if any(kw in message_lower for kw in keywords):
                intent["detected_topic"] = topic
                intent["primary_tool"] = ToolType.GET_FIQIH_RULING.value
                break
        
        # Detect kitab intent
        kitab_keywords = ["kitab", "buku", "rujukan", "referensi", "karya"]
        if any(kw in message_lower for kw in kitab_keywords):
            intent["primary_tool"] = ToolType.LIST_KITAB.value
        
        # Default to general search
        if not intent["primary_tool"]:
            intent["primary_tool"] = ToolType.SEARCH_MAZHAB.value
        
        return intent
    
    def _execute_tool(self, tool_name: str, **params) -> str:
        """Execute a tool and return results"""
        if tool_name not in self.tools:
            return f"Tool tidak ditemukan: {tool_name}"
        
        tool = self.tools[tool_name]
        try:
            return tool.function(**params)
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return f"Error menjalankan tool: {str(e)}"
    
    def _generate_response(
        self,
        user_message: str,
        context: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """Generate response using Groq API"""
        
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT}
        ]
        
        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history[-6:])  # Last 3 exchanges
        
        # Add context and user message
        enhanced_message = f"""KONTEKS DARI DATABASE KITAB MAZHAB:
{context}

PERTANYAAN PENGGUNA:
{user_message}

Berikan jawaban yang informatif berdasarkan konteks di atas. Jika informasi tidak tersedia dalam konteks, katakan dengan jujur."""

        messages.append({"role": "user", "content": enhanced_message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
                top_p=0.9
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error calling Groq API: {e}")
            return f"Maaf, terjadi kesalahan dalam memproses pertanyaan Anda. Error: {str(e)}"
    
    def process_message(
        self,
        message: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> AgentResponse:
        """Process user message and generate response"""
        
        logger.info(f"Processing message: {message[:100]}...")
        
        # Determine intent
        intent = self._determine_intent(message)
        logger.info(f"Detected intent: {intent}")
        
        tools_used = []
        all_context = []
        
        # Execute primary tool
        primary_tool = intent["primary_tool"]
        tools_used.append(primary_tool)
        
        if primary_tool == ToolType.COMPARE_MAZHAB.value:
            context = self._execute_tool(
                primary_tool,
                topic=intent.get("detected_topic", message)
            )
        elif primary_tool == ToolType.GET_IMAM_BIO.value:
            if intent["detected_mazhab"]:
                context = self._execute_tool(primary_tool, mazhab=intent["detected_mazhab"])
            else:
                context = self._execute_tool(ToolType.SEARCH_MAZHAB.value, query=message)
        elif primary_tool == ToolType.GET_FIQIH_RULING.value:
            context = self._execute_tool(
                primary_tool,
                topic=intent.get("detected_topic", message),
                mazhab=intent.get("detected_mazhab")
            )
        elif primary_tool == ToolType.LIST_KITAB.value:
            if intent["detected_mazhab"]:
                context = self._execute_tool(primary_tool, mazhab=intent["detected_mazhab"])
            else:
                # List all if no specific mazhab
                all_kitab = []
                for mzb in self.MAZHAB_LIST:
                    all_kitab.append(self._execute_tool(primary_tool, mazhab=mzb))
                context = "\n\n".join(all_kitab)
        else:
            context = self._execute_tool(
                primary_tool,
                query=message,
                mazhab=intent.get("detected_mazhab")
            )
        
        all_context.append(context)
        
        # If comparison needed but not detected, add comparison context
        if intent["is_comparison"] and primary_tool != ToolType.COMPARE_MAZHAB.value:
            tools_used.append(ToolType.COMPARE_MAZHAB.value)
            comparison_context = self._execute_tool(
                ToolType.COMPARE_MAZHAB.value,
                topic=intent.get("detected_topic", message)
            )
            all_context.append(comparison_context)
        
        # Combine all context
        combined_context = "\n\n---\n\n".join(all_context)
        
        # Generate response
        answer = self._generate_response(
            message,
            combined_context,
            conversation_history
        )
        
        return AgentResponse(
            answer=answer,
            sources=[{"tool": t} for t in tools_used],
            reasoning=f"Intent: {intent}",
            tools_used=tools_used
        )
    
    def get_greeting(self) -> str:
        """Get greeting message"""
        return """Assalamu'alaikum warahmatullahi wabarakatuh 🙏

Saya adalah *Asisten Kitab Imam Mazhab*, siap membantu Anda mempelajari empat mazhab fiqih Islam:

📚 *Mazhab Hanafi* - Imam Abu Hanifah
📚 *Mazhab Maliki* - Imam Malik
📚 *Mazhab Syafi'i* - Imam Syafi'i  
📚 *Mazhab Hanbali* - Imam Ahmad bin Hanbal

*Yang bisa saya bantu:*
• Biografi dan sejarah para imam
• Hukum fiqih (thaharah, shalat, zakat, puasa, haji, nikah, dll)
• Kitab-kitab rujukan setiap mazhab
• Perbandingan pendapat antar mazhab
• Metodologi istinbath hukum

Silakan ajukan pertanyaan Anda! 🤲"""
    
    def get_help(self) -> str:
        """Get help message"""
        return """*PANDUAN PENGGUNAAN* 📖

*Contoh pertanyaan:*

1️⃣ *Biografi Imam*
   "Siapa Imam Syafi'i?"
   "Ceritakan tentang Imam Abu Hanifah"

2️⃣ *Hukum Fiqih*
   "Bagaimana cara wudhu menurut mazhab Syafi'i?"
   "Apa yang membatalkan puasa?"
   "Rukun nikah dalam Islam"

3️⃣ *Perbandingan Mazhab*
   "Apa perbedaan posisi tangan shalat antar mazhab?"
   "Bandingkan cara mengusap kepala saat wudhu"

4️⃣ *Kitab Rujukan*
   "Kitab apa saja dalam mazhab Maliki?"
   "Sebutkan kitab-kitab fiqih Hanbali"

5️⃣ *Metodologi*
   "Apa ciri khas mazhab Hanafi?"
   "Sumber hukum mazhab Syafi'i"

*Tips:*
• Sebutkan nama mazhab untuk jawaban spesifik
• Gunakan kata "bandingkan" untuk melihat perbedaan
• Pertanyaan bisa dalam Bahasa Indonesia atau Arab

Ketik pertanyaan Anda... 🤲"""


# Singleton
_agent_instance: Optional[KitabMazhabAgent] = None

def get_agent() -> KitabMazhabAgent:
    """Get or create agent singleton"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = KitabMazhabAgent()
    return _agent_instance


if __name__ == "__main__":
    # Test the agent
    agent = KitabMazhabAgent()
    
    # Load RAG data first
    from core.rag_engine import get_rag_engine
    rag = get_rag_engine()
    rag.load_knowledge_base("./data/knowledge_base/kitab_mazhab.json")
    
    # Test queries
    test_messages = [
        "Assalamualaikum",
        "Siapa pendiri mazhab Syafi'i?",
        "Bagaimana cara wudhu menurut Hanafi?",
        "Apa perbedaan posisi tangan shalat antar mazhab?"
    ]
    
    for msg in test_messages:
        print(f"\n{'='*60}")
        print(f"User: {msg}")
        print('='*60)
        
        response = agent.process_message(msg)
        print(f"\nAgent: {response.answer}")
        print(f"\nTools used: {response.tools_used}")
