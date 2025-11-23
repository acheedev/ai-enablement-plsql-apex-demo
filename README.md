# AI Enablement Toolkit – Oracle / APEX Demo

This repository is a **demo project** showing how an Oracle / APEX development team can use AI tools (ChatGPT, GitHub Copilot, etc.) in a **structured, repeatable way**.

The focus is not on “AI hype,” but on **practical workflows**:

- Reviewing PL/SQL packages for style, safety, and performance
- Generating unit-test skeletons for PL/SQL procedures and functions
- Assisting with APEX API design and documentation
- Helping with data migration planning and validation
- Writing better incident postmortems and runbooks

The code and prompts here are intentionally small and focused so they can be:
- Walked through live in an interview
- Used as a template inside a real team
- Extended into a full internal AI enablement program

---

## Contents

### `/samples`

Small Oracle-centric examples used by the prompts and scripts:

- `plsql_invoice_pkg.sql` – simple invoice package with a few procedures/functions.
- `apex_page_export_example.sql` – trimmed export of an APEX page (for structure, not realism).

### `/prompts`

Reusable, documented prompts for AI tools. Each file is a single “prompt pattern” with sections:

- **Context** – what the AI should assume
- **Input** – what the user provides (code, logs, requirements)
- **Tasks** – what the AI should produce
- **Constraints** – rules (no schema changes, no guessing, etc.)

Examples:

- `01-code-review-plsql.md` – code review assistant for PL/SQL.
- `02-generate-unit-tests-plsql.md` – generate utPLSQL-style test skeletons.
- `03-apex-api-design.md` – help design REST-style APIs backing APEX pages.
- `04-data-migration-assistant.md` – plan/check migrations between schemas.
- `05-incident-postmortem-writer.md` – turn raw notes into a structured postmortem.

### `/scripts`

Example Python scripts that call an AI API to automate some of these workflows:

- `ai_review_plsql.py` – reads a PL/SQL file and asks the model for a structured review.
- `ai_generate_tests.py` – reads a PL/SQL package and asks the model to propose unit-test cases.

These scripts are intentionally minimal and designed for discussion, not production.

### `/workflows`

- `example-review-workflow.md` – shows how a team could wire this into Git + code review:
  - Developer pushes a branch
  - Optional pre-review AI pass using a script
  - Human code review augmented with AI suggestions

---

## How to use this demo in an interview

Some talking points you can use:

- **Strategy** – “Most teams don’t need ‘AI magic’; they need repeatable workflows. I built prompt patterns and simple scripts that plug into their existing Oracle / APEX practices.”
- **Governance** – “All prompts emphasize safety: don’t hallucinate schema changes, flag uncertainty, keep changes reviewable.”
- **Leverage** – “The goal is to make seniors faster and juniors more capable, not replace anyone.”
- **Extendability** – “This repo is a seed. In a real role I’d expand this into a prompt library, internal docs, GitHub Actions, and training sessions.”

This project is meant to show how I would **bring AI into a real Oracle / APEX shop** without chaos: small tools, strong guardrails, and a clear path to adoption.
