"""
RAG Engine untuk Kitab Imam Mazhab
Menggunakan ChromaDB sebagai vector store dan sentence-transformers untuk embedding
"""

import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Hasil pencarian dari RAG"""
    content: str
    metadata: Dict[str, Any]
    score: float
    source: str


class KitabMazhabRAG:
    """
    RAG Engine untuk pengetahuan Kitab Imam Mazhab
    """
    
    def __init__(
        self,
        persist_directory: str = "./data/chroma_db",
        embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        collection_name: str = "kitab_mazhab"
    ):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Initialize embedding model
        logger.info(f"Loading embedding model: {embedding_model}")
        self.embedder = SentenceTransformer(embedding_model)
        
        # Initialize ChromaDB
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Kitab Imam Mazhab Knowledge Base"}
        )
        
        logger.info(f"RAG Engine initialized. Collection has {self.collection.count()} documents")
    
    def _flatten_json(self, data: Dict, prefix: str = "") -> List[Dict[str, Any]]:
        """Flatten nested JSON into chunks with metadata"""
        chunks = []
        
        def process_item(item: Any, path: str, parent_context: str = ""):
            if isinstance(item, dict):
                # Create chunk for dict with meaningful content
                if any(isinstance(v, str) for v in item.values()):
                    content_parts = []
                    metadata = {"path": path}
                    
                    for k, v in item.items():
                        if isinstance(v, str):
                            content_parts.append(f"{k}: {v}")
                        elif isinstance(v, list) and all(isinstance(i, str) for i in v):
                            content_parts.append(f"{k}: {', '.join(v)}")
                    
                    if content_parts:
                        content = f"{parent_context}\n" + "\n".join(content_parts) if parent_context else "\n".join(content_parts)
                        chunks.append({
                            "content": content.strip(),
                            "metadata": metadata
                        })
                
                # Recurse into nested dicts
                for k, v in item.items():
                    new_path = f"{path}.{k}" if path else k
                    new_context = f"{parent_context} > {k}" if parent_context else k
                    process_item(v, new_path, new_context)
                    
            elif isinstance(item, list):
                for i, v in enumerate(item):
                    if isinstance(v, dict):
                        process_item(v, f"{path}[{i}]", parent_context)
                    elif isinstance(v, str) and len(v) > 50:
                        chunks.append({
                            "content": f"{parent_context}: {v}",
                            "metadata": {"path": f"{path}[{i}]"}
                        })
        
        process_item(data, prefix)
        return chunks
    
    def _create_mazhab_chunks(self, data: Dict) -> List[Dict[str, Any]]:
        """Create specialized chunks for mazhab knowledge"""
        chunks = []
        
        mazhab_data = data.get("mazhab", {})
        
        for mazhab_name, mazhab_info in mazhab_data.items():
            mazhab_title = mazhab_name.capitalize()
            
            # Imam biography chunk
            if "imam" in mazhab_info:
                imam = mazhab_info["imam"]
                chunk = f"""MAZHAB {mazhab_title.upper()}

Imam: {imam.get('nama', '')}
Lahir: {imam.get('lahir', '')}
Wafat: {imam.get('wafat', '')}
Gelar: {imam.get('gelar', '')}

Biografi:
{imam.get('biografi', '')}

Guru-guru: {', '.join(imam.get('guru', []))}
Murid utama: {', '.join(imam.get('murid_utama', []))}
"""
                chunks.append({
                    "content": chunk.strip(),
                    "metadata": {
                        "mazhab": mazhab_name,
                        "category": "imam_biography",
                        "imam_name": imam.get('nama', '')
                    }
                })
            
            # Methodology chunk
            if "metodologi" in mazhab_info:
                metod = mazhab_info["metodologi"]
                sumber = "\n- ".join(metod.get('sumber_hukum', []))
                prinsip = "\n- ".join(metod.get('prinsip_utama', []))
                
                chunk = f"""METODOLOGI MAZHAB {mazhab_title.upper()}

Sumber Hukum:
- {sumber}

Ciri Khas:
{metod.get('ciri_khas', '')}

