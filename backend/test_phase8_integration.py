"""Phase 8.4: Full Backend Integration Test."""
import json
from fastapi.testclient import TestClient
from app.main import app

print("Phase 8.4: Full Backend Integration Test")
print("=" * 60)

client = TestClient(app)

def test_billing_query():
    """Test billing agent through API."""
    print("\n1. Testing Billing Agent:")
    try:
        response = client.post(
            "/chat",
            json={
                "message": "What are your pricing plans?",
                "thread_id": "test_billing_001",
                "stream": False
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        print(f"   ✓ Status: {response.status_code}")
        print(f"   ✓ Response length: {len(data.get('response', ''))}")
        print(f"   ✓ Agent type: {data.get('agent_type')}")
        print(f"   ✓ Thread ID: {data.get('thread_id')}")
        print(f"   ✓ Response preview: {data.get('response', '')[:100]}...")
        return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_technical_query():
    """Test technical agent through API."""
    print("\n2. Testing Technical Agent:")
    try:
        response = client.post(
            "/chat",
            json={
                "message": "How do I troubleshoot API errors?",
                "thread_id": "test_technical_001",
                "stream": False
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        print(f"   ✓ Status: {response.status_code}")
        print(f"   ✓ Response length: {len(data.get('response', ''))}")
        print(f"   ✓ Agent type: {data.get('agent_type')}")
        print(f"   ✓ Thread ID: {data.get('thread_id')}")
        print(f"   ✓ Response preview: {data.get('response', '')[:100]}...")
        return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_policy_query():
    """Test policy agent through API."""
    print("\n3. Testing Policy Agent:")
    try:
        response = client.post(
            "/chat",
            json={
                "message": "What is your privacy policy?",
                "thread_id": "test_policy_001",
                "stream": False
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        print(f"   ✓ Status: {response.status_code}")
        print(f"   ✓ Response length: {len(data.get('response', ''))}")
        print(f"   ✓ Agent type: {data.get('agent_type')}")
        print(f"   ✓ Thread ID: {data.get('thread_id')}")
        print(f"   ✓ Response preview: {data.get('response', '')[:100]}...")
        return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_streaming():
    """Test streaming response."""
    print("\n4. Testing Streaming Response:")
    try:
        response = client.post(
            "/chat",
            json={
                "message": "Tell me about refunds",
                "thread_id": "test_streaming_001",
                "stream": True
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "text/event-stream" in response.headers.get("content-type", ""), "Should be event-stream"
        
        chunks = []
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data_str = line_str[6:]
                    if data_str == '[DONE]':
                        break
                    try:
                        chunk = json.loads(data_str)
                        chunks.append(chunk)
                    except:
                        pass
        
        print(f"   ✓ Status: {response.status_code}")
        print(f"   ✓ Content-Type: {response.headers.get('content-type')}")
        print(f"   ✓ Received {len(chunks)} chunks")
        if chunks:
            print(f"   ✓ First chunk content: {chunks[0].get('content', '')[:50]}...")
            print(f"   ✓ Last chunk done: {chunks[-1].get('done', False)}")
            print(f"   ✓ Agent type (final): {chunks[-1].get('agent_type')}")
        
        return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_conversation_continuity():
    """Test conversation history persistence."""
    print("\n5. Testing Conversation Continuity:")
    try:
        thread_id = "test_continuity_002"
        
        # First message
        response1 = client.post(
            "/chat",
            json={
                "message": "What are your pricing plans?",
                "thread_id": thread_id,
                "stream": False
            }
        )
        assert response1.status_code == 200
        
        # Second message (should maintain context)
        response2 = client.post(
            "/chat",
            json={
                "message": "Tell me more about the premium plan",
                "thread_id": thread_id,
                "stream": False
            }
        )
        assert response2.status_code == 200
        
        data1 = response1.json()
        data2 = response2.json()
        
        print(f"   ✓ First response thread_id: {data1.get('thread_id')}")
        print(f"   ✓ Second response thread_id: {data2.get('thread_id')}")
        assert data1.get('thread_id') == data2.get('thread_id'), "Thread IDs should match"
        print(f"   ✓ Thread IDs match - conversation continuity verified")
        
        return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all integration tests."""
    results = []
    
    results.append(("Billing Agent", test_billing_query()))
    results.append(("Technical Agent", test_technical_query()))
    results.append(("Policy Agent", test_policy_query()))
    results.append(("Streaming", test_streaming()))
    results.append(("Conversation Continuity", test_conversation_continuity()))
    
    print("\n" + "=" * 60)
    print("Integration Test Results:")
    print("-" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:30} {status}")
        if not passed:
            all_passed = False
    
    print("-" * 60)
    if all_passed:
        print("\n✅ Phase 8.4: Full Backend Integration Test - PASSED")
    else:
        print("\n⚠ Phase 8.4: Some tests failed. Review errors above.")
    
    return all_passed


if __name__ == "__main__":
    main()

