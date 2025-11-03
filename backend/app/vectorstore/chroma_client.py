"""
ChromaDB client for vector store operations.

LangChain Version: v1.0+
Documentation Reference: https://docs.langchain.com/oss/python/langchain/vectorstores
"""

import os
from pathlib import Path
from typing import Optional
import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from app.core.config import get_settings


class ChromaDBClient:
    """Client for managing ChromaDB vector store with persistence."""
    
    def __init__(self, collection_name: Optional[str] = None):
        """
        Initialize ChromaDB client.
        
        Args:
            collection_name: Optional collection name. If None, uses default collection.
        """
        self.settings = get_settings()
        self.persist_directory = Path(self.settings.chroma_db_path)
        
        # Ensure directory exists
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize embeddings (will be set when needed)
        self.embeddings: Optional[OpenAIEmbeddings] = None
        self.collection_name = collection_name or "documents"
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
    def get_embeddings(self) -> OpenAIEmbeddings:
        """
        Get or create OpenAI embeddings instance.
        
        Returns:
            OpenAIEmbeddings: Configured embeddings model
        """
        if self.embeddings is None:
            self.embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small",  # Cost-effective model
                api_key=self.settings.openai_api_key
            )
        return self.embeddings
    
    def get_vectorstore(self, collection_name: Optional[str] = None) -> Chroma:
        """
        Get or create a Chroma vector store.
        
        Args:
            collection_name: Collection name. Uses instance default if not provided.
            
        Returns:
            Chroma: LangChain Chroma vector store instance
        """
        collection = collection_name or self.collection_name
        embeddings = self.get_embeddings()
        
        vectorstore = Chroma(
            client=self.client,
            collection_name=collection,
            embedding_function=embeddings,
            persist_directory=str(self.persist_directory)
        )
        
        return vectorstore
    
    def create_collection(self, collection_name: str, metadata: Optional[dict] = None) -> Chroma:
        """
        Create a new collection in ChromaDB.
        
        Args:
            collection_name: Name of the collection to create
            metadata: Optional metadata for the collection
            
        Returns:
            Chroma: New vector store instance
        """
        embeddings = self.get_embeddings()
        
        vectorstore = Chroma(
            client=self.client,
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=str(self.persist_directory)
        )
        
        return vectorstore
    
    def list_collections(self) -> list[str]:
        """
        List all collections in ChromaDB.
        
        Returns:
            List of collection names
        """
        collections = self.client.list_collections()
        return [col.name for col in collections]
    
    def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a collection.
        
        Args:
            collection_name: Name of collection to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            self.client.delete_collection(name=collection_name)
            return True
        except Exception as e:
            print(f"Error deleting collection {collection_name}: {e}")
            return False


# Global client instance
_chroma_client: Optional[ChromaDBClient] = None


def get_chroma_client(collection_name: Optional[str] = None) -> ChromaDBClient:
    """
    Get or create global ChromaDB client instance.
    
    Args:
        collection_name: Optional collection name
        
    Returns:
        ChromaDBClient: Configured client instance
    """
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = ChromaDBClient(collection_name=collection_name)
    return _chroma_client

