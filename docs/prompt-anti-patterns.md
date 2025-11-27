# 12. Prompt Anti-Patterns (What *Not* To Do)
*A reference guide to the most common prompt failures in engineering use cases.*

Most LLM errors aren’t “model failures” — they come from **prompt design flaws**.
Anti-patterns are the structures, phrasing styles, and habits that reliably cause hallucinations, drift, incorrect reasoning, or invalid outputs.

This section lists the most dangerous anti-patterns and explains why they break deterministic workflows.

---

## 12.1 Anti-Pattern: Multi-Task Prompts
**Description:** Asking the model to do multiple unrelated tasks in one pass.

**Example:**
“Summarize this package, list risks, rewrite the code, and propose optimizations.”

**Why it fails:**
The model merges tasks, changes behavior, invents rules, or produces mixed outputs.

**Fix:**
Break it into micro-prompts → one atomic task per step.

---

## 12.2 Anti-Pattern: Vague or Open-Ended Prompts
**Description:** The model is told to “analyze,” “optimize,” or “improve” without constraints.

**Why it fails:**
Open verbs broaden the probability space → unpredictable reasoning.

**Fix:**
Specify the *dimension* of the task:
- “Refactor for readability only.”
- “Analyze for performance only.”

---

## 12.3 Anti-Pattern: Purpose-First Prompting
**Description:** Prompts that begin with “This is for engineers…” or “This will be used in training…”

**Why it fails:**
Purpose invites narrative voice, interpretation, and “use-case imagination," leading to hallucinations.

**Fix:**
Move purpose out of the prompt.
Use Role → Constraints → Task → Output shape.

---

## 12.4 Anti-Pattern: Tone / Style Directives in Engineering Prompts
**Description:** Asking for tone (“friendly”, “helpful”, “conversational”) inside code workflows.

**Why it fails:**
Tone cues imply creative writing mode → unstable output, more drift.

**Fix:**
Omit tone entirely in engineering contexts.

---

## 12.5 Anti-Pattern: Combining Instructions and Examples Inline
**Description:** Mixing rules, explanation, examples, and desired output in one block.

**Why it fails:**
The model may treat examples as required output or blend them into reasoning.

**Fix:**
Use:
- *rules at top*
- *task next*
- *output shape last*
- optionally add an “Example Output” section, but isolated.

---

## 12.6 Anti-Pattern: Under-Specifying Output Shape
**Description:** Asking for JSON without specifying required keys or format.

**Why it fails:**
The model fills gaps creatively → missing keys, added commentary, malformed JSON.

**Fix:**
Explicit schema:
Output only JSON with exact fields:
summary, risks, assumptions

---

## 12.7 Anti-Pattern: Over-Stuffing Context
**Description:** Pasting entire schemas, pages of APEX metadata, or multiple packages at once.

**Why it fails:**
Large contexts increase hallucination probability and degrade accuracy.

**Fix:**
Pass only the relevant function/procedure/package.

---

## 12.8 Anti-Pattern: Assuming the Model "Knows" Your Environment
**Description:** Saying “You know our schema”, “You know our architecture”, or “Assume the usual constraints.”

**Why it fails:**
LLMs cannot remember or infer organizational context.
This guarantees invented rules or incorrect assumptions.

**Fix:**
Explicitly provide context—or force uncertainty acknowledgement.

---

## 12.9 Anti-Pattern: Optimization Without Guardrails
**Description:** Asking the model to “optimize code,” “make this faster,” or “clean up this PL/SQL.”

**Why it fails:**
AI rewrites logic, changes exception paths, or alters SQL.

**Fix:**
State:
- behavior must be preserved
- no SQL changes
- refactor for readability only

---

## 12.10 Anti-Pattern: Hidden Ambiguity
**Description:** Prompts that leave interpretation open, such as:

- “Explain this code”
- “Review this procedure”
- “What issues do you see?”

**Why it fails:**
Ambiguity causes overreach: the model invents risks or “imagines” logic.

**Fix:**
Specify:
- exact scope (“syntax only”, “readability only”)
- exact categories
- exact analysis boundaries

---

## 12.11 Anti-Pattern: Missing Negative Constraints
**Description:** Telling the model what to do but not what *not* to do.

**Why it fails:**
Without explicit prohibitions, the model fills gaps creatively.

**Fix:**
Include negative constraints such as:
- do not invent schema objects
- do not infer unseen logic
- do not modify SQL
- if uncertain, say “UNKNOWN”

---

## 12.12 Anti-Pattern: Letting the Model Rewrite Inputs
**Description:** Asking for edits or improvements without ensuring the input stays immutable.

**Why it fails:**
The model may reorder code, remove comments, or change semantics.

**Fix:**
Forbid input mutation unless explicitly requested and scoped.

---

## 12.13 Anti-Pattern: Accepting Prose + JSON Mixed Output
**Description:** Allowing the model to output narrative explanations around machine-readable content.

**Why it fails:**
Scripts break, parsing fails, CI pipelines crash.

**Fix:**
Strict output rule: “Output JSON only.”

---

## 12.14 Anti-Pattern: Prompting Without Version Control
**Description:** Changing prompts casually inside scripts or tools.

**Why it fails:**
You get inconsistent results across time.
No reproducibility, no audit, no debugging path.

**Fix:**
Store prompts in versioned files.
Tag breaking changes.

---

## 12.15 Anti-Pattern: Overusing Examples
**Description:** Examples placed inline distort model attention and may override rules.

**Why it fails:**
Examples become unintended templates or “canonical patterns.”

**Fix:**
Use examples *sparingly* and isolate them in a separate block.

---

# 12.16 Summary
Prompt anti-patterns cause:

- hallucinations
- drift
- incorrect behavior
- mixed outputs
- invalid JSON
- invented schema
- unsafe rewrites

Avoiding these failure styles is a non-negotiable discipline in **AI systems engineering**, particularly when:

- analyzing PL/SQL
- reviewing APEX components
- generating refactors
- driving CI pipelines
- performing structured audits

Mastering the anti-patterns is as important as mastering the patterns.

