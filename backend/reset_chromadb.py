"""
Reset ChromaDB - Delete all collections and start fresh.

Usage:
    python reset_chromadb.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.vectorstore.chroma_client import get_chroma_client

def main():
    """Delete all ChromaDB collections."""
    print("Resetting ChromaDB...")
    print("=" * 60)
    
    client = get_chroma_client()
    
    # List all collections
    collections = client.list_collections()
    print(f"\nFound {len(collections)} collections:")
    for col in collections:
        print(f"  - {col}")
    
    # Delete all collections
    print("\nDeleting collections...")
    for col_name in collections:
        try:
            client.delete_collection(col_name)
            print(f"  ✓ Deleted: {col_name}")
        except Exception as e:
            print(f"  ✗ Error deleting {col_name}: {e}")
    
    # Verify deletion
    remaining = client.list_collections()
    if remaining:
        print(f"\nWarning: {len(remaining)} collections still exist:")
        for col in remaining:
            print(f"  - {col}")
    else:
        print("\n✓ All collections deleted successfully!")
    
    print("=" * 60)
    print("\nChromaDB reset complete. You can now run ingest_data.py")

if __name__ == "__main__":
    main()