Prinsip Utama:
- {prinsip}
"""
                chunks.append({
                    "content": chunk.strip(),
                    "metadata": {
                        "mazhab": mazhab_name,
                        "category": "methodology"
                    }
                })
            
            # Kitab utama chunks
            if "kitab_utama" in mazhab_info:
                kitab_list = []
                for kitab in mazhab_info["kitab_utama"]:
                    kitab_list.append(f"• {kitab['judul']} karya {kitab['penulis']}: {kitab['deskripsi']}")
                
                chunk = f"""KITAB-KITAB UTAMA MAZHAB {mazhab_title.upper()}

{chr(10).join(kitab_list)}
"""
                chunks.append({
                    "content": chunk.strip(),
                    "metadata": {
                        "mazhab": mazhab_name,
                        "category": "kitab_reference"
                    }
                })
            
            # Hukum fiqih chunks - per category
            if "hukum_fiqih" in mazhab_info:
                for category, details in mazhab_info["hukum_fiqih"].items():
                    chunk_content = f"HUKUM {category.upper()} MAZHAB {mazhab_title.upper()}\n\n"
                    
                    def format_details(d, indent=0):
                        result = ""
                        for key, value in d.items():
                            prefix = "  " * indent
                            if isinstance(value, dict):
                                result += f"{prefix}{key.replace('_', ' ').title()}:\n"
                                result += format_details(value, indent + 1)
                            elif isinstance(value, list):
                                result += f"{prefix}{key.replace('_', ' ').title()}:\n"
                                for item in value:
                                    if isinstance(item, str):
                                        result += f"{prefix}  • {item}\n"
                                    elif isinstance(item, dict):
                                        for k, v in item.items():
                                            result += f"{prefix}  • {k}: {v}\n"
                            else:
                                result += f"{prefix}{key.replace('_', ' ').title()}: {value}\n"
                        return result
                    
                    chunk_content += format_details(details)
                    
                    chunks.append({
                        "content": chunk_content.strip(),
                        "metadata": {
                            "mazhab": mazhab_name,
                            "category": f"fiqih_{category}",
                            "topic": category
                        }
                    })
            
            # Penyebaran geografis
            if "penyebaran" in mazhab_info:
                wilayah = ", ".join(mazhab_info["penyebaran"])
                chunk = f"""PENYEBARAN MAZHAB {mazhab_title.upper()}

Mazhab {mazhab_title} tersebar luas di wilayah berikut:
{wilayah}

Mazhab ini menjadi mazhab mayoritas di daerah-daerah tersebut dan mempengaruhi praktik keagamaan masyarakat setempat.
"""
                chunks.append({
                    "content": chunk.strip(),
                    "metadata": {
                        "mazhab": mazhab_name,
                        "category": "geographical_spread"
                    }
                })
        
        # Perbandingan praktis
        if "perbandingan_praktis" in data:
            for topic, comparison in data["perbandingan_praktis"].items():
                chunk = f"""PERBANDINGAN ANTAR MAZHAB: {topic.replace('_', ' ').upper()}

"""
                for mazhab, pendapat in comparison.items():
                    chunk += f"• Mazhab {mazhab.capitalize()}: {pendapat}\n"
                
                chunks.append({
                    "content": chunk.strip(),
                    "metadata": {
                        "category": "comparison",
                        "topic": topic
                    }
                })
        
        # Adab ikhtilaf
        if "adab_ikhtilaf" in data:
            adab = data["adab_ikhtilaf"]
            prinsip = "\n• ".join(adab.get("prinsip", []))
            kutipan = "\n\n".join(adab.get("kutipan_ulama", []))
            
            chunk = f"""ADAB DALAM PERBEDAAN MAZHAB

Prinsip-prinsip dalam menyikapi perbedaan mazhab:
• {prinsip}

Kutipan dari para Imam:

