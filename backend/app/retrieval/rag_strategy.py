"""
Pure RAG (Retrieval-Augmented Generation) strategy.

This strategy retrieves relevant document chunks from ChromaDB based on
semantic similarity and returns them for LLM context.

LangChain Version: v1.0+
Documentation Reference: https://docs.langchain.com/oss/python/langchain/retrieval
"""

from typing import List, Optional
from langchain_chroma import Chroma

from app.vectorstore.chroma_client import get_chroma_client


class RAGStrategy:
    """Pure RAG retrieval strategy using vector similarity search."""
    
    def __init__(self, collection_name: str, k: int = 3):
        """
        Initialize RAG strategy.
        
        Args:
            collection_name: ChromaDB collection name to search
            k: Number of documents to retrieve (default: 3)
        """
        self.collection_name = collection_name
        self.k = k
        self.client = get_chroma_client()
        self.vectorstore: Optional[Chroma] = None
    
    def _get_vectorstore(self) -> Chroma:
        """Get or create vector store instance."""
        if self.vectorstore is None:
            self.vectorstore = self.client.get_vectorstore(self.collection_name)
        return self.vectorstore
    
    def retrieve(self, query: str, k: Optional[int] = None, filter: Optional[dict] = None) -> List[str]:
        """
        Retrieve relevant document chunks for a query.
        
        Args:
            query: User query string
            k: Number of documents to retrieve (overrides instance default)
            filter: Optional metadata filter (e.g., {'domain': 'technical'})
            
        Returns:
            List of retrieved document chunk strings formatted for LLM context
        """
        try:
            vectorstore = self._get_vectorstore()
            num_results = k if k is not None else self.k
            
            # Perform similarity search
            if filter:
                results = vectorstore.similarity_search(
                    query,
                    k=num_results,
                    filter=filter
                )
            else:
                results = vectorstore.similarity_search(query, k=num_results)
            
            # Format results for LLM context
            formatted_chunks = []
            for i, doc in enumerate(results, 1):
                # Include metadata in context for better understanding
                metadata_info = ""
                if doc.metadata:
                    source = doc.metadata.get('source_file', 'unknown')
                    metadata_info = f"[Source: {source}]"
                
                chunk_text = f"{metadata_info}\n{doc.page_content}"
                formatted_chunks.append(chunk_text)
            
            return formatted_chunks
        except Exception as e:
            # Handle case where collection doesn't exist or is corrupted
            # Return empty list so get_context can handle it gracefully
            print(f"Warning: Error retrieving from collection '{self.collection_name}': {e}")
            return []
    
    def retrieve_with_scores(self, query: str, k: Optional[int] = None, filter: Optional[dict] = None) -> List[tuple]:
        """
        Retrieve documents with similarity scores.
        
        Args:
            query: User query string
            k: Number of documents to retrieve
            filter: Optional metadata filter
            
        Returns:
            List of tuples (document_text, similarity_score)
        """
        vectorstore = self._get_vectorstore()
        num_results = k if k is not None else self.k
        
        # Use similarity_search_with_score to get scores
        if filter:
            results = vectorstore.similarity_search_with_score(
                query,
                k=num_results,
                filter=filter
            )
        else:
            results = vectorstore.similarity_search_with_score(query, k=num_results)
        
        formatted_results = []
        for doc, score in results:
            metadata_info = ""
            if doc.metadata:
                source = doc.metadata.get('source_file', 'unknown')
                metadata_info = f"[Source: {source}]"
            
            chunk_text = f"{metadata_info}\n{doc.page_content}"
            formatted_results.append((chunk_text, score))
        
        return formatted_results
    
    def get_context(self, query: str, k: Optional[int] = None, filter: Optional[dict] = None) -> str:
        """
        Get formatted context string for LLM prompt.
        
        Args:
            query: User query string
            k: Number of documents to retrieve
            filter: Optional metadata filter
            
        Returns:
            Formatted context string combining all retrieved chunks
        """
        chunks = self.retrieve(query, k=k, filter=filter)
        
        if not chunks:
            return "No relevant information found in the knowledge base."
        
        context_parts = [f"Relevant information from knowledge base:\n"]
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(f"\n--- Document {i} ---\n{chunk}")
        
        return "\n".join(context_parts)

