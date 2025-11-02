"""
Data ingestion pipeline for loading documents into ChromaDB.

This script processes markdown documents from the data/ directory,
chunks them, embeds them, and stores them in ChromaDB with metadata.

Usage:
    python ingest_data.py
"""

import os
from pathlib import Path
from typing import List, Dict
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent))

from app.vectorstore.chroma_client import get_chroma_client
from app.llm.providers import get_openai_embeddings


def load_documents_from_directory(directory: Path) -> List[Dict]:
    """
    Load all markdown files from a directory.
    
    Args:
        directory: Path to directory containing markdown files
        
    Returns:
        List of dictionaries with 'path', 'content', and 'filename' keys
    """
    documents = []
    
    if not directory.exists():
        print(f"Warning: Directory {directory} does not exist")
        return documents
    
    for file_path in directory.glob("*.md"):
        try:
            loader = TextLoader(str(file_path), encoding='utf-8')
            doc_content = loader.load()[0].page_content
            documents.append({
                'path': file_path,
                'content': doc_content,
                'filename': file_path.name
            })
            print(f"Loaded: {file_path.name}")
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    return documents


def chunk_documents(
    documents: List[Dict],
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List[Dict]:
    """
    Split documents into chunks.
    
    Args:
        documents: List of document dictionaries
        chunk_size: Maximum size of each chunk
        chunk_overlap: Overlap between chunks
        
    Returns:
        List of chunked documents with metadata
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunked_docs = []
    
    for doc in documents:
        chunks = text_splitter.split_text(doc['content'])
        
        for i, chunk in enumerate(chunks):
            chunked_docs.append({
                'content': chunk,
                'source_file': doc['filename'],
                'chunk_index': i,
                'total_chunks': len(chunks),
                'domain': doc.get('domain', 'unknown')
            })
        
        print(f"Chunked {doc['filename']}: {len(chunks)} chunks")
    
    return chunked_docs


def ingest_documents_to_chromadb(
    chunked_docs: List[Dict],
    collection_name: str,
    domain: str
) -> None:
    """
    Embed and store documents in ChromaDB.
    
    Args:
        chunked_docs: List of chunked document dictionaries
        collection_name: Name of ChromaDB collection
        domain: Domain category (billing, technical, policy)
    """
    client = get_chroma_client()
    vectorstore = client.create_collection(collection_name)
    
    texts = [doc['content'] for doc in chunked_docs]
    metadatas = [
        {
            'source_file': doc['source_file'],
            'chunk_index': doc['chunk_index'],
            'total_chunks': doc['total_chunks'],
            'domain': domain
        }
        for doc in chunked_docs
    ]
    
    print(f"Embedding and storing {len(texts)} chunks in collection '{collection_name}'...")
    
    vectorstore.add_texts(texts=texts, metadatas=metadatas)
    
    print(f"Successfully stored {len(texts)} chunks")


def main():
    """Main ingestion pipeline."""
    # Get data directory path
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    
    if not data_dir.exists():
        print(f"Error: Data directory not found at {data_dir}")
        return
    
    print("Starting data ingestion pipeline...")
    print(f"Data directory: {data_dir}\n")
    
    # Process each domain
    domains = {
        'billing': 'billing_documents',
        'technical': 'technical_documents',
        'policy': 'policy_documents',
        'dad_jokes': 'dad_jokes_documents'
    }
    
    total_chunks = 0
    
    for domain, collection_name in domains.items():
        domain_dir = data_dir / domain
        
        if not domain_dir.exists():
            print(f"Skipping {domain}: directory not found")
            continue
        
        print(f"\n{'='*60}")
        print(f"Processing {domain.upper()} domain")
        print(f"{'='*60}\n")
        
        # Load documents
        documents = load_documents_from_directory(domain_dir)
        
        if not documents:
            print(f"No documents found in {domain_dir}")
            continue
        
        # Add domain metadata
        for doc in documents:
            doc['domain'] = domain
        
        # Chunk documents
        chunked_docs = chunk_documents(documents)
        total_chunks += len(chunked_docs)
        
        # Store in ChromaDB
        ingest_documents_to_chromadb(chunked_docs, collection_name, domain)
        
        print(f"✓ Completed {domain} domain: {len(chunked_docs)} chunks")
    
    print(f"\n{'='*60}")
    print(f"Data ingestion complete!")
    print(f"Total chunks stored: {total_chunks}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()

