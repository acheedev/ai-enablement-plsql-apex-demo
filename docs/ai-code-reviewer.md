# 14. AI Code Reviewer (Your First Real Deliverable)
*A complete, end-to-end PL/SQL analysis workflow — production-safe, deterministic, and ready for CI/CD.*

This is the first fully engineered AI tool in your enablement system.
It takes PL/SQL code (procedures, functions, packages, triggers), runs it through chained micro-prompts, validates outputs, and generates a clean review report.

The goal is not “chatbot reviewing code.”
The goal is a **deterministic code-analysis pipeline** with:

- stable behavior
- strict output shapes
- zero hallucinations
- clear validation layers
- governance compliance
- CI/CD compatibility

This becomes the star artifact in your interview portfolio and demo project.

---

# 14.1 System Overview
The AI Code Reviewer operates as a **multi-step workflow**:

```
PL/SQL File
↓
Step 1: Literal Summary (micro-prompt)
↓
Validator #1 (schema, format)
↓
Step 2: Issue Classification (micro-prompt)
↓
Validator #2 (categories, consistency)
↓
Step 3: Structured JSON Analysis (micro-prompt)
↓
Validator #3 (schema enforcement, no invention)
↓
Step 4 (Optional): Behavior-Preserving Refactor
↓
Validator #4 (diff checking)
↓
Step 5: Final Report Generator (Markdown)
```


Every step is isolated → no cross-task contamination.

This protects against hallucinations and ensures repeatability.

---

# 14.2 Inputs & Outputs

### **Input**
A `.sql`, `.pks`, `.pkb`, or `.pls` file.

### **Output**
Two artifacts per file:

1. **A structured JSON file**
    ```
    {
      "summary": "...",
      "risks": [...],
      "assumptions": [...],
      "categories": {
        "performance": [...],
        "logic_correctness": [...],
        ...
      }
    }
    ```

2. **A human-readable Markdown report**
    ```
    # Code Review: invoice_pkg.pkb

    ## Summary
    ...

    ## Issue Categories
    ### Performance
    - ...

    ### Logic Correctness
    - ...

    ## Risks
    - ...

    ## Assumptions
    - ...

    ## Suggested Refactor (optional)
    ...
    ```

This dual-output structure is CI-friendly **and** human-friendly.

---

# 14.3 Workflow Step Details

## **Step 1 — Literal Summary**
Micro-prompt #1.

Purpose:
- anchor the model
- reveal uncertainty
- expose missing context early

Constraints ensure:
- no inventing business rules
- no guessing intent
- no assumed tables

Validator checks:
- summary < 6 sentences
- no invented identifiers
- no speculative language

---

## **Step 2 — Issue Classification**
Micro-prompt #5.

Categories:
- performance
- error_handling
- logic_correctness
- maintainability
- security
- data_integrity
- uncertainty

Validator checks:
- only allowed categories
- no invented concepts
- no changes to the code

---

## **Step 3 — Structured JSON Analysis**
Micro-prompt #3.

Fields:
- summary
- risks[]
- assumptions[]

Validator checks:
- JSON syntax
- required keys
- no prose
- values are lists or strings
- no invented objects

---

## **Step 4 (Optional) — Behavior-Preserving Refactor**
Pattern 7.3.

Constraints:
- no behavior changes
- no SQL rewrites
- same variable names
- same exception flow
- identical logic paths

Validator checks:
- diff is structural only
- SQL unchanged
- exception blocks unchanged
- no new variables created

This step is optional in the v1 tool.
You can toggle it with a CLI flag:

--refactor


---

## **Step 5 — Final Report Generator**
A simple Python component combines the outputs into a Markdown file.

Sections:

1. Summary
2. Classification
3. Risks
4. Assumptions
5. Refactor (if enabled)

This is the file you read in GitHub or deliver in a PR.

---

# 14.4 Python Structure (Folder + Files)

In your `/scripts` directory:

```
/scripts
│
├── plsql_review.py ← main orchestrator
├── prompts.py ← loads micro-prompts & patterns
├── validator.py ← validation utilities
├── reporter.py ← Markdown generator
├── utils/
│ ├── io.py
│ ├── parsing.py
│ ├── diff.py
│ └── schema.py
```


The code is simple:
**You orchestrate → AI produces → validator approves or retries.**

We'll build these together after the doc sections.

---

# 14.5 Example Flow (Realistic)

### Input:
`invoice_pkg.pkb`

### Running the tool:

`python scripts/plsql_review.py invoice_pkg.pkb --refactor`


### Output:
```
/output/invoice_pkg_summary.json
/output/invoice_pkg_review.md
/output/invoice_pkg_refactor.sql
```


### Markdown Includes:
- a grounded summary
- structured findings
- risks & assumptions
- clear categories
- optional refactor

This is 1000x better than human-only reviews, and safer than letting an LLM freeform-review code.

---

# 14.6 CI/CD Integration (GitHub Actions)
You can add a workflow:

`/.github/workflows/plsql-review.yml`


Triggered on:
- PR
- commit
- push to dev

It runs:

1. AI summary
2. AI issue classification
3. JSON validation
4. Report generation

And posts a comment on the PR.

This is a **fully automated AI reviewer for PL/SQL**
— and you built it.

---

# 14.7 How This Becomes Your Portfolio Centerpiece
You’ll be able to demonstrate:

- prompt engineering
- workflow design
- validation logic
- PL/SQL domain knowledge
- deterministic LLM control
- responsible AI governance
- CI/CD integration
- documentation discipline

This puts you *years* ahead of other applicants.

---

# 14.8 Summary
This deliverable is your first end-to-end AI engineering tool:

- safe
- predictable
- repeatable
- validated
- documented
- CI-ready
