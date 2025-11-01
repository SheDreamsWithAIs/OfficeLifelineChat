# How Retrieval Strategies Connect to Agents

## Overview

Each specialized agent uses a retrieval strategy to get relevant information before generating a response. The strategies are wrapped as **tools** that agents can call using LangChain v1.0's `@tool` decorator pattern.

## Architecture Flow

```
User Query → Orchestrator Agent → Routes to Worker Agent → 
  ↓
Worker Agent calls Retrieval Tool → 
  ↓
Retrieval Strategy retrieves info → 
  ↓
Tool returns context → 
  ↓
Agent uses context to generate response → 
  ↓
Response returned to user
```

## Strategy-to-Agent Mapping

### 1. Technical Support Agent → Pure RAG Strategy

**Collection**: `technical_documents`
**Strategy**: `RAGStrategy`

**How it works**:
- Agent receives technical query (e.g., "How do I fix API errors?")
- Agent calls a `search_technical_docs` tool
- Tool uses `RAGStrategy` to:
  1. Query ChromaDB `technical_documents` collection
  2. Retrieve top-k relevant chunks (e.g., troubleshooting guides, API docs)
  3. Return formatted context
- Agent uses retrieved context + LLM to generate informed response

**Example tool**:
```python
@tool
def search_technical_docs(query: str) -> str:
    """Search technical documentation, bug reports, and troubleshooting guides."""
    rag = RAGStrategy('technical_documents', k=3)
    context = rag.get_context(query)
    return context
```

### 2. Policy & Compliance Agent → Pure CAG Strategy

**Directory**: `data/policy/`
**Strategy**: `CAGStrategy`

**How it works**:
- Agent receives policy query (e.g., "What is your privacy policy?")
- Agent calls a `get_policy_documents` tool
- Tool uses `CAGStrategy` to:
  1. Load static policy documents from memory cache (already loaded at startup)
  2. Return full document content (not chunks - policies should be seen in full)
  3. No vector search needed - fast retrieval from cache
- Agent uses full policy documents to give accurate, complete answers

**Example tool**:
```python
@tool
def get_policy_documents(query: str = "") -> str:
    """Get policy documents (Terms of Service, Privacy Policy, Compliance guidelines)."""
    cag = CAGStrategy()  # Loads from data/policy/
    context = cag.get_context(query)  # Returns all documents
    return context
```

### 3. Billing Support Agent → Hybrid RAG/CAG Strategy

**Collection**: `billing_documents`
**Strategy**: `HybridRAGCAGStrategy`

**How it works**:
- **First query** (e.g., "What are your pricing tiers?"):
  - Agent calls `search_billing_info` tool
  - Tool uses `HybridRAGCAGStrategy` to:
    1. Perform RAG retrieval from ChromaDB (gets relevant billing chunks)
    2. Cache results in session state
    3. Return context
  - Agent generates response using retrieved billing info
  
- **Subsequent queries** (e.g., "What's the payment policy?"):
  - Agent calls same tool
  - Tool uses `HybridRAGCAGStrategy` to:
    1. Check session cache
    2. Return cached results (NO RAG call - faster!)
    3. Uses same billing context from first query
  - Agent generates response using cached context

**Why Hybrid?**
- Billing info doesn't change frequently
- First query retrieves comprehensive billing context
- Follow-up billing questions can use same context
- Faster responses for subsequent queries
- Reduces API calls to ChromaDB

**Example tool**:
```python
@tool
def search_billing_info(query: str, runtime: ToolRuntime) -> str:
    """Search billing information including pricing, invoices, and payment policies."""
    # Get session cache from runtime state
    session_cache = runtime.state.get("session_cache", {})
    
    hybrid = HybridRAGCAGStrategy('billing_documents', k=3)
    context = hybrid.get_context(query, session_cache)
    
    # Update session cache in state (if needed)
    runtime.state["session_cache"] = session_cache
    
    return context
```

## Implementation Details

### Tools as LangChain Tools

Each retrieval strategy will be wrapped as a `@tool` decorated function:

```python
from langchain.tools import tool

@tool
def retrieval_tool(query: str, ...) -> str:
    """Tool description that agent uses to decide when to call."""
    strategy = RetrievalStrategy(...)
    context = strategy.get_context(query, ...)
    return context
```

### Agent Creation Pattern

Agents will be created using `create_agent()` with their retrieval tools:

```python
from langchain.agents import create_agent

technical_agent = create_agent(
    model="openai:gpt-4o-mini",
    tools=[search_technical_docs],  # Uses RAGStrategy
    system_prompt="You are a technical support specialist...",
    name="technical_support_agent"
)

policy_agent = create_agent(
    model="openai:gpt-4o-mini",
    tools=[get_policy_documents],  # Uses CAGStrategy
    system_prompt="You are a compliance specialist...",
    name="policy_compliance_agent"
)

billing_agent = create_agent(
    model="openai:gpt-4o-mini",
    tools=[search_billing_info],  # Uses HybridRAGCAGStrategy
    system_prompt="You are a billing support specialist...",
    name="billing_support_agent"
)
```

### Session State Management

For the Hybrid strategy, session cache will be stored in LangGraph state:

- Access via `runtime.state` in tools
- Persists across agent invocations within same conversation
- Cleared when new conversation starts (new thread_id)

## Key Benefits

1. **Pure RAG (Technical)**: Dynamic, always fresh - good for changing technical docs
2. **Pure CAG (Policy)**: Fast, complete - good for static policy documents
3. **Hybrid (Billing)**: Best of both - retrieve once, cache for follow-ups

## Next Steps

When implementing agents (Phase 6), we'll:
1. Create tool functions wrapping each strategy
2. Pass tools to `create_agent()` for each worker agent
3. Configure system prompts to guide agents on when/how to use tools
4. Test each agent independently before integration

