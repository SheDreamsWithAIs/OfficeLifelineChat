<!-- da437bbe-8a30-4e8e-912a-bf27ce69e84c dda348e5-62d5-41cf-8b8f-b73dee0e3708 -->
# Detailed Development Plan: Advanced Customer Service AI

## Project Folder Structure Reference

### Root Level Structure

```
OfficeLifelineChat/
├── backend/                    # Python FastAPI backend
├── frontend/                   # Next.js React frontend
├── data/                       # Mock documents and data sources
├── scripts/                    # Utility and data ingestion scripts
├── AI_docs/                    # Existing documentation (keep as-is)
├── .gitignore
├── README.md
└── .env.example                # Template for environment variables
```

### Backend Structure (backend/)

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── chat.py         # /chat endpoint with streaming
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── orchestrator.py     # Supervisor/orchestrator agent
│   │   ├── billing_agent.py    # Hybrid RAG/CAG agent
│   │   ├── technical_agent.py  # Pure RAG agent
│   │   └── policy_agent.py     # Pure CAG agent
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py            # Configuration management
│   │   ├── models.py             # Pydantic models for API
│   │   └── state.py              # LangGraph state definitions
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── rag_strategy.py     # Pure RAG implementation
│   │   ├── cag_strategy.py      # Pure CAG implementation
│   │   └── hybrid_strategy.py  # Hybrid RAG/CAG implementation
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── providers.py         # LLM provider initialization (OpenAI, Bedrock)
│   │   └── models.py            # Model selection logic
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py           # Utility functions
│   └── vectorstore/
│       ├── __init__.py
│       └── chroma_client.py     # ChromaDB client initialization and management
├── chroma_db/                  # ChromaDB persistence directory (created by ingestion script)
│   └── .gitkeep                # Keep directory in git (actual DB files gitignored)
├── ingest_data.py              # Data ingestion pipeline script (root level for easy access)
├── requirements.txt            # Python dependencies
└── .env                        # Environment variables (gitignored)
```

### Frontend Structure (frontend/)

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.jsx           # Root layout
│   │   ├── page.jsx             # Main chat page
│   │   └── globals.css          # Global styles
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatInterface.jsx
│   │   │   ├── MessageList.jsx
│   │   │   ├── MessageBubble.jsx
│   │   │   ├── ChatInput.jsx
│   │   │   └── StreamingMessage.jsx
│   │   ├── sidebar/
│   │   │   ├── Sidebar.jsx
│   │   │   └── AgentInfo.jsx
│   │   └── ui/                  # shadcn/ui components (if used)
│   └── lib/
│       ├── api.js               # API client for backend
│       └── utils.js             # Utility functions
├── public/                      # Static assets
├── package.json
├── next.config.js
├── tailwind.config.js          # Tailwind CSS configuration
└── .env.local                  # Frontend environment variables
```

### Data Structure (data/)

```
data/
├── billing/                     # Documents for billing agent
│   ├── pricing_tiers.md
│   ├── invoice_policy.md
│   └── billing_faq.md
├── technical/                   # Documents for technical agent
│   ├── api_documentation.md
│   ├── bug_reports.md
│   ├── forum_posts.md
│   └── troubleshooting_guides.md
├── policy/                      # Documents for policy agent
│   ├── terms_of_service.md
│   ├── privacy_policy.md
│   └── compliance_guidelines.md
└── README.md                    # Documentation about data sources
```

### Scripts Structure (scripts/)

```
scripts/
├── setup.sh                    # Setup script for environment
├── test_agents.py              # Testing utilities
└── validate_data.py            # Validate data ingestion
```

### Environment Variables Structure

Both `.env.example` (root) and `.env.local` (frontend) should include:

- OpenAI API key (OPENAI_API_KEY)
- AWS Bedrock API key (AWS_BEDROCK_API_KEY) - **Note**: Uses API key, not access credentials
- ChromaDB persistence path (CHROMA_DB_PATH)
- Backend API URL (for frontend) (NEXT_PUBLIC_API_URL)
- Port configurations (BACKEND_PORT, FRONTEND_PORT)

**Important Technology Notes**:

- **LangChain/LangGraph v1.0.0+**: Must use latest v1.0 patterns (create_agent(), StateGraph, etc.)
- **AWS Bedrock**: Uses API key authentication (AWS_BEDROCK_API_KEY), not access credentials
- **Breaking Changes**: v1.0 removed LCEL, deprecated patterns - use current APIs only
- **No TypeScript**: Frontend uses JavaScript (.jsx) files only

