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
from app.agents.models import PolicyResponse, TechnicalResponse, BillingResponse
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
    
    if isinstance(structured_response, TechnicalResponse):
        parts = []
        if structured_response.friendly_response:
            parts.append(structured_response.friendly_response)
        if structured_response.technical_description:
            parts.append("\n\n" + structured_response.technical_description)
        if structured_response.steps:
            parts.append("\n\n**Steps:**")
            for i, step in enumerate(structured_response.steps, 1):
                parts.append(f"\n{i}. {step}")
        if structured_response.code_examples:
            parts.append("\n\n**Code Examples:**")
            for example in structured_response.code_examples:
                parts.append(f"\n```\n{example}\n```")
        if structured_response.error_codes:
            parts.append("\n\n**Error Codes:**")
            for error in structured_response.error_codes:
                parts.append(f"\n- {error}")
        return "".join(parts)
    
    if isinstance(structured_response, BillingResponse):
        parts = []
        if structured_response.friendly_response:
            parts.append(structured_response.friendly_response)
        if structured_response.billing_description:
            parts.append("\n\n" + structured_response.billing_description)
        if structured_response.plans:
            parts.append("\n\n**Available Plans:**")
            for plan in structured_response.plans:
                if isinstance(plan, dict):
                    plan_str = "\n".join(f"- {k}: {v}" for k, v in plan.items())
                    parts.append(f"\n{plan_str}")
                else:
                    parts.append(f"\n- {plan}")
        if structured_response.payment_info:
            parts.append(f"\n\n**Payment Information:**\n{structured_response.payment_info}")
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
        
        # Handle streaming vs non-streaming
        if request.stream:
            # Stream response using LangChain's native streaming
            async def stream_response() -> AsyncIterator[str]:
                logger.info("Chat Endpoint: Starting streaming response")
                agent_type = None
                accumulated_content = ""
                
                # Stream from orchestrator - this yields chunks as they're generated
                async for chunk in orchestrator.astream(
                    {"messages": [{"role": "user", "content": request.message}]},
                    config
                ):
                    # Check if this chunk contains messages
                    if "messages" in chunk:
                        messages = chunk["messages"]
                        if messages:
                            last_message = messages[-1]
                            
                            # Detect agent type from messages if not yet detected
                            if agent_type is None:
                                agent_type = _detect_agent_type(messages)
                                if agent_type:
                                    logger.info(f"Chat Endpoint: Detected agent_type={agent_type} during streaming")
                            
                            # Get content from message if available
                            if hasattr(last_message, 'content') and last_message.content:
                                content = str(last_message.content)
                                # Only send new content (incremental)
                                if len(content) > len(accumulated_content):
                                    new_content = content[len(accumulated_content):]
                                    accumulated_content = content
                                    
                                    # Stream the new content character by character for smooth UX
                                    for char in new_content:
                                        chunk_data = ChatStreamChunk(
                                            content=char,
                                            done=False,
                                            thread_id=thread_id,
                                            agent_type=agent_type
                                        )
                                        yield f"data: {chunk_data.model_dump_json()}\n\n"
                
                # Final chunk with done flag
                final_chunk = ChatStreamChunk(
                    content="",
                    done=True,
                    thread_id=thread_id,
                    agent_type=agent_type
                )
                yield f"data: {final_chunk.model_dump_json()}\n\n"
                
                # Final signal
                yield "data: [DONE]\n\n"
                logger.info(f"Chat Endpoint: Streaming complete, total length={len(accumulated_content)} chars")
            
            return StreamingResponse(
                stream_response(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )
        else:
            # Non-streaming: invoke orchestrator
            logger.info("Chat Endpoint: Invoking orchestrator (non-streaming)")
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

