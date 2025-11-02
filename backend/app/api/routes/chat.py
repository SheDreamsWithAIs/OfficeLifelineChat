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
from app.agents.models import PolicyResponse
from app.core.logging_config import get_logger, log_dict_keys, log_truncated

logger = get_logger("chat_endpoint")

router = APIRouter(prefix="/chat", tags=["chat"])


def _generate_thread_id() -> str:
    """Generate a new thread ID for conversation."""
    return f"thread_{uuid.uuid4().hex[:12]}"


def _format_structured_response(result: dict) -> str:
    """
    Format structured response into readable markdown.
    
    Args:
        result: Agent result dictionary with optional structured_response
        
    Returns:
        Formatted markdown string, or None if no structured response
    """
    structured_response = result.get("structured_response")
    if not structured_response:
        return None
    
    # Handle different structured response types
    if isinstance(structured_response, PolicyResponse):
        parts = []
        if structured_response.friendly_response:
            parts.append(structured_response.friendly_response)
        if structured_response.policy_description:
            parts.append("\n\n" + structured_response.policy_description)
        if structured_response.key_points:
            parts.append("\n\n**Key Points:**")
            for point in structured_response.key_points:
                parts.append(f"\n- {point}")
        if structured_response.contact_info:
            parts.append(f"\n\n**Contact:** {structured_response.contact_info}")
        return "".join(parts)
    
    # For other structured response types, convert to JSON or string
    return str(structured_response)


def _detect_agent_type(messages: list) -> str:
    """
    Detect which agent type handled the query based on tool calls.
    
    Args:
        messages: List of messages from agent response
        
    Returns:
        Agent type string (policy, technical, billing, dad_joke) or None
    """
    # Look for tool calls in messages (reverse order to get most recent)
    for msg in reversed(messages):
        # Check if message has tool_calls attribute (OpenAI format)
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            for tool_call in msg.tool_calls:
                tool_name = tool_call.get('name', '').lower()
                # Exact match first, then substring match
                if 'handle_policy_query' in tool_name or ('policy' in tool_name and 'query' in tool_name):
                    return "policy"
                elif 'handle_technical_query' in tool_name or ('technical' in tool_name and 'query' in tool_name):
                    return "technical"
                elif 'handle_billing_query' in tool_name or ('billing' in tool_name and 'query' in tool_name):
                    return "billing"
                elif 'handle_dad_joke' in tool_name or 'dad_joke' in tool_name:
                    return "dad_joke"
        
        # Check if this is a ToolMessage - they contain the tool name in metadata
        if hasattr(msg, 'name') and msg.name:
            tool_name = msg.name.lower()
            if 'handle_policy_query' in tool_name:
                return "policy"
            elif 'handle_technical_query' in tool_name:
                return "technical"
            elif 'handle_billing_query' in tool_name:
                return "billing"
            elif 'handle_dad_joke' in tool_name:
                return "dad_joke"
    
    # Fallback: Check message content for explicit tool function names (not keywords)
    for msg in reversed(messages):
        if hasattr(msg, 'content') and msg.content:
            content = str(msg.content)
            # Only check for exact tool function names, not keywords
            if 'handle_policy_query' in content:
                return "policy"
            elif 'handle_technical_query' in content:
                return "technical"
            elif 'handle_billing_query' in content:
                return "billing"
            elif 'handle_dad_joke_request' in content:
                return "dad_joke"
    
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
        
        logger.info(f"Chat Endpoint: Received message=\"{request.message}\", thread_id={thread_id}")
        
        # Get orchestrator agent
        orchestrator = get_orchestrator()
        
        # Invoke orchestrator with user message
        logger.info("Chat Endpoint: Invoking orchestrator")
        result = orchestrator.invoke(
            {"messages": [{"role": "user", "content": request.message}]},
            config
        )
        
        # Log result structure
        log_dict_keys(logger, result, prefix="Chat Endpoint: Orchestrator result ")
        
        # Get response - prefer structured response if available
        structured_content = _format_structured_response(result)
        has_structured = structured_content is not None
        logger.info(f"Chat Endpoint: Structured response available={has_structured}")
        
        if structured_content:
            logger.info(f"Chat Endpoint: Using structured response, length={len(structured_content)} chars")
            response_content = structured_content
        else:
            logger.info("Chat Endpoint: Using message content (no structured response)")
            response_content = result["messages"][-1].content
        
        log_truncated(logger, response_content, prefix="Chat Endpoint: Final response content: ", max_chars=200)
        
        agent_type = _detect_agent_type(result["messages"])
        logger.info(f"Chat Endpoint: Detected agent_type={agent_type}")
        
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
                        thread_id=thread_id,  # Include in all chunks for consistency
                        agent_type=agent_type  # Include in all chunks for consistency
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

