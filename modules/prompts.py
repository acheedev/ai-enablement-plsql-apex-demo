"""
Prompt builders for the PL/SQL review pipeline.
Each function returns (system_prompt, user_prompt).
"""

ANALYSIS_JSON_TEMPLATE = """
{
  "summary": "string",
  "risks": ["string"],
  "assumptions": ["string"]
}
""".strip()

CLASSIFICATION_JSON_TEMPLATE = """
{
  "performance": ["string"],
  "error_handling": ["string"],
  "logic_correctness": ["string"],
  "maintainability": ["string"],
  "security": ["string"],
  "data_integrity": ["string"],
  "uncertainty": ["string"]
}
""".strip()


def build_summary_prompt(code: str) -> tuple[str, str]:
    system_prompt = (
        "You are a principal PL/SQL code reviewer. "
        "You must be literal, conservative, and avoid any guessing or invention. "
        "If the code's intent is unclear, you must state that explicitly."
    )

    user_prompt = f"""
[ROLE]
Act as a principal PL/SQL code reviewer.

[CONTEXT]
You will be given a PL/SQL procedure, function, trigger, package specification, or package body.
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
No code, no examples, no commentary.

[INPUT CODE]
{code}
""".strip()

    return system_prompt, user_prompt


def build_classification_prompt(code: str) -> tuple[str, str]:
    system_prompt = (
        "You are a principal PL/SQL code reviewer. "
        "Your job is to identify potential issues and classify them into predefined categories. "
        "You must not invent schema, variables, or business rules."
    )

    user_prompt = f"""
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

{{
  "performance": ["string"],
  "error_handling": ["string"],
  "logic_correctness": ["string"],
  "maintainability": ["string"],
  "security": ["string"],
  "data_integrity": ["string"],
  "uncertainty": ["string"]
}}

Each list may be empty.
Each entry must be a short, human-readable description of a specific issue.
The JSON must be syntactically valid.

[INPUT CODE]
{code}
""".strip()

    return system_prompt, user_prompt


def build_analysis_prompt(code: str) -> tuple[str, str]:
    system_prompt = (
        "You are a senior PL/SQL reviewer. "
        "You must analyze the provided code and emit a JSON object with summary, risks, and assumptions. "
        "You must not invent schema objects, variables, or business rules."
    )

    user_prompt = f"""
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
- If there is not enough context to determine something, either:
  - include a plain-text explanation in the "assumptions" list, or
  - use the string "UNKNOWN".
- Do NOT include any comments in the JSON (no '//' or '/* ... */' anywhere).
- Do NOT append explanations after values (e.g. no `"UNKNOWN"  // explanation`).
  Any explanation must be inside the string itself, like: "UNKNOWN: not enough context to determine X".
- Do not include explanations, prose, or commentary outside the JSON.
- The JSON must be syntactically valid.

[OUTPUT]
Output only a JSON object in exactly this structure:

{{
  "summary": "string",
  "risks": ["string"],
  "assumptions": ["string"]
}}

Each item in "risks" and "assumptions" must be a plain JSON string value, with no trailing comments or extra tokens of any kind.

[INPUT CODE]
{code}
""".strip()

    return system_prompt, user_prompt

def build_refactor_prompt(code: str) -> tuple[str, str]:
    system_prompt = (
        "You are a principal PL/SQL engineer. "
        "You refactor code to improve readability and maintainability without changing behavior. "
        "You must preserve all business logic, SQL statements, and exception behavior exactly."
    )

    user_prompt = f"""
[ROLE]
Act as a principal PL/SQL engineer.

[CONTEXT]
You will be given a PL/SQL procedure, function, trigger, package specification, or package body.
Your job is to refactor the code for readability and maintainability while preserving behavior.

[TASK]
- Improve formatting, structure, and readability.
- Group related logic where appropriate.
- Clarify indentation and whitespace.
- Keep all SQL statements, conditions, and exception logic semantically identical.

[CONSTRAINTS]
- Do NOT change any business rules.
- Do NOT change the meaning of any IF, CASE, or loop conditions.
- Do NOT add or remove SQL statements.
- Do NOT add or remove exception handlers.
- Do NOT rename variables, parameters, or procedures.
- Do NOT introduce new dependencies or packages.
- You may only change layout, formatting, and non-semantic structure.
- If refactoring would require changing behavior, do NOT do it; keep the original structure instead.

[OUTPUT]
Return only the full refactored PL/SQL code.
Do not include explanations, comments, or markdown—code only.

[INPUT CODE]
{code}
""".strip()

    return system_prompt, user_prompt

def build_json_correction_prompt(raw_json: str, template: str) -> tuple[str, str]:
    system_prompt = (
        "You are a strict JSON repair assistant. "
        "Your only job is to take malformed JSON and output syntactically valid JSON that matches the given template. "
        "You must not change the meaning of any values, only fix formatting and syntax."
    )

    user_prompt = f"""
[ROLE]
Act as a JSON repair tool.

[CONTEXT]
You are given JSON-like output that may contain syntax errors (such as comments, trailing commas,
or invalid tokens). You must correct it to be valid JSON that matches the target structure.

[TASK]
- Take the provided raw JSON-like text.
- Fix only the syntax and formatting to make it valid JSON.
- Preserve the meaning and text of each value as much as possible.
- Ensure the result matches the structure described in the template.

[CONSTRAINTS]
- Do NOT add new fields.
- Do NOT remove fields that are present and valid.
- Do NOT change field names.
- Do NOT convert strings to other types.
- Do NOT include any comments (no '//' or '/* ... */').
- Do NOT include any explanation or text outside the JSON.
- Output must be syntactically valid JSON.

[TEMPLATE]
{template}

[RAW_JSON]
{raw_json}
""".strip()

    return system_prompt, user_prompt