{kutipan}
"""
            chunks.append({
                "content": chunk.strip(),
                "metadata": {
                    "category": "adab_ikhtilaf"
                }
            })
        
        return chunks
    
    def load_knowledge_base(self, json_path: str) -> int:
        """Load knowledge base from JSON file"""
        logger.info(f"Loading knowledge base from: {json_path}")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create specialized chunks
        chunks = self._create_mazhab_chunks(data)
        
        logger.info(f"Created {len(chunks)} chunks from knowledge base")
        
        # Check if already loaded
        if self.collection.count() > 0:
            logger.info("Collection already has data. Clearing and reloading...")
            # Delete existing
            existing_ids = self.collection.get()['ids']
            if existing_ids:
                self.collection.delete(ids=existing_ids)
        
        # Prepare for insertion
        documents = []
        metadatas = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            documents.append(chunk["content"])
            metadatas.append(chunk["metadata"])
            ids.append(f"chunk_{i}")
        
        # Generate embeddings and add to collection
        logger.info("Generating embeddings...")
        embeddings = self.embedder.encode(documents, show_progress_bar=True).tolist()
        
        # Add in batches
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            end = min(i + batch_size, len(documents))
            self.collection.add(
                documents=documents[i:end],
                embeddings=embeddings[i:end],
                metadatas=metadatas[i:end],
                ids=ids[i:end]
            )
            logger.info(f"Added batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")
        
        logger.info(f"Successfully loaded {len(documents)} documents into vector store")
        return len(documents)
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        filter_mazhab: Optional[str] = None,
        filter_category: Optional[str] = None
    ) -> List[SearchResult]:
        """Search the knowledge base"""
        
        # Build filter
        where_filter = None
        if filter_mazhab or filter_category:
            conditions = []
            if filter_mazhab:
                conditions.append({"mazhab": filter_mazhab.lower()})
            if filter_category:
                conditions.append({"category": filter_category})
            
            if len(conditions) == 1:
                where_filter = conditions[0]
            else:
                where_filter = {"$and": conditions}
        
        # Generate query embedding
        query_embedding = self.embedder.encode(query).tolist()
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        search_results = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                # Convert distance to similarity score (ChromaDB uses L2 distance)
                distance = results['distances'][0][i] if results['distances'] else 0
                score = 1 / (1 + distance)  # Convert to similarity
                
                search_results.append(SearchResult(
                    content=doc,
                    metadata=results['metadatas'][0][i] if results['metadatas'] else {},
                    score=score,
                    source=results['metadatas'][0][i].get('category', 'unknown') if results['metadatas'] else 'unknown'
                ))
        
        return search_results
    
    def get_context_for_query(
        self,
        query: str,
        top_k: int = 5,
        filter_mazhab: Optional[str] = None
    ) -> str:
        """Get formatted context for LLM from search results"""
        
        results = self.search(query, top_k=top_k, filter_mazhab=filter_mazhab)
        
        if not results:
            return "Tidak ditemukan informasi yang relevan dalam database."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"[Sumber {i}] (Relevansi: {result.score:.2f})\n{result.content}")
        
        return "\n\n---\n\n".join(context_parts)


# Singleton instance
_rag_instance: Optional[KitabMazhabRAG] = None

def get_rag_engine() -> KitabMazhabRAG:
    """Get or create RAG engine singleton"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = KitabMazhabRAG()
    return _rag_instance


if __name__ == "__main__":
    # Test the RAG engine
    rag = KitabMazhabRAG()
    
    # Load knowledge base
    kb_path = "./data/knowledge_base/kitab_mazhab.json"
    if Path(kb_path).exists():
        rag.load_knowledge_base(kb_path)
    
    # Test search
    test_queries = [
        "Siapa pendiri mazhab Syafi'i?",
        "Bagaimana cara wudhu menurut mazhab Hanafi?",
        "Apa perbedaan posisi tangan saat shalat antar mazhab?",
        "Kitab apa saja yang menjadi rujukan mazhab Maliki?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print('='*60)
        
        results = rag.search(query, top_k=2)
        for i, result in enumerate(results, 1):
            print(f"\n[Result {i}] Score: {result.score:.3f}")
            print(f"Category: {result.metadata.get('category', 'N/A')}")
            print(f"Content: {result.content[:300]}...")
