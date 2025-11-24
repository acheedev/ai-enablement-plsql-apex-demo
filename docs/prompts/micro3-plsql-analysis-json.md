# Micro-Prompt 3: "Structured Output"

## Goal

Force the model to return JSON so you can use it in automation later.

Write a prompt that takes PL/SQL code and returns:
{
  "summary": "...",
  "risks": ["...", "..."],
  "assumptions": ["...", "..."]
}

With the following constraints:
- No invented schema objects
- No invented variables
- No invented business rules
- If not enough context exists, populate fields with "UNKNOWN"

Output only JSON

---
### Prompt

```ini
[ROLE]
Act as a senior PL/SQL reviewer.

[CONTEXT]
You are analyzing PL/SQL code and must return your analysis as a JSON object.

[TASK]
- Review the provided PL/SQL code.
- Produce:
  - a concise summary of what the code does,
  - a list of potential risks the code may introduce,
  - a list of assumptions the code appears to make.

[CONSTRAINTS]
- Do not invent schema objects, tables, or columns that are not clearly present in the code.
- Do not invent new variables or business rules.
- If there is not enough context to determine something, use the string "UNKNOWN" in that position or explain the uncertainty in the "assumptions" list.
- Do not include explanations, prose, or commentary outside the JSON.
- The JSON must be syntactically valid.

[OUTPUT]
Output only a JSON object in exactly this structure:

{
  "summary": "string",
  "risks": ["string"],
  "assumptions": ["string"]
}

```
