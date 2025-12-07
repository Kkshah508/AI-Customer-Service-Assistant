import os
import uuid
import logging
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)

# Environment flag to control heavy ML imports for low-memory deployments
ENABLE_KNOWLEDGE_ML = os.getenv("ENABLE_KNOWLEDGE_ML", "true").lower() == "true"

# Lazy import flags - imports happen only when needed
_chromadb = None
_docling_converter_class = None
CHROMADB_AVAILABLE = False
DOCLING_AVAILABLE = False

def _lazy_import_chromadb():
    global _chromadb, CHROMADB_AVAILABLE
    if _chromadb is not None:
        return _chromadb
    if not ENABLE_KNOWLEDGE_ML:
        return None
    try:
        import chromadb
        _chromadb = chromadb
        CHROMADB_AVAILABLE = True
        logger.info("ChromaDB loaded successfully")
        return _chromadb
    except ImportError:
        logger.warning("ChromaDB not available")
        return None

def _lazy_import_docling():
    global _docling_converter_class, DOCLING_AVAILABLE
    if _docling_converter_class is not None:
        return _docling_converter_class
    if not ENABLE_KNOWLEDGE_ML:
        return None
    try:
        from docling.document_converter import DocumentConverter
        _docling_converter_class = DocumentConverter
        DOCLING_AVAILABLE = True
        logger.info("Docling loaded successfully")
        return _docling_converter_class
    except ImportError:
        logger.warning("Docling not available")
        return None

