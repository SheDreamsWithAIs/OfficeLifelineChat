"""
Hybrid RAG/CAG (Retrieval-Augmented Generation / Cached-Augmented Generation) strategy.

This strategy combines RAG and CAG:
- First call: Performs RAG retrieval from ChromaDB
- Subsequent calls: Uses cached results from session state

LangChain Version: v1.0+
"""

from typing import Dict, List, Optional, Any
from app.retrieval.rag_strategy import RAGStrategy


class HybridRAGCAGStrategy:
    """
    Hybrid retrieval strategy that uses RAG initially, then caches results.
    
    Suitable for billing queries where:
    - First query: Retrieve relevant billing info via RAG
    - Follow-up queries: Use cached billing context (policies don't change frequently)
    """
    
    def __init__(self, collection_name: str, k: int = 3):
        """
        Initialize Hybrid RAG/CAG strategy.
        
        Args:
            collection_name: ChromaDB collection name for RAG retrieval
            k: Number of documents to retrieve via RAG
        """
        self.rag_strategy = RAGStrategy(collection_name=collection_name, k=k)
        self.collection_name = collection_name
        self.k = k
    
    def retrieve(
        self,
        query: str,
        session_cache: Dict[str, Any],
        k: Optional[int] = None,
        filter: Optional[dict] = None
    ) -> List[str]:
        """
        Retrieve documents using hybrid strategy.
        
        Args:
            query: User query string
            session_cache: Session state dictionary to store/retrieve cache
            k: Number of documents to retrieve (overrides instance default)
            filter: Optional metadata filter
            
        Returns:
            List of retrieved document chunk strings
        """
        cache_key = f"hybrid_cache_{self.collection_name}"
        
        # Check if cache exists in session
        if cache_key in session_cache:
            cached_chunks = session_cache[cache_key]
            print(f"[Hybrid Strategy] Using cached results (no RAG call)")
            return cached_chunks
        
        # First call: Perform RAG retrieval
        print(f"[Hybrid Strategy] Performing RAG retrieval (first call)")
        try:
            chunks = self.rag_strategy.retrieve(query, k=k, filter=filter)
            
            # Cache results in session
            session_cache[cache_key] = chunks
            print(f"[Hybrid Strategy] Cached {len(chunks)} chunks for future use")
            
            return chunks
        except Exception as e:
            # Handle case where collection doesn't exist or is corrupted
            print(f"[Hybrid Strategy] Warning: Error retrieving from collection '{self.collection_name}': {e}")
            return []
    
    def get_context(
        self,
        query: str,
        session_cache: Dict[str, Any],
        k: Optional[int] = None,
        filter: Optional[dict] = None
    ) -> str:
        """
        Get formatted context string using hybrid strategy.
        
        Args:
            query: User query string
            session_cache: Session state dictionary
            k: Number of documents to retrieve
            filter: Optional metadata filter
            
        Returns:
            Formatted context string
        """
        chunks = self.retrieve(query, session_cache, k=k, filter=filter)
        
        if not chunks:
            return "No relevant information found."
        
        context_parts = ["Relevant billing information:\n"]
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(f"\n--- Document {i} ---\n{chunk}")
        
        return "\n".join(context_parts)
    
    def clear_cache(self, session_cache: Dict[str, Any]) -> None:
        """
        Clear cached results from session.
        
        Args:
            session_cache: Session state dictionary
        """
        cache_key = f"hybrid_cache_{self.collection_name}"
        if cache_key in session_cache:
            del session_cache[cache_key]
            print(f"[Hybrid Strategy] Cache cleared for {self.collection_name}")

