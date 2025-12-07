import os
import uuid
import logging
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    chromadb = None
    CHROMADB_AVAILABLE = False

try:
    from docling.document_converter import DocumentConverter
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False

class KnowledgeBase:
    def __init__(self):
        self.storage_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'knowledge_storage')
        os.makedirs(self.storage_dir, exist_ok=True)
        self.documents_file = os.path.join(self.storage_dir, 'documents.json')
        self.documents = self._load_documents()
        self.chroma_client = None
        self.collection = None
        self.converter = None
        if CHROMADB_AVAILABLE:
            logger.info("ChromaDB available for knowledge base")
        else:
            logger.warning("ChromaDB not available")
        if DOCLING_AVAILABLE:
            logger.info("Docling available for knowledge base")
        else:
            logger.warning("Docling not available")

    def _ensure_chroma(self):
        if self.collection or not CHROMADB_AVAILABLE:
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
        if self.converter or not DOCLING_AVAILABLE:
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
            if self.converter and DOCLING_AVAILABLE:
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
    
    def query(self, query_text: str, n_results: int = 3) -> List[Dict[str, Any]]:
        self._ensure_chroma()
        if not self.collection:
            return []
        
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
            return []
    
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
