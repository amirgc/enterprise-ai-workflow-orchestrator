# Enterprise AI Workflow Orchestrator

An AI-powered vendor onboarding system that demonstrates production-grade AI engineering patterns. Built as a hands-on learning project covering the full stack of skills needed to architect LLM-powered enterprise applications.

## What This System Does

The AI processes vendor onboarding requests like:

> "Onboard ABC Supplies as a new vendor. They provide office equipment. Payment terms are Net 30. Need W9, tax classification, bank info, and finance approval."

The system then:
1. **Classifies** the request type
2. **Extracts** structured fields (vendor name, category, payment terms)
3. **Detects** missing information
4. **Retrieves** internal policy from documents (RAG)
5. **Decides** which backend tools to call
6. **Creates** a draft workflow task
7. **Requires human approval** before final submission
8. **Logs** prompt version, model, latency, token usage, confidence, and cost

## AI Engineering Skills Demonstrated

| Skill | How This Project Proves It |
|---|---|
| **LLM Integration** | Claude + OpenAI providers behind a common interface |
| **Prompt Engineering** | Versioned prompt templates with A/B tracking |
| **Tool Use** | AI decides which backend tools to call |
| **Structured Outputs** | JSON schema validation on every LLM response |
| **RAG** | Retrieves policy docs before answering |
| **Evaluation** | Test cases with expected results and scoring |
| **Guardrails** | Blocks risky or invalid actions |
| **Human-in-the-Loop** | Approval gate before workflow execution |
| **Observability** | Logs latency, cost, tokens, model per step |

## Build Iterations

This project is built in 6 iterations, each adding a layer:

### Iteration 1 — Foundation & Config
> *Learn: Python project structure, environment variables, type hints*

Set up the project skeleton, configuration, and `.env` handling.

### Iteration 2 — LLM Providers
> *Learn: Anthropic SDK, OpenAI SDK, abstract base classes, the provider pattern*

Build a common interface so the pipeline can swap between Claude and OpenAI.

### Iteration 3 — Prompt Engineering & Structured Outputs
> *Learn: Versioned prompts, JSON schema, Pydantic models, structured extraction*

Create versioned prompt templates and force the LLM to return validated JSON.

### Iteration 4 — Tool Use & RAG
> *Learn: Function calling, tool definitions, document retrieval, context injection*

Give the AI backend tools to call and policy documents to reference.

### Iteration 5 — Guardrails & Human-in-the-Loop
> *Learn: Input/output validation, approval workflows, safety patterns*

Add validation rules that block risky actions and require human sign-off.

### Iteration 6 — Observability & Evaluation
> *Learn: Metrics collection, cost tracking, eval harnesses, test-driven AI*

Log every LLM call and build a test suite that scores the system's accuracy.

## Project Structure

```
enterprise-ai-workflow-orchestrator/
├── README.md
├── pyproject.toml
├── .env.example
├── .gitignore
├── src/
│   ├── config.py              # Settings & env vars
│   ├── providers/             # LLM provider abstraction
│   │   ├── base.py            # Abstract interface
│   │   ├── claude.py          # Anthropic Claude
│   │   └── openai_provider.py # OpenAI GPT
│   ├── prompts/               # Versioned prompt templates
│   │   ├── registry.py        # Prompt management
│   │   └── templates/         # .txt prompt files
│   ├── tools/                 # Backend tool definitions
│   │   ├── registry.py        # Tool routing
│   │   ├── compliance.py      # Compliance checks
│   │   └── workflow.py        # Workflow task creation
│   ├── rag/                   # Document retrieval
│   │   ├── store.py           # Simple doc store
│   │   └── policies/          # Policy documents
│   ├── guardrails/            # Validation & safety
│   │   └── validators.py
│   ├── approval/              # Human-in-the-loop
│   │   └── gate.py
│   ├── observability/         # Logging & metrics
│   │   └── logger.py
│   └── pipeline.py            # Orchestrates everything
├── evals/                     # Evaluation test suite
│   ├── runner.py
│   └── test_cases.json
└── docs/
    └── architecture.md
```

## Tech Stack

- **Python 3.11+**
- **Anthropic SDK** — Claude API integration
- **OpenAI SDK** — GPT API integration
- **Pydantic** — Data validation and structured outputs
- **python-dotenv** — Environment variable management
- **Rich** — Terminal output formatting

## Getting Started

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/enterprise-ai-workflow-orchestrator.git
cd enterprise-ai-workflow-orchestrator

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -e ".[dev]"

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the pipeline
python -m src.main
```

## License

MIT
