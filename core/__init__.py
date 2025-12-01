"""
Core module for Kitab Imam Mazhab RAG AI
"""

from .rag_engine import KitabMazhabRAG, get_rag_engine
from .agent import KitabMazhabAgent, get_agent, AgentResponse

__all__ = [
    "KitabMazhabRAG",
    "get_rag_engine",
    "KitabMazhabAgent", 
    "get_agent",
    "AgentResponse"
]