---

## Development Strategy

**Build order**: Backend → Frontend → Integration

**Validation**: Test each component immediately after creation before moving forward

**Checkpoints**: Stop and verify at each checkpoint before proceeding

---

## PHASE 1: Project Setup & Foundation (Backend)

**Goal**: Establish project structure and environment

### Step 1.1: Initialize Project Structure

- Create all folder directories per folder structure plan
- Initialize git repository
- Create `.gitignore` files (Python, Node.js, ChromaDB)
- Create root `.env.example` template

**Validation Checkpoint 1.1**:

- [ ] All directories exist
- [ ] `.gitignore` excludes `.env`, `chroma_db/`, `node_modules/`, `__pycache__/`
- [ ] Repository initialized

**Commit**: `[Phase 1 Step 1.1] Initialize project structure and directories`

### Step 1.2: Backend Python Environment

- Create `backend/requirements.txt` with initial dependencies
- Set up Python virtual environment
- Install dependencies
- Create `backend/.env` from template

**Validation Checkpoint 1.2**:

- [ ] Virtual environment activates successfully
- [ ] All packages install without errors
- [ ] LangChain and LangGraph v1.0.0+ installed (verify versions)
- [ ] Python version compatible (3.9+)

**Commit**: `[Phase 1 Step 1.2] Setup Python environment and dependencies`

### Step 1.3: Backend Core Configuration

- Create `backend/app/core/config.py` with settings management
- Set up environment variable loading
- Define base configuration classes

**Validation Checkpoint 1.3**:

- [ ] Config loads environment variables correctly
- [ ] Can access config values (test with print statements)
- [ ] Error handling for missing required vars

**Commit**: `[Phase 1 Step 1.3] Create backend configuration management`

### Step 1.4: Mock Data Preparation

- Create `data/` folder structure
- Create sample markdown files for billing, technical, and policy domains
- Document data structure in `data/README.md`

**Validation Checkpoint 1.4**:

- [ ] Sample documents exist in each category
- [ ] Documents are readable and formatted correctly
- [ ] At least 2-3 documents per category minimum

**Commit**: `[Phase 1 Step 1.4] Create mock data documents for all domains`

---

## PHASE 2: Data Pipeline & Vector Store (Backend)

**Goal**: Get ChromaDB working and data ingested

### Step 2.1: ChromaDB Setup

- Create `backend/app/vectorstore/chroma_client.py`
- Initialize ChromaDB client with persistence
- Test connection to `backend/chroma_db/` directory

**Validation Checkpoint 2.1**:

- [ ] ChromaDB client initializes without errors
- [ ] `chroma_db/` directory created on first run
- [ ] Can create a test collection and query it

### Step 2.2: Embeddings Setup

- Configure OpenAI embeddings in `backend/app/llm/providers.py`
- Test embedding generation with sample text

**Validation Checkpoint 2.2**:

- [ ] Embeddings generate successfully
- [ ] Embedding vectors have expected dimensions
- [ ] No API errors

### Step 2.3: Data Ingestion Script

- Create `backend/ingest_data.py`
- Implement document loading (markdown files)
- Implement text chunking (RecursiveCharacterTextSplitter)
- Implement embedding and storage to ChromaDB
- Add metadata tagging (document type, category)

**Validation Checkpoint 2.3**:

- [ ] Script runs without errors
- [ ] Documents are loaded and chunked
- [ ] Chunks are embedded and stored in ChromaDB
- [ ] Can query ChromaDB and retrieve relevant chunks
- [ ] Metadata is preserved (verify with sample query)

### Step 2.4: Collection Organization

- Verify separate collections or metadata filters for:
- Billing documents
- Technical documents  
- Policy documents

**Validation Checkpoint 2.4**:

- [ ] Each document type stored with correct metadata
- [ ] Can filter queries by document type
- [ ] Test retrieval: billing query returns billing docs only

---

## PHASE 3: Retrieval Strategies (Backend)

**Goal**: Implement all three retrieval strategies independently

### Step 3.1: Pure RAG Strategy

- Create `backend/app/retrieval/rag_strategy.py`
- Implement similarity search from ChromaDB
- Return retrieved document chunks

**Validation Checkpoint 3.1**:

- [ ] Can call RAG strategy with test query
- [ ] Returns relevant document chunks
- [ ] Chunks are formatted correctly for LLM context

### Step 3.2: Pure CAG Strategy

- Create `backend/app/retrieval/cag_strategy.py`
- Load static documents into memory (for Policy agent)
- Implement caching mechanism
- Return cached content

**Validation Checkpoint 3.2**:

- [ ] Static documents load into memory
- [ ] CAG returns full document content (not chunks)
- [ ] Cache persists across multiple calls

### Step 3.3: Hybrid RAG/CAG Strategy

- Create `backend/app/retrieval/hybrid_strategy.py`
- Implement initial RAG query on first call
- Cache results for subsequent calls in session
- Combine RAG retrieval with cached data

**Validation Checkpoint 3.3**:

- [ ] First call performs RAG retrieval
- [ ] Results are cached in session state
- [ ] Subsequent calls use cached data (no RAG call)
- [ ] Can verify cache is being used (logging)

---

## PHASE 4: LLM Providers & Models (Backend)

**Goal**: Set up multi-provider LLM strategy

### Step 4.1: LLM Provider Setup

- Complete `backend/app/llm/providers.py`
- Initialize OpenAI client
- Initialize AWS Bedrock client
- Test connections to both providers

**Validation Checkpoint 4.1**:

- [ ] OpenAI client works (test with simple prompt)
- [ ] AWS Bedrock client works (test with simple prompt)
- [ ] Can switch between providers programmatically
- [ ] Error handling for API failures

### Step 4.2: Model Selection Logic

- Create `backend/app/llm/models.py`
- Define model selection: Bedrock for routing, OpenAI for generation
- Create helper functions for model selection

**Validation Checkpoint 4.2**:

- [ ] Can get routing model (Bedrock - fast/cheap)
- [ ] Can get generation model (OpenAI - high quality)
- [ ] Model selection works correctly

---

## PHASE 5: LangGraph State & Core (Backend)

**Goal**: Set up LangGraph infrastructure

### Step 5.1: State Definition

- Create `backend/app/core/state.py`
- Define TypedDict for agent state (messages, context, etc.)
- Include fields for session caching (Hybrid RAG/CAG)

**Validation Checkpoint 5.1**:

- [ ] State schema is properly defined
- [ ] State can be instantiated with test data
- [ ] Type hints are correct

### Step 5.2: Checkpointing Setup

- Initialize InMemorySaver for conversation history
- Test state persistence across invocations
- Verify thread_id handling

**Validation Checkpoint 5.2**:

- [ ] Can create checkpointed graph
- [ ] State persists between calls with same thread_id
- [ ] Different thread_ids maintain separate state

---

## PHASE 6: Worker Agents (Backend) - Build One at a Time

**Goal**: Create each specialized agent independently

### Step 6.1: Policy Agent (Pure CAG) - EASIEST FIRST

- Create `backend/app/agents/policy_agent.py`
- Use `create_agent()` with CAG strategy
- Configure with OpenAI generation model
- Test with policy-related queries

**Validation Checkpoint 6.1**:

- [ ] Policy agent responds to policy queries
- [ ] Responses come from cached documents (verify source)
- [ ] Agent returns complete, formatted answers
- [ ] Test: "What is your privacy policy?"

### Step 6.2: Technical Agent (Pure RAG)

- Create `backend/app/agents/technical_agent.py`
- Use `create_agent()` with RAG strategy
- Configure with OpenAI generation model
- Test with technical queries

**Validation Checkpoint 6.2**:

- [ ] Technical agent responds to technical queries
- [ ] Responses include information from knowledge base
- [ ] RAG retrieval is working (verify chunks retrieved)
- [ ] Test: "How do I fix API errors?"

### Step 6.3: Billing Agent (Hybrid RAG/CAG)

- Create `backend/app/agents/billing_agent.py`
- Use `create_agent()` with Hybrid strategy
- Implement session-based caching
- Configure with OpenAI generation model
- Test with billing queries

**Validation Checkpoint 6.3**:

- [ ] First billing query performs RAG retrieval
- [ ] Subsequent queries use cached data (verify no RAG call)
- [ ] Responses are accurate
- [ ] Test: Multiple billing questions in sequence

---

## PHASE 7: Orchestrator Agent (Backend)

**Goal**: Create supervisor that routes to worker agents

### Step 7.1: Create Orchestrator

- Create `backend/app/agents/orchestrator.py`
- Use `create_agent()` as supervisor
- Wrap worker agents as tools using `@tool` decorator
- Configure orchestrator to use Bedrock model (fast routing)
- Create routing logic based on query analysis

**Validation Checkpoint 7.1**:

- [ ] Orchestrator can identify query type
- [ ] Routes billing queries to billing agent (verify in logs)
- [ ] Routes technical queries to technical agent
- [ ] Routes policy queries to policy agent
- [ ] Test with clear examples of each type

### Step 7.2: Multi-Agent Integration Test

- Create test script to verify full agent workflow
- Test routing accuracy
- Verify agent responses are returned to orchestrator
- Test conversation flow

**Validation Checkpoint 7.2**:

- [ ] Orchestrator routes correctly to all three agents
- [ ] Worker agent responses are properly formatted
- [ ] Full conversation maintains context
- [ ] Thread ID preserves conversation history

---

## PHASE 8: FastAPI Backend API (Backend)

**Goal**: Expose agents via REST API

### Step 8.1: Pydantic Models

- Create `backend/app/core/models.py`
- Define request/response models for `/chat` endpoint
- Include streaming response model

**Validation Checkpoint 8.1**:

- [ ] Models validate input correctly
- [ ] Models serialize output correctly

### Step 8.2: Chat Endpoint

- Create `backend/app/api/routes/chat.py`
- Implement `/chat` POST endpoint
- Integrate orchestrator agent
- Implement streaming response using FastAPI StreamingResponse
- Handle thread_id for conversation persistence

**Validation Checkpoint 8.2**:

- [ ] Endpoint accepts POST requests
- [ ] Returns streaming response
- [ ] Can test with curl/Postman
- [ ] Streaming works (tokens appear incrementally)
- [ ] Thread ID persists conversation

### Step 8.3: FastAPI App Setup

- Create `backend/app/main.py`
- Initialize FastAPI app
- Register chat route
- Add CORS middleware (for frontend connection later)
- Add error handling

**Validation Checkpoint 8.3**:

- [ ] FastAPI server starts successfully
- [ ] `/chat` endpoint accessible
- [ ] Can send test request and receive response
- [ ] CORS headers present (check with browser dev tools)
- [ ] Error responses are properly formatted

### Step 8.4: Backend Integration Test

- Test full backend flow: API → Orchestrator → Worker Agent → Response
- Test with all three agent types
- Verify streaming works end-to-end
- Test conversation continuity with thread_id

**Validation Checkpoint 8.4**:

- [ ] Full backend works for billing queries
- [ ] Full backend works for technical queries
- [ ] Full backend works for policy queries
- [ ] Streaming responses work correctly
- [ ] Conversation history maintained
- [ ] No critical errors in logs

---

## PHASE 9: Frontend Setup & Foundation

**Goal**: Initialize Next.js frontend

### Step 9.1: Next.js Project Setup

- Create Next.js project in `frontend/` directory
- Configure Tailwind CSS
- Set up project structure per folder plan
- Install dependencies

**Validation Checkpoint 9.1**:

- [ ] Next.js app runs (`npm run dev`)
- [ ] Tailwind CSS is working (test with styled component)
- [ ] Folder structure matches plan
- [ ] No build errors

### Step 9.2: Frontend Configuration

- Create `frontend/.env.local` with backend API URL
- Set up API client in `frontend/src/lib/api.js`
- Create basic fetch function (non-streaming first)

**Validation Checkpoint 9.2**:

- [ ] Environment variables load correctly
- [ ] API client can make requests to backend
- [ ] Can receive responses from backend (test with simple fetch)

---

## PHASE 10: Frontend UI Components (Visual Only)

**Goal**: Build UI components without backend integration

### Step 10.1: Core Layout Components

- Create `frontend/src/app/layout.jsx`
- Create `frontend/src/app/page.jsx` (main chat page)
- Set up basic page structure

**Validation Checkpoint 10.1**:

- [ ] Page renders without errors
- [ ] Layout is visible
- [ ] Basic structure matches design intent

### Step 10.2: Chat Components (Static)

- Create `frontend/src/components/chat/ChatInterface.jsx`
- Create `frontend/src/components/chat/MessageList.jsx`
- Create `frontend/src/components/chat/MessageBubble.jsx`
- Create `frontend/src/components/chat/ChatInput.jsx`
- Use mock data for messages (no API calls yet)

**Validation Checkpoint 10.2**:

