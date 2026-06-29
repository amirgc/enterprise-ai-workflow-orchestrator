# CLAUDE.md

## Project Overview

Enterprise AI Workflow Orchestrator — an AI-powered vendor onboarding system that demonstrates production-grade AI engineering patterns. This is both a learning project and a portfolio piece to showcase AI engineering skills.

## User Context

- The user is learning Python (new to it) — explain concepts, don't assume knowledge
- This is a hands-on project: the user writes the code, Claude guides and explains
- Build iteratively — one file at a time, explain what and why before writing
- This project also serves as prep for the Claude Certified Architect — Foundations exam
- The repo doubles as a portfolio piece to demonstrate AI engineering skills to employers

## What the System Does

Processes vendor onboarding requests like:
> "Onboard ABC Supplies as a new vendor. They provide office equipment. Payment terms are Net 30."

Pipeline steps: Classify request → Extract fields → Detect missing info → Retrieve policy (RAG) → Call backend tools → Create draft task → Human approval → Log metrics

## Build Plan — 6 Iterations

### Iteration 1 — Foundation & Config (CURRENT)
Files to build: `pyproject.toml`, `.env.example`, `.gitignore`, `src/__init__.py`, `src/config.py`
Teaches: Python project structure, env vars, type hints, packages

### Iteration 2 — LLM Providers
Files: `src/providers/base.py`, `src/providers/claude.py`, `src/providers/openai_provider.py`
Teaches: Anthropic SDK, OpenAI SDK, abstract base classes, provider pattern

### Iteration 3 — Prompt Engineering & Structured Outputs
Files: `src/prompts/registry.py`, `src/prompts/templates/*.txt`
Teaches: Versioned prompts, JSON schema, Pydantic models, structured extraction

### Iteration 4 — Tool Use & RAG
Files: `src/tools/registry.py`, `src/tools/compliance.py`, `src/tools/workflow.py`, `src/rag/store.py`, `src/rag/policies/*.md`
Teaches: Function calling, tool definitions, document retrieval, context injection

### Iteration 5 — Guardrails & Human-in-the-Loop
Files: `src/guardrails/validators.py`, `src/approval/gate.py`
Teaches: Input/output validation, approval workflows, safety patterns

### Iteration 6 — Observability & Evaluation
Files: `src/observability/logger.py`, `evals/runner.py`, `evals/test_cases.json`
Teaches: Metrics collection, cost tracking, eval harnesses, test-driven AI

## AI Engineering Skills Covered

| Skill | Implementation |
|---|---|
| LLM Integration | Claude + OpenAI behind a common interface |
| Prompt Engineering | Versioned prompt templates |
| Tool Use | AI calls backend tools |
| Structured Outputs | JSON schema validation |
| RAG | Policy doc retrieval |
| Evaluation | Test cases with expected results |
| Guardrails | Blocks risky/invalid actions |
| Human-in-the-Loop | Approval before execution |
| Observability | Logs latency, cost, tokens, model |

## Tech Stack

- Python 3.11+
- Anthropic SDK (Claude)
- OpenAI SDK (GPT)
- Pydantic (validation)
- python-dotenv (env vars)
- Rich (terminal output)

## Commands

```bash
# Activate venv
.venv\Scripts\activate     # Windows

# Install
pip install -e ".[dev]"

# Run
python -m src.main
```

## Repo

https://github.com/amirgc/enterprise-ai-workflow-orchestrator
