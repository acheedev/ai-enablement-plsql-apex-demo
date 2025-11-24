# Micro-Prompt 4: "Summarize With Guardrails" (Refined)

## Goal

Write a micro-prompt that forces the model to produce a short, literal, accurate summary of a piece of PL/SQL code without:
- guessing behavior
- inventing details
- adding logic
- inferring domain knowledge
- skipping uncertain areas

This summary micro-prompt will later become the first step of your AI review pipeline.

---
### Prompt:

```ini
[ROLE]
Act as a principal PL/SQL code reviewer.

[CONTEXT]
You will be given a PL/SQL procedure, function, trigger, package spec, or package body.
Your job is to summarize only what the code explicitly shows.

[TASK]
Produce a short, literal, and accurate summary of what the code does and what its structure reveals.
Do not analyze or critique — summarize only.

[CONSTRAINTS]
- Do not guess behavior.
- Do not invent details, variables, objects, or business rules.
- Do not infer intent or domain knowledge.
- Do not add logic or interpretation.
- If any part of the code is unclear or under-specified, explicitly state “UNCERTAIN” for that portion.
- Reference only what is directly present in the input code.
- The summary must be strictly factual and free of embellishment.

[OUTPUT]
Provide one short paragraph (3–5 sentences) containing only the summary.
No code, no examples, no commentary, no acceptance checks.

```