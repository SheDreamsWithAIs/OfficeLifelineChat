"""
Chat API endpoint for multi-agent customer service.

LangChain Version: v1.0+
"""

import uuid
from typing import AsyncIterator
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.core.models import ChatRequest, ChatStreamChunk, ErrorResponse
from app.agents.orchestrator import get_orchestrator

router = APIRouter(prefix="/chat", tags=["chat"])


def _generate_thread_id() -> str:
    """Generate a new thread ID for conversation."""
    return f"thread_{uuid.uuid4().hex[:12]}"


def _detect_agent_type(messages: list) -> str:
    """
    Detect which agent type handled the query based on tool calls.
    
    Args:
        messages: List of messages from agent response
        
    Returns:
        Agent type string (policy, technical, billing) or None
    """
    # Look for tool calls in messages
    for msg in messages:
        # Check if message has tool_calls attribute (OpenAI format)
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            for tool_call in msg.tool_calls:
                tool_name = tool_call.get('name', '').lower()
                if 'policy' in tool_name:
                    return "policy"
                elif 'technical' in tool_name:
                    return "technical"
                elif 'billing' in tool_name:
                    return "billing"
        
        # Check message content for tool usage hints
        if hasattr(msg, 'content') and msg.content:
            content_lower = str(msg.content).lower()
            if 'handle_policy_query' in content_lower or 'policy' in content_lower:
                return "policy"
            elif 'handle_technical_query' in content_lower or 'technical' in content_lower:
                return "technical"
            elif 'handle_billing_query' in content_lower or 'billing' in content_lower:
                return "billing"
    
    return None


@router.post("", response_model=None)
async def chat_endpoint(request: ChatRequest):
    """
    Chat endpoint that routes queries to appropriate specialist agents.
    
    Supports both streaming and non-streaming responses.
    Uses thread_id for conversation persistence.
    
    Args:
        request: ChatRequest with message, thread_id, and stream flag
        
    Returns:
        StreamingResponse if stream=True, else ChatResponse
    """
    try:
        # Get or generate thread_id
        thread_id = request.thread_id or _generate_thread_id()
        config = {"configurable": {"thread_id": thread_id}}
        
        # Get orchestrator agent
        orchestrator = get_orchestrator()
        
        # Invoke orchestrator with user message
        result = orchestrator.invoke(
            {"messages": [{"role": "user", "content": request.message}]},
            config
        )
        
        # Get response
        response_content = result["messages"][-1].content
        agent_type = _detect_agent_type(result["messages"])
        
        # Handle streaming vs non-streaming
        if request.stream:
            # Return streaming response
            async def stream_response() -> AsyncIterator[str]:
                # Stream response in chunks (word-based chunking for simplicity)
                # In production, you might want to use LangChain's native streaming
                words = response_content.split()
                total_words = len(words)
                
                for i, word in enumerate(words):
                    is_last = (i == total_words - 1)
                    chunk = ChatStreamChunk(
                        content=word + (" " if not is_last else ""),
                        done=is_last,
                        thread_id=thread_id if is_last else None,  # Only send thread_id on last chunk
                        agent_type=agent_type if is_last else None  # Only send agent_type on last chunk
                    )
                    yield f"data: {chunk.model_dump_json()}\n\n"
                
                # Final signal to indicate completion
                yield "data: [DONE]\n\n"
            
            return StreamingResponse(
                stream_response(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )
        else:
            # Return non-streaming response
            from app.core.models import ChatResponse
            return ChatResponse(
                response=response_content,
                thread_id=thread_id,
                agent_type=agent_type
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        )