class KnowledgeBase:
    def __init__(self):
        self.storage_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'knowledge_storage')
        os.makedirs(self.storage_dir, exist_ok=True)
        self.documents_file = os.path.join(self.storage_dir, 'documents.json')
        self.documents = self._load_documents()
        self.chroma_client = None
        self.collection = None
        self.converter = None
        logger.info("KnowledgeBase initialized (ML features load on demand)")

    def _ensure_chroma(self):
        # Skip if already initialized or if collection exists
        if self.collection:
            return
        # Lazy load chromadb only when needed
        chromadb = _lazy_import_chromadb()
        if not chromadb:
            return
        try:
            self.chroma_client = chromadb.PersistentClient(
                path=os.path.join(self.storage_dir, 'chroma_db')
            )
            self.collection = self.chroma_client.get_or_create_collection(
                name="knowledge_base",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("ChromaDB initialized successfully")
        except Exception as e:
            logger.error(f"ChromaDB initialization failed: {e}")
            self.chroma_client = None
            self.collection = None

    def _ensure_converter(self):
        # Skip if already initialized
        if self.converter:
            return
        # Lazy load docling only when needed
        DocumentConverter = _lazy_import_docling()
        if not DocumentConverter:
            return
        try:
            self.converter = DocumentConverter()
            logger.info("Docling converter initialized")
        except Exception as e:
            logger.warning(f"Docling initialization failed: {e}")
            self.converter = None
    
    def _load_documents(self) -> Dict:
        if os.path.exists(self.documents_file):
            try:
                with open(self.documents_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading documents: {e}")
                return {}
        return {}
    
    def _save_documents(self):
        try:
            with open(self.documents_file, 'w', encoding='utf-8') as f:
                json.dump(self.documents, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving documents: {e}")
    
    def process_document(self, file_path: str, filename: str) -> Dict[str, Any]:
        doc_id = str(uuid.uuid4())
        
        try:
            self._ensure_converter()
            # Check if converter was successfully loaded
            if self.converter:
                result = self.converter.convert(file_path)
                text_content = result.document.export_to_markdown()
                logger.info(f"Docling processed {filename} successfully")
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    text_content = f.read()
                logger.info(f"Processed {filename} as plain text")
            
            chunks = self._chunk_text(text_content, chunk_size=500, overlap=50)
            
            self._ensure_chroma()
            if self.collection and chunks:
                chunk_ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
                metadatas = [{"doc_id": doc_id, "filename": filename, "chunk_index": i} for i in range(len(chunks))]
                
                self.collection.add(
                    documents=chunks,
                    metadatas=metadatas,
                    ids=chunk_ids
                )
                logger.info(f"Added {len(chunks)} chunks to vector store for {filename}")
            
            file_hash = self._calculate_file_hash(file_path)
            
            self.documents[doc_id] = {
                "id": doc_id,
                "filename": filename,
                "file_path": file_path,
                "file_hash": file_hash,
                "chunks_count": len(chunks),
                "uploaded_at": str(Path(file_path).stat().st_mtime)
            }
            self._save_documents()
            
            return {
                "id": doc_id,
                "filename": filename,
                "chunks": len(chunks),
                "status": "processed"
            }
            
        except Exception as e:
            logger.error(f"Error processing document {filename}: {e}")
            raise
    
    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            if chunk.strip():
                chunks.append(chunk.strip())
            start = end - overlap
        
        return chunks
    
    def _calculate_file_hash(self, file_path: str) -> str:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def query(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        self._ensure_chroma()
        
        if self.collection:
            try:
                results = self.collection.query(
                    query_texts=[query_text],
                    n_results=n_results
                )
                
                retrieved_chunks = []
                if results and results['documents'] and results['documents'][0]:
                    for i, doc in enumerate(results['documents'][0]):
                        metadata = results['metadatas'][0][i] if results.get('metadatas') else {}
                        distance = results['distances'][0][i] if results.get('distances') else 0
                        
                        retrieved_chunks.append({
                            "text": doc,
                            "metadata": metadata,
                            "score": 1 - distance
                        })
                
                return retrieved_chunks
                
            except Exception as e:
                logger.error(f"Error querying knowledge base: {e}")
        
        return self._fallback_text_search(query_text, n_results)
    
    def _fallback_text_search(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        if not self.documents:
            return []
        
        results = []
        query_lower = query_text.lower()
        query_words = set(query_lower.split())
        
        for doc_id, doc_data in self.documents.items():
            file_path = doc_data.get("file_path")
            if not file_path or not os.path.exists(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                content_lower = content.lower()
                matching_words = sum(1 for word in query_words if word in content_lower)
                if matching_words == 0:
                    continue
                
                score = matching_words / len(query_words) if query_words else 0
                
                chunks = self._chunk_text(content, chunk_size=500, overlap=50)
                for i, chunk in enumerate(chunks):
                    chunk_lower = chunk.lower()
                    chunk_matches = sum(1 for word in query_words if word in chunk_lower)
                    if chunk_matches > 0:
                        chunk_score = chunk_matches / len(query_words)
                        results.append({
                            "text": chunk,
                            "metadata": {"filename": doc_data.get("filename", "Unknown"), "doc_id": doc_id, "chunk_index": i},
                            "score": chunk_score
                        })
            except Exception as e:
                logger.warning(f"Error reading document {doc_id}: {e}")
                continue
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:n_results]
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": doc_id,
                "filename": doc_data["filename"],
                "chunks_count": doc_data.get("chunks_count", 0),
                "uploaded_at": doc_data.get("uploaded_at", "")
            }
            for doc_id, doc_data in self.documents.items()
        ]
    
    def delete_document(self, doc_id: str) -> bool:
        if doc_id not in self.documents:
            return False
        
        try:
            self._ensure_chroma()
            if self.collection:
                chunk_ids = [f"{doc_id}_chunk_{i}" for i in range(self.documents[doc_id].get("chunks_count", 0))]
                if chunk_ids:
                    try:
                        self.collection.delete(ids=chunk_ids)
                    except Exception as e:
                        logger.warning(f"Error deleting chunks from vector store: {e}")
            
            file_path = self.documents[doc_id].get("file_path")
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.warning(f"Error deleting file {file_path}: {e}")
            
            del self.documents[doc_id]
            self._save_documents()
            
            logger.info(f"Deleted document {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            return False
