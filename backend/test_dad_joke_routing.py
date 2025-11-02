"""
Test dad joke routing through orchestrator.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.agents.orchestrator import get_orchestrator
from app.core.checkpointing import get_or_create_checkpointer

print("Testing Dad Joke Routing Through Orchestrator")
print("=" * 60)

orchestrator = get_orchestrator()
checkpointer = get_or_create_checkpointer()
config = {"configurable": {"thread_id": "test_routing_456"}}

# Test 1: Direct joke request
print("\n1. Testing direct joke request:")
print("-" * 60)
result1 = orchestrator.invoke(
    {"messages": [{"role": "user", "content": "Tell me a dad joke"}]},
    config
)
print(f"Response: {result1['messages'][-1].content[:300]}...")
print()

# Test 2: Stress-related joke request
print("\n2. Testing stress-related joke request:")
print("-" * 60)
result2 = orchestrator.invoke(
    {"messages": [{"role": "user", "content": "I'm overwhelmed with meetings, I need something funny"}]},
    config
)
print(f"Response: {result2['messages'][-1].content[:300]}...")
print()

# Check agent type detection
print("\n3. Checking agent type detection:")
print("-" * 60)
from app.api.routes.chat import _detect_agent_type
agent_type = _detect_agent_type(result1['messages'])
print(f"Detected agent type: {agent_type}")
print()

print("=" * 60)
print("Routing Tests Complete!")
if agent_type == "dad_joke":
    print("✅ Orchestrator correctly routes to dad joke agent!")
else:
    print(f"⚠️ Agent type detected as: {agent_type} (expected: dad_joke)")

