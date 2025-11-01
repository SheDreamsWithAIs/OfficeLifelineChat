"""
Pure CAG (Cached-Augmented Generation) strategy.

This strategy loads static documents into memory and returns full document
content (not chunks). Documents are cached for fast access.

LangChain Version: v1.0+
"""

from pathlib import Path
from typing import Dict, List, Optional
import json


class CAGStrategy:
    """
    Pure CAG retrieval strategy - loads documents into memory cache.
    
    Suitable for static policy documents that don't change frequently
    and should be returned in full (not as chunks).
    """
    
    def __init__(self, data_directory: Optional[Path] = None):
        """
        Initialize CAG strategy.
        
        Args:
            data_directory: Path to data directory. Defaults to project data/policy/
        """
        if data_directory is None:
            # Default to policy documents directory
            project_root = Path(__file__).parent.parent.parent.parent
            data_directory = project_root / "data" / "policy"
        
        self.data_directory = Path(data_directory)
        self._cache: Dict[str, str] = {}
        self._loaded = False
    
    def load_documents(self) -> None:
        """Load all markdown documents from data directory into cache."""
        if self._loaded:
            return
        
        if not self.data_directory.exists():
            raise FileNotFoundError(f"Data directory not found: {self.data_directory}")
        
        for file_path in self.data_directory.glob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self._cache[file_path.stem] = content
            except Exception as e:
                print(f"Warning: Failed to load {file_path}: {e}")
        
        self._loaded = True
    
    def get_document(self, document_name: str) -> Optional[str]:
        """
        Get a specific document by name (without .md extension).
        
        Args:
            document_name: Name of document (e.g., 'privacy_policy')
            
        Returns:
            Document content or None if not found
        """
        self.load_documents()
        return self._cache.get(document_name)
    
    def get_all_documents(self) -> Dict[str, str]:
        """
        Get all cached documents.
        
        Returns:
            Dictionary mapping document names to content
        """
        self.load_documents()
        return self._cache.copy()
    
    def get_context(self, query: str = "") -> str:
        """
        Get all document content as context (full documents, not chunks).
        
        For CAG, we return all policy documents since they're static
        and should be available in full context.
        
        Args:
            query: Optional query (not used in CAG, but kept for interface consistency)
            
        Returns:
            Formatted string with all document contents
        """
        self.load_documents()
        
        if not self._cache:
            return "No documents loaded in cache."
        
        context_parts = ["Policy documents (full content):\n"]
        
        for doc_name, content in self._cache.items():
            context_parts.append(f"\n--- {doc_name.replace('_', ' ').title()} ---\n{content}\n")
        
        return "\n".join(context_parts)
    
    def search_documents(self, keywords: List[str]) -> str:
        """
        Search for documents containing specific keywords.
        Returns full document content if keywords match.
        
        Args:
            keywords: List of keywords to search for
            
        Returns:
            Formatted string with matching documents
        """
        self.load_documents()
        
        if not self._cache:
            return "No documents loaded in cache."
        
        matching_docs = []
        keywords_lower = [kw.lower() for kw in keywords]
        
        for doc_name, content in self._cache.items():
            content_lower = content.lower()
            if any(kw in content_lower for kw in keywords_lower):
                matching_docs.append((doc_name, content))
        
        if not matching_docs:
            return f"No documents found matching keywords: {keywords}"
        
        context_parts = [f"Documents matching {keywords}:\n"]
        
        for doc_name, content in matching_docs:
            context_parts.append(f"\n--- {doc_name.replace('_', ' ').title()} ---\n{content}\n")
        
        return "\n".join(context_parts)
    
    def clear_cache(self) -> None:
        """Clear the document cache (useful for testing)."""
        self._cache.clear()
        self._loaded = False

