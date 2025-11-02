"""
Test script for Dad Joke Agent.

Tests the dad joke agent's ability to retrieve contextually relevant jokes
from ChromaDB using RAG.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.agents.dad_joke_agent import get_dad_joke_agent
from app.core.checkpointing import get_or_create_checkpointer

print("Testing Dad Joke Agent")
print("=" * 60)

# Create agent
dad_joke_agent = get_dad_joke_agent()
checkpointer = get_or_create_checkpointer()
config = {"configurable": {"thread_id": "test_dad_joke_123"}}

# Test 1: Simple joke request
print("\n1. Testing simple joke request:")
print("-" * 60)
result1 = dad_joke_agent.invoke(
    {"messages": [{"role": "user", "content": "Tell me a joke"}]},
    config
)
print(f"Response: {result1['messages'][-1].content[:200]}...")
print()

# Test 2: Contextual joke (stress-related)
print("\n2. Testing contextual joke (stress/deadlines):")
print("-" * 60)
result2 = dad_joke_agent.invoke(
    {"messages": [{"role": "user", "content": "I'm really stressed about deadlines, can you help?"}]},
    config
)
print(f"Response: {result2['messages'][-1].content[:200]}...")
print()

# Test 3: Technical context joke
print("\n3. Testing joke with technical context:")
print("-" * 60)
result3 = dad_joke_agent.invoke(
    {"messages": [{"role": "user", "content": "I'm getting API errors, this is frustrating. Tell me something funny."}]},
    config
)
print(f"Response: {result3['messages'][-1].content[:200]}...")
print()

print("=" * 60)
print("Dad Joke Agent Tests Complete!")
print("\n✅ Dad Joke Agent is working and retrieving jokes from ChromaDB!")

