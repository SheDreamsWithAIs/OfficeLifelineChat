"""
Test dad joke agent through the FastAPI endpoint.
"""

import requests
import json

API_URL = "http://localhost:8000"

print("Testing Dad Joke Agent via API")
print("=" * 60)

# Test 1: Non-streaming joke request
print("\n1. Testing non-streaming joke request:")
print("-" * 60)
response1 = requests.post(
    f"{API_URL}/chat",
    json={
        "message": "Tell me a joke",
        "thread_id": "test_api_joke_789",
        "stream": False
    }
)

if response1.status_code == 200:
    data = response1.json()
    print(f"Status: {response1.status_code}")
    print(f"Agent Type: {data.get('agent_type')}")
    print(f"Response: {data.get('response', '')[:200]}...")
    print()
else:
    print(f"Error: {response1.status_code}")
    print(response1.text)
    print()

# Test 2: Contextual joke (stress)
print("\n2. Testing contextual joke (stress about deadlines):")
print("-" * 60)
response2 = requests.post(
    f"{API_URL}/chat",
    json={
        "message": "I'm really stressed about deadlines, can you help?",
        "thread_id": "test_api_joke_789",
        "stream": False
    }
)

if response2.status_code == 200:
    data = response2.json()
    print(f"Status: {response2.status_code}")
    print(f"Agent Type: {data.get('agent_type')}")
    print(f"Response: {data.get('response', '')[:200]}...")
    print()
else:
    print(f"Error: {response2.status_code}")
    print(response2.text)
    print()

# Test 3: Streaming joke request
print("\n3. Testing streaming joke request:")
print("-" * 60)
response3 = requests.post(
    f"{API_URL}/chat",
    json={
        "message": "I need something funny about meetings",
        "thread_id": "test_api_joke_789",
        "stream": True
    },
    stream=True
)

if response3.status_code == 200:
    print(f"Status: {response3.status_code}")
    print("Streaming chunks:")
    chunks = []
    for line in response3.iter_lines():
        if line:
            line_str = line.decode('utf-8')
            if line_str.startswith('data: '):
                data_str = line_str[6:]
                if data_str == '[DONE]':
                    break
                try:
                    chunk = json.loads(data_str)
                    chunks.append(chunk)
                    if len(chunks) <= 3:  # Show first 3 chunks
                        print(f"  Chunk {len(chunks)}: {chunk.get('content', '')[:50]}...")
                except:
                    pass
    
    if chunks:
        full_content = ''.join([c.get('content', '') for c in chunks])
        agent_type = chunks[-1].get('agent_type')
        print(f"\nFull response: {full_content[:200]}...")
        print(f"Agent Type: {agent_type}")
    print()
else:
    print(f"Error: {response3.status_code}")
    print(response3.text)
    print()

print("=" * 60)
print("API Tests Complete!")
if response1.status_code == 200 and response1.json().get('agent_type') == 'dad_joke':
    print("✅ Dad Joke Agent working through API!")
else:
    print("⚠️ Check the responses above for issues")

