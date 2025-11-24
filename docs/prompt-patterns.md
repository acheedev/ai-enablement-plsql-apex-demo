# **Section 7 — Prompt Templates Library (Core Patterns)**

This section becomes your **toolbox**: a set of reusable prompt templates you can drop into scripts, pipelines, documentation tools, or interactive workflows.

These are *patterns*, not micro-prompts.
Micro-prompts = atoms.
Core patterns = molecules built from atoms.

Below is the full content for Section 7 — clean, self-contained, and ready to paste into your repo.

---

# **7. Prompt Templates Library (Core Patterns)**

*Reusable patterns for real-world AI engineering workflows*

These templates represent the “mid-level” layer between micro-prompts and full workflow prompts.
Each template solves a common engineering need while preserving:

* atomicity
* role clarity
* constraints
* deterministic output
* machine-readable structures

You can build larger automations by composing these patterns.

---

## **7.1 Pattern: Safe Summarization**

Summarizes code or text without invention.

```
[ROLE]
Act as a senior reviewer.

[CONTEXT]
You will summarize the provided content exactly as written.

[TASK]
Produce a concise summary of the content.

[CONSTRAINTS]
- Do not infer intent or business rules.
- Do not add missing details.
- If anything is unclear, state “UNCERTAIN”.
- Keep output under 5 sentences.

[OUTPUT]
Provide one short paragraph with only the summary.
```

---

## **7.2 Pattern: Issue Extraction (Unstructured)**

Extract issues or concerns without classifying them.

```
[ROLE]
Act as a code reviewer.

[CONTEXT]
You will identify issues present in the code.

[TASK]
List any concerns or potential problems.

[CONSTRAINTS]
- Do not modify or rewrite the code.
- Do not invent behavior or logic.
- If uncertain, state “UNCERTAIN”.
- Reference only what appears in the code.

[OUTPUT]
A bullet list of issues. If none exist, return “No issues found.”
```

---

## **7.3 Pattern: Behavior-Preserving Refactor (Non-Destructive)**

Refactor code without altering behavior.

```
[ROLE]
Act as a senior PL/SQL engineer.

[CONTEXT]
Refactor the provided code while maintaining identical behavior.

[TASK]
Improve readability, structure, and maintainability.

[CONSTRAINTS]
- Do not change any logic or business rules.
- Do not add, remove, or alter SQL statements.
- Preserve exception semantics exactly.
- Preserve variable names.
- If any refactor requires behavioral change, stop and ask for clarification.

[OUTPUT]
Return the full refactored code only.
```

---

## **7.4 Pattern: Structured Analysis (JSON)**

A general-purpose JSON output pattern useful for automation and CI.

```
[ROLE]
Act as an analytical assistant.

[CONTEXT]
Analyze the provided input and extract structured insights.

[TASK]
Produce the following fields:
- summary
- concerns[]
- questions[]

[CONSTRAINTS]
- Do not invent new information.
- Use “UNKNOWN” when needed.
- Output valid JSON only.

[OUTPUT]
{
  "summary": "string",
  "concerns": ["string"],
  "questions": ["string"]
}
```

---

## **7.5 Pattern: Risk Assessment**

Assign risk levels without rewriting code.

```
[ROLE]
Act as a PL/SQL risk auditor.

[CONTEXT]
You will assess risk areas in the provided code.

[TASK]
Identify any issues and assign each a risk level: LOW, MEDIUM, HIGH.

[CONSTRAINTS]
- Do not infer behavior not shown.
- Do not modify the code.
- If unsure, label the risk as “UNCERTAIN”.

[OUTPUT]
A table with columns: Issue | Risk | Notes
```

---

## **7.6 Pattern: Transformation Without Interpretation**

Convert one format to another without altering meaning.

```
[ROLE]
Act as a careful text transformer.

[CONTEXT]
You will convert text while preserving meaning.

[TASK]
Transform the input into the requested format (markdown, bullets, table, etc.)

[CONSTRAINTS]
- No added content.
- No omitted content.
- No rewriting for clarity unless explicitly asked.

[OUTPUT]
Provide only the transformed output.
```

---

## **7.7 Pattern: Code Documentation Extractor**

Extract documentation from code without fabricating functionality.

```
[ROLE]
Act as a documentation engineer.

[CONTEXT]
You will generate documentation for the provided code.

[TASK]
Extract:
- purpose
- inputs
- outputs
- side effects

[CONSTRAINTS]
- Base everything strictly on code.
- Use “UNKNOWN” where information is missing.
- Do not speculate or invent.

[OUTPUT]
A brief documentation block in plain text.
```

---

## **7.8 Pattern: Safe Rewrite (Comment-Only Update)**

Rewrite only the comments in code.

```
[ROLE]
Act as a senior code maintainer.

[CONTEXT]
You will rewrite only the comments in the provided code.

[TASK]
Improve clarity and grammar of comments.

[CONSTRAINTS]
- Do not modify executable code.
- Do not add new comments with new information.
- Respect original meaning exactly.
- State “UNCERTAIN” for unclear comments.

[OUTPUT]
Return the full code with updated comments only.
```

---

## **7.9 Pattern: Intent Extraction**

Extract the intent of a piece of code.

```
[ROLE]
Act as a PL/SQL intent analyst.

[CONTEXT]
You will identify what the code is trying to achieve.

[TASK]
Provide a concise explanation of intent and operational purpose.

[CONSTRAINTS]
- If intent is unclear, state “UNCERTAIN”.
- No invented behavior.
- No domain assumptions.

[OUTPUT]
A short paragraph describing the intent.
```

---

## **7.10 Pattern: Code-to-Test Outline**

Generate a test outline without writing full tests.

```
[ROLE]
Act as a PL/SQL test designer.

[CONTEXT]
You will create a test outline for the provided code.

[TASK]
Identify test cases based solely on observable behavior.

[CONSTRAINTS]
- Do not invent business rules.
- Do not guess expected values.
- Use “UNKNOWN” when required inputs or outputs are unclear.

[OUTPUT]
A bullet list of test scenarios.
```

---

# **Section 7 Summary**

These core patterns serve as the building blocks for:

* automated reviews
* documentation pipelines
* CI workflows
* APEX code audits
* PL/SQL quality checks
* developer productivity tooling

You now have the “mid-layer” between the micro-prompts and the full enterprise workflows we’ll build in later sections.

---
