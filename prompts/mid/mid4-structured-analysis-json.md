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
