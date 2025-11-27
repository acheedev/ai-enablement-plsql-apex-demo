# **The Twelve Laws of Prompt Design**

*Hard rules for building reliable, deterministic, enterprise-grade prompts.*

These principles come from thousands of hours of applied LLM work.
Follow them, and your prompts will behave consistently under pressure.

<br />
<br />

---

## **Law 1 — One Task per Prompt**

If you ask the model to do multiple things, it will blend them.
Micro-prompts prevent scope explosion and make outputs predictable.

---

## **Law 2 — Define the Role Explicitly**

The model imitates the role you assign.
“Act as a senior PL/SQL reviewer” gives you a different reasoning pattern than “Act as a tutor.”

---

## **Law 3 — Specify the Output Shape Exactly**

Structured formats (JSON, bullets, tables, numbered steps) force consistent outputs.
Models are excellent at filling containers — give them a container.

---

## **Law 4 — Add Negative Constraints**

Telling the model what *not* to do is as important as telling it what to do.

Examples:

* “Do not invent schema objects.”
* “Do not modify code.”
* “Do not infer beyond input.”

---

## **Law 5 — Limit Reasoning Length**

Long responses drift.
Short responses stay on-task.

Use limits such as:

* “Under 5 sentences.”
* “One short paragraph.”
* “Maximum 10 bullet points.”

---

## **Law 6 — Demand Explicit Uncertainty**

Models will guess unless instructed otherwise.

Add:

* “If unsure, say ‘UNKNOWN.’”
* “List uncertainties explicitly.”

---

## **Law 7 — Provide Context, Never Assumptions**

Give the model relevant information up front.
Do not rely on it to “know what you mean.”

Context anchors reduce hallucinations.

---

## **Law 8 — Make the Prompt Self-Contained**

If a prompt relies on implied instructions, the model will drift.
All rules must be in the prompt itself — not in your head.

---

## **Law 9 — Reduce Ambiguity to Zero**

Ambiguous instructions create unpredictable output.
Be literal, precise, and explicit.

Example:
Instead of “optimize this,” use “Refactor for readability without altering behavior.”

---

## **Law 10 — Prefer Checklists Over Open Instructions**

Models follow lists exceptionally well.
A numbered list guarantees step-by-step processing.

---

## **Law 11 — Require Validation or Self-Checks**

Ending a prompt with a verification step forces the model to confirm it followed your instructions.

Examples:

* “Before returning the output, check for any invented details.”
* “Verify that the JSON is valid.”

---

## **Law 12 — Never Mix Instruction and Content Carelessly**

Separating prompt logic from user-provided code/content reduces confusion.

Use section headers like:


[ROLE]
[CONTEXT]
[TASK]
[CONSTRAINTS]
[OUTPUT]
[INPUT CODE BELOW]


This prevents the model from misinterpreting your instructions as code to analyze.

---

# **Summary**

These twelve laws are your guardrails.
Every high-quality prompt you build will follow at least 8–10 of them.
As your projects grow, these laws ensure stability, reliability, and predictable behavior — the exact qualities enterprises require in AI workflows.