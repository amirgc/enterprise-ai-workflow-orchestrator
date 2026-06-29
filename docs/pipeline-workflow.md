# Vendor Onboarding Pipeline — Workflow Diagram

## Pipeline Flow

```
User Input: "Onboard ABC Supplies from Germany, office equipment, Net 30"
                             │ 
                             ▼
╔══════════════════════════════════════════════════════════════════╗
║  STEP 1: VALIDATE INPUT (guardrails/validators.py)               ║
║                                                                  ║
║  • Check for prompt injection patterns                           ║
║  • Check for SQL/XSS keywords                                    ║
║  • Check length limits                                           ║
║                                                                  ║
║  No LLM — pure Python regex + string matching                    ║
╚══════════════════════════╤═══════════════════════════════════════╝
                           │ PASS
                           ▼
╔══════════════════════════════════════════════════════════════════╗
║  STEP 2: CLASSIFY REQUEST                                        ║
║                                                                  ║
║  ┌─────────────────┐     ┌──────────────┐     ┌─────────────┐    ║
║  │ PromptRegistry  │───▶ │ LLM CALL    │────▶│ parse_llm_  │    ║
║  │ .get("classify  │     │ provider     │     │ json() +    │    ║
║  │  _v1", text=...)│     │ .generate()  │     │ Pydantic    │    ║
║  └─────────────────┘     └──────────────┘     └─────────────┘    ║
║                                                                  ║
║  Input:  "Classify this request into a category..."              ║
║  Output: {"category": "new_vendor", "confidence": 0.95}          ║
║                                                                  ║
║  LLM USED HERE — classifies the request type                     ║
╚══════════════════════════╤═══════════════════════════════════════╝
                           │ ClassificationResult
                           ▼
╔══════════════════════════════════════════════════════════════════╗
║  STEP 3: EXTRACT VENDOR FIELDS                                   ║
║                                                                  ║
║  ┌─────────────────┐     ┌──────────────┐     ┌─────────────┐    ║
║  │ PromptRegistry  │────▶│ LLM CALL     │────▶│ parse_llm_ │    ║
║  │ .get("extract   │     │ provider     │     │ json() +    │    ║
║  │  _v1", text=...)│     │ .generate()  │     │ Pydantic    │    ║ 
║  └─────────────────┘     └──────────────┘     └─────────────┘    ║
║                                                                  ║
║  Input:  "Extract vendor info from this request..."              ║
║  Output: {"vendor_name": "ABC Supplies", "country": "Germany"}   ║
║                                                                  ║
║  LLM USED HERE — pulls structured fields from free text          ║
╚══════════════════════════╤═══════════════════════════════════════╝
                           │ VendorInfo
                           ▼
╔══════════════════════════════════════════════════════════════════╗
║  STEP 4: RAG — SEARCH POLICIES (rag/store.py)                    ║
║                                                                  ║
║  Query: "office equipment Germany Net 30"                        ║
║         │                                                        ║
║         ▼                                                        ║
║  ┌──────────────────────┐                                        ║
║  │ PolicyStore.search()  │──▶ keyword match against .md files   ║
║  │                       │                                       ║
║  │ vendor_onboarding.md  │                                       ║
║  │ payment_policy.md     │                                       ║
║  │ compliance_reqs.md    │                                       ║
║  └──────────────────────┘                                        ║
║                                                                  ║
║  No LLM — pure Python keyword search                             ║
║  (In production, you'd use embeddings + vector DB here)          ║
╚══════════════════════════╤═══════════════════════════════════════╝
                           │ PolicyMatch[]
                           ▼
╔══════════════════════════════════════════════════════════════════╗
║  STEP 5: COMPLIANCE CHECK (tools/compliance.py)                  ║
║                                                                  ║
║  ToolRegistry.execute("check_vendor_compliance", {               ║
║      vendor_name, country, vendor_type                           ║
║  })                                                              ║
║         │                                                        ║
║         ▼                                                        ║
║  Result: { passed, requires_review, issues }                     ║
║                                                                  ║
║  No LLM — pure Python business rules                             ║
║  (In production, LLM would DECIDE to call this tool)             ║
╚══════════════════════════╤═══════════════════════════════════════╝
                           │ compliance result
                           ▼
╔══════════════════════════════════════════════════════════════════╗
║  STEP 6: HUMAN APPROVAL (approval/gate.py)                       ║
║                                                                  ║
║  Shows action, reason, and details to a human reviewer           ║
║  Human types: y (approve) or n (reject)                          ║
║                                                                  ║
║  No LLM — terminal input() from a human                          ║
╚══════════════════════════╤═══════════════════════════════════════╝
                           │ APPROVED
                           ▼
╔══════════════════════════════════════════════════════════════════╗
║  STEP 7: CREATE VENDOR RECORD (tools/workflow.py)                ║
║                                                                  ║
║  ToolRegistry.execute("create_vendor_record", {                  ║
║      vendor_name, vendor_type, payment_terms,                    ║
║      contact_email, country                                      ║
║  })                                                              ║
║         │                                                        ║
║         ▼                                                        ║
║  Result: { vendor_id, status: "pending_approval" }               ║
║                                                                  ║
║  No LLM — pure Python (in production: database/ERP API call)     ║
╚══════════════════════════╤═══════════════════════════════════════╝
                           │ vendor record
                           ▼
╔══════════════════════════════════════════════════════════════════╗
║  STEP 8: METRICS REPORT (observability/logger.py)                ║
║                                                                  ║
║  Reports: total calls, tokens, cost, latency per step            ║
║                                                                  ║
║  No LLM — pure Python aggregation                                ║
╚══════════════════════════════════════════════════════════════════╝
```

## Where LLM Is Used vs Not

| Step | LLM? | Why / Why not |
|---|---|---|
| 1. Validate input | No | Regex patterns — fast, deterministic, no cost |
| 2. Classify request | **Yes** | Free text to category. Only an LLM can understand natural language intent |
| 3. Extract fields | **Yes** | Free text to structured JSON. LLM understands "Net 30" is payment terms |
| 4. RAG search | No | Keyword matching (production would use embeddings, still not LLM) |
| 5. Compliance check | No | Business rules are deterministic — "Iran = blocked" doesn't need AI |
| 6. Human approval | No | Human decision — the whole point is a person decides |
| 7. Create record | No | Database operation — deterministic |
| 8. Metrics | No | Math aggregation — deterministic |

## Key Design Principle

Only 2 out of 8 steps use the LLM. Good AI engineering means using LLMs **only where you need language understanding** and keeping everything else as cheap, fast, deterministic code.

## What Would Change in Production

| Current (demo) | Production upgrade |
|---|---|
| Keyword search in RAG | Embeddings + vector DB (Pinecone, ChromaDB) |
| Our code calls tools directly | LLM decides which tools to call via function calling |
| Terminal input() for approval | Slack/email/web UI approval workflow |
| Print metrics to terminal | Send to Datadog, Grafana, etc. |
| Simulated vendor record | Write to real database or ERP API |
| Single provider hardcoded | Load balancing across providers with failover |

## File Map

```
src/
├── config.py                    # Settings from .env
├── main.py                      # Orchestrator — wires all steps
├── providers/
│   ├── base.py                  # Abstract LLM interface
│   ├── claude.py                # Anthropic SDK implementation
│   └── openai_provider.py       # OpenAI SDK implementation
├── prompts/
│   ├── registry.py              # Loads and fills prompt templates
│   └── templates/
│       ├── classify_v1.txt      # Classification prompt
│       └── extract_v1.txt       # Extraction prompt
├── models/
│   └── schemas.py               # Pydantic models for LLM output validation
├── rag/
│   ├── store.py                 # Policy document search
│   └── policies/                # Company policy .md files
├── tools/
│   ├── registry.py              # Tool name → function mapping
│   ├── compliance.py            # Compliance check tool
│   └── workflow.py              # Vendor creation tool
├── guardrails/
│   └── validators.py            # Input/output safety checks
├── approval/
│   └── gate.py                  # Human-in-the-loop approval
└── observability/
    └── logger.py                # Token, cost, latency tracking

evals/
├── runner.py                    # Evaluation harness
└── test_cases.json              # Test inputs with expected outputs
```
