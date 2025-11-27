# 13. AI System Architecture for PL/SQL & APEX Teams
*A practical blueprint for building a safe, stable, enterprise-grade AI enablement system inside an Oracle-centric environment.*

Most enterprises want AI, but they don’t know how to integrate it safely with:

- PL/SQL codebases
- APEX applications
- database governance
- CI/CD pipelines
- secure data boundaries

This section provides an architecture that is realistic, safe, and implementable by a small team.

---

# 13.1 Core Goals of the System
This architecture ensures:

- **deterministic LLM output**
- **zero hallucinations in code workflows**
- **no invented schema or logic**
- **strict validation gates**
- **clear, reusable prompts**
- **CI/CD compatibility**
- **enterprise governance and auditability**
- **Oracle-safe integration patterns**

The system transforms LLMs from a “chat tool” into a **structured engineering assistant**.

---

# 13.2 High-Level Architecture
The system has five layers:


| Layer 1| Prompt Library (Micro-Prompts + Patterns) |
|:-------| :---------------------------------------------------|
| Layer 2| Workflow Engine (Chained steps, validation gates) |
| Layer 3| Validation Layer (JSON, schema, anti-hallucination)|
| Layer 4| Integration Layer (PL/SQL, APEX, GitHub, CI/CD) |
| Layer 5| Governance Layer (access, logging, boundaries) |


Each layer isolates risk and enforces deterministic behavior.

---

# 13.3 Layer 1: Prompt Library (Your Foundation)
Your repo contains the **three levels** of prompting:

### **1) Micro-Prompts (atomic units)**
- summary
- classification
- structured JSON analysis
- refactor (behavior-preserving)
- transformation

These are “compiler phases.”

### **2) Prompt Patterns (Section 7)**
Reusable templates for:

- safe summarization
- issue extraction
- documentation extraction
- test-design
- risk analysis
- code-to-doc
- comment-only rewrites

### **3) Workflow Blueprints (Section 11)**
Full end-to-end processes (PL/SQL review, APEX documentation, SQL optimizer, etc.)

This library is the **brain** of the system.

---

# 13.4 Layer 2: Workflow Engine
The workflow engine is a small Python script (or set of scripts) that:

- runs the prompt chain
- passes outputs step-to-step
- handles failures
- enforces strict output formats
- retries on malformed output
- logs all steps

A typical workflow chain:
```
Step 1: Summary (micro-prompt)<br >
Step 2: Classification (micro-prompt)<br >
Step 3: Structured JSON analysis (micro-prompt)<br >
Step 4: Optional refactor (pattern)<br >
Step 5: Produce final report<br >
```


This structure:

- reduces drift
- isolates hallucinations
- improves stability
- enables debugging

This design replaces “single giant prompts” with **modular, predictable orchestration**.

---

# 13.5 Layer 3: Validation Layer
Every workflow step feeds into a **validator** before continuing.

### Validation includes:

- JSON syntax check
- schema check (required keys)
- no invented variables (regex match against input)
- no invented tables, columns, or packages
- no commentary outside JSON
- output token budget check
- behavioral diff detection (for refactors)

### If validation fails?
The engine:

1. Requests correction using a micro-prompt:
   - “Correct the output to satisfy the schema without adding new information.”
2. Falls back to a simpler prompt if needed.
3. Logs the failure for audit.

This layer makes the system **fail-safe**, not fail-open.

---

# 13.6 Layer 4: Integration Layer (PL/SQL, APEX, GitHub, CI/CD)
This layer connects the AI system to real engineering environments.

## **GitHub Integration**
- PR review bots
- diffs analyzed via micro-prompts
- comments generated via structured templates
- optional risk classification

## **PL/SQL Integration**
- input = .sql, .pkb, .pks files
- output = JSON + Markdown reports
- optional: refactored code

## **APEX Integration**
- page exports
- component catalogs
- page flows
- validations
- processes

AI produces:

- documentation
- risk reports
- summaries
- test cases

## **CI/CD Integration**
- run code review workflows during builds
- block on invalid JSON or hallucinations
- produce review artifacts as build outputs

This is where the system becomes *practical*.

---

# 13.7 Layer 5: Governance Layer
This is the security + safety layer:

### **Access Control**
- approved models only (Azure OpenAI, OCI, Bedrock)
- no public endpoints
- controlled API keys

### **Data Boundaries**
- no production data
- no sensitive PII
- masked logs only

### **Logging & Audit**
For every workflow:

- timestamp
- model version
- prompt version
- input hash
- output hash
- success/failure state

### **Policy Enforcement**
- no rewriting behavior without explicit authorization
- SQL cannot be modified unless in a refactor step
- APEX logic cannot be inferred

This ensures compliance and reduces organizational risk.

---

# 13.8 Reference Repository Structure
```
ai-enablement/
│
├── /docs/
│ ├── ai-foundations-cheatsheet.md
│ ├── prompt-patterns.md
│ ├── ai-governance.md
│ ├── llm-debugging.md
│ ├── failure-resistant-workflows.md
│ ├── ai-system-architecture.md ← (this file)
│
├── /prompts/
│ ├── micro/
│ ├── patterns/
│ ├── workflows/
│
├── /scripts/
│ ├── plsql_review.py
│ ├── apex_docgen.py
│ ├── validator.py
│
├── /examples/
│ ├── plsql/
│ ├── apex/
│
└── /ci/
├── github_actions.yml
├── model_config.json
```



This repo layout is professional and interview-ready.

---

# 13.9 How This Architecture Helps You in Interviews
Hiring managers see:

- governance discipline
- engineering-grade prompting
- clear workflows
- structured validation
- understanding of risks
- Oracle/APEX alignment
- reproducible processes
- DevOps-style design applied to AI

This is the **exact** gap in the job market right now.

---

# 13.10 Summary
This architecture gives you:

- a complete AI enablement system
- tuned for PL/SQL, APEX, Oracle workflows
- deterministic, safe, and audit-ready
- with guardrails + validation
- using your micro-prompts, patterns, and blueprints
- and ready for CI/CD integration

This is the backbone of your **AI Enablement Portfolio**.