- [ ] Chat interface displays mock messages
- [ ] Messages render correctly (user vs AI)
- Input field is visible
- Styling matches design intent (refer to mockup if needed)

### Step 10.3: Sidebar Components

- Create `frontend/src/components/sidebar/Sidebar.jsx`
- Create `frontend/src/components/sidebar/AgentInfo.jsx`
- Display static agent information

**Validation Checkpoint 10.3**:

- [ ] Sidebar renders correctly
- [ ] Agent info displays
- [ ] Responsive design works (mobile/desktop)
- [ ] Matches design intent

### Step 10.4: UI Polish

- Style components with Tailwind
- Ensure responsive design
- Add loading states (visual only)
- Test on different screen sizes

**Validation Checkpoint 10.4**:

- [ ] UI looks polished and professional
- [ ] Responsive on mobile and desktop
- [ ] All visual components render correctly
- [ ] No layout issues

---

## PHASE 11: Frontend-Backend Integration

**Goal**: Connect frontend to backend API

### Step 11.1: API Integration (Non-Streaming First)

- Update `frontend/src/lib/api.js` with chat endpoint
- Connect ChatInterface to API
- Test with non-streaming responses first
- Handle errors gracefully

**Validation Checkpoint 11.1**:

- [ ] Frontend can send messages to backend
- [ ] Backend responses appear in chat
- [ ] Error handling works (test with backend offline)
- [ ] Loading states display correctly

### Step 11.2: Streaming Implementation

- Create `frontend/src/components/chat/StreamingMessage.jsx`
- Implement streaming response handling
- Update API client to handle Server-Sent Events or streaming
- Display tokens as they arrive

**Validation Checkpoint 11.2**:

- [ ] Streaming works - tokens appear incrementally
- [ ] Streaming message component displays correctly
- [ ] Full message appears after streaming completes
- [ ] No UI glitches during streaming

### Step 11.3: Conversation Persistence

- Implement thread_id management
- Store thread_id in session/localStorage
- Pass thread_id with each API request
- Maintain conversation history

**Validation Checkpoint 11.3**:

- [ ] Conversations persist across page refreshes (if using localStorage)
- [ ] Thread IDs are managed correctly
- [ ] Backend maintains conversation context
- [ ] Can start new conversation (clear thread_id)

### Step 11.4: Agent Type Display

- Display which agent responded (billing, technical, policy)
- Update UI to show agent badges/labels
- Style different agents differently if desired

**Validation Checkpoint 11.4**:

- [ ] Agent type is displayed correctly
- [ ] Different agents show different visual indicators
- [ ] Agent info updates based on response

---

## PHASE 12: Testing & Final Polish

**Goal**: End-to-end testing and documentation

### Step 12.1: End-to-End Testing

- Test all three agent types through full UI
- Test conversation flows
- Test error scenarios (API down, invalid input)
- Test streaming in various conditions

**Validation Checkpoint 12.1**:

- [ ] All three agents work through UI
- [ ] Conversations flow naturally
- [ ] Errors are handled gracefully
- [ ] Streaming is reliable

### Step 12.2: Documentation

- Create comprehensive `README.md`
- Document setup instructions
- Document environment variables
- Add code comments where needed

**Validation Checkpoint 12.2**:

- [ ] README has clear setup steps
- [ ] Someone else could follow README and run project
- [ ] Environment variables are documented
- [ ] Code has helpful comments

### Step 12.3: Final Validation Against Rubric

- Verify multi-agent system works ✓
- Verify all three worker agents implemented ✓
- Verify FastAPI endpoint works ✓
- Verify frontend UI is polished ✓
- Verify streaming works ✓
- Verify multi-LLM strategy (Bedrock routing, OpenAI generation) ✓
- Verify data ingestion pipeline works ✓
- Verify all three retrieval strategies implemented ✓

**Final Checkpoint**:

- [ ] Run through rubric checklist
- [ ] All MVP requirements met
- [ ] Project ready for submission

---

## Critical Validation Rules

1. **Never proceed to next phase without passing checkpoint**
2. **Test immediately after creating each component**
3. **If checkpoint fails, fix before continuing**
4. **Document any deviations from plan**
5. **Keep backend working before starting frontend**

## Time-Saving Strategies

- Test incrementally (don't build everything then test)
- Use simple test cases first, complex later
- Log everything during development (easier debugging)
- Commit working checkpoints (easier rollback)
- One agent at a time, validate each before next