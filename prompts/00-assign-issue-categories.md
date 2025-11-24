# Micro-Prompt 5 — Assign Issue Categories

## Goal

Write a prompt that assigns issue categories to parts of a PL/SQL procedure/function/package
- stays strictly within what the code shows
- does not invent behavior
- does not hallucinate problems
- uses predefined categories
- outputs only the classification structure


And remember: micro-prompts = atomic
 This prompt should not explain issues, rewrite anything, propose fixes, or summarize.
 It should only classify.

---
### Prompt:

```ini
[ROLE]
Act as a principal PL/SQL code reviewer.

[CONTEXT]
You will be given a PL/SQL procedure, function, trigger, package specification, or package body.
Your job is to identify potential issues in the code and assign them to predefined issue categories.

[TASK]
For the provided code:
- Identify any potential issues you see.
- Assign each issue to one of the following categories:
  - performance
  - error_handling
  - logic_correctness
  - maintainability
  - security
  - data_integrity
  - uncertainty
- If you do not see any issues for a given category, return an empty list for that category.

[CONSTRAINTS]
- Stay strictly within what the code shows.
- Do not modify or rewrite the code.
- Do not invent behavior, details, variables, objects, or business rules.
- Do not infer functionality that is not explicitly present.
- If you are uncertain whether something is an issue, place it under the "uncertainty" category and state why.

[OUTPUT]
Return only a JSON object in exactly this structure:

{
  "performance": ["string"],
  "error_handling": ["string"],
  "logic_correctness": ["string"],
  "maintainability": ["string"],
  "security": ["string"],
  "data_integrity": ["string"],
  "uncertainty": ["string"]
}

Each list may be empty.
Each entry must be a short, human-readable description of a specific issue.
The JSON must be syntactically valid.

```


