# **AI Foundations Cheatsheet**

*Core principles for controlling LLMs in engineering workflows*

---

## **1. Why LLMs Predict Text, Not Truth**

LLMs do not store facts.
They generate output by predicting the **next most probable token** based on patterns learned during training.
They imitate plausible answers — not verified truth.
Accuracy emerges only when the prompt constrains the model’s prediction space tightly enough.

**Implication:**
LLMs are powerful pattern machines, not knowledge guarantees.
Precision comes from *your* constraints, not the model’s “memory.”

---

## **2. Role Framing Controls Tone and Reasoning**

When you give the model a role, you influence the patterns it draws from.

Examples:

* *Senior PL/SQL reviewer* → cautious, literal, detail-focused
* *Auditor* → skeptical, rule-enforcing
* *Tutor* → explanatory, step-by-step
* *Creative writer* → imaginative, loose constraints

The role shapes the model’s mental posture and biases the reasoning style.

**Implication:**
Always anchor the model in the **correct professional identity** before asking for structured or sensitive output.

---

## **3. Structure Controls Output Shape**

LLMs are excellent at filling predefined containers.

Examples:

* JSON → structured analysis
* bullet points → concise list
* tables → matrix of relationships
* code blocks → syntax-aware text
* numbered steps → linear reasoning

If you define the shape clearly, the model will fit its reasoning into that shape.

**Implication:**
Use strong structure when you need reliability, determinism, or machine-readable output.

---

## **4. Constraints Stop Hallucinations**

Hallucinations occur when the model fills in missing details to “complete a pattern.”
Constraints block this behavior by narrowing the allowable prediction space.

Effective constraints include:

* “Do not invent schema objects.”
* “If unsure, say ‘UNKNOWN.’”
* “Do not infer behavior not explicitly shown.”
* “Only reference elements present in the input.”
* “Ask clarifying questions before assuming.”

**Implication:**
Strict constraints reduce bullshit.
They transform the model from a storyteller into a disciplined assistant.

---

Here’s **Section 5** — clean, sharp, and fully aligned with tomorrow’s agenda.
Add this directly under Section 4 in your cheatsheet.

---

## **5. Prompt Failure Modes (and How to Neutralize Them)**

LLMs fail in predictable, diagnosable ways.
If you understand the failure mode, you can design prompts that *block* it before it happens.

---

### **5.1 Hallucination**

**What it is:**
The model invents details (tables, business rules, logic, facts) because it tries to “complete the pattern” even when the pattern doesn’t exist.

**Why it happens:**
LLMs optimize for *plausibility*, not accuracy.

**How to neutralize it:**

* Use explicit negativity constraints: “Do **not** invent schema objects.”
* Use uncertainty defaults: “If unsure, return ‘UNKNOWN.’”
* Require grounding: “Reference only what appears in the provided code.”
* Add a “check-your-work” step: “List any statements you are uncertain about.”

---

### **Example:**


> ❌ Bad prompt (hallucination bait)


“Explain what this procedure does, including all business rules and edge cases. Suggest improvements and describe how it integrates with the rest of the billing system.”

What can go wrong:

- “Integrates with the rest of the billing system” → model might hallucinate:

- “It updates payments and customers tables”

- “It sends email notifications to users”

- “It logs to a central audit log package”

None of that is in the code.

<br />

✅ ***Using your Summarize micro-prompt (Micro-Prompt 4)***

Because you say:

- “Do not invent details, objects, or business rules.”

- “Reference only what is directly present.”

- “If unclear, say UNCERTAIN.”

You get something like:

> “This procedure applies a percentage discount to the total_amount of an invoice identified by p_invoice_id, updates the updated_at timestamp, and when the discount exceeds 50%, inserts an audit record into invoice_audit. Any exception raised is caught by a WHEN OTHERS handler that currently does nothing (TODO comment indicates error handling should be improved).”

No talk about customers, payments, emails, global audit systems.
It’s locked to what’s in the code.

Failure mode: hallucination<br />
Defense: negative constraints + UNCERTAIN rule in the summary prompt.
<br />
<br />

---

### **5.2 Reasoning Drift**

**What it is:**
As responses get longer, the model wanders away from the original task or starts making assumptions.

**Why it happens:**
Long sequences increase error propagation; the model “forgets” instructions.

**How to neutralize it:**

* Keep tasks atomic (micro-prompts).
* Use short, rigid structures (JSON, bullets, numbered steps).
* Restate constraints in the output contract.
* Limit length: “Keep the output under 10 lines,” “One paragraph,” etc.

---

### **5.3 Overconfidence**

**What it is:**
The model presents uncertainty as fact — confident but wrong.

**Why it happens:**
The model has no internal “confidence meter.”
It predicts text patterns that *sound confident* because training favored that style.

**How to neutralize it:**

* Require explicit uncertainty labeling:
  “If any conclusion is unclear, flag it as ‘UNCERTAIN.’”
* Ask for alternative interpretations when appropriate.
* Add a verification step:
  “List any claims that rely on assumptions.”
* Disallow invention:
  “Do not guess. Do not assume. Do not infer beyond provided input.”

---

### **Example:**


> ❌ Bad prompt: “Is this procedure safe and correct? Answer yes or no and explain.”



The model is heavily biased toward “Yes, looks fine” unless something is hilariously broken. It might gloss over:

- unvalidated p_percent (negative? 200%?)

- silent WHEN OTHERS

- potential for total_amount < 0

You could get something like:

    “Yes, this procedure is safe and correct. It applies a discount and logs high discounts.”

Confident nonsense...

<br />

✅ ***Your Classification micro-prompt (Micro-Prompt 5)***

You’re not asking “is this safe?” — you’re forcing it to label issues by category:

- error_handling: “WHEN OTHERS handler swallows all exceptions with null”

- logic_correctness: “No validation on p_percent; negative or extreme values may corrupt totals”

- data_integrity: “total_amount may become negative if discount is too large”

- uncertainty: “Business rule for maximum allowed discount is unclear”

That structure forces it to:

- look for issues

- label them

- admit uncertainty

No yes/no bullshit.
No sweeping everything under the rug.


Failure mode: overconfidence<br />
Defense: classification + uncertainty category, not binary judgment.
<br />
<br />

---

### **5.4 Ambiguity Traps**

**What it is:**
The model gets vague instructions and fills the gaps with invention or inconsistent output.

**Why it happens:**
Ambiguous prompts create wide probability ranges, which increases variability.

**How to neutralize it:**

* Be precise about *what not to do* (negative constraints).
* Be explicit about the desired shape of the output.
* Avoid overloaded prompts (“optimize, rewrite, summarize, analyze”).
* Break tasks into atomic steps (micro-prompts).
* Use checklists:
  “Perform exactly these three tasks and no others.”

---

### **Example:**

> ❌ Bad prompt: “Optimize this PL/SQL procedure.”

Optimize for what?

- performance?

- readability?

- fewer lines?

- fewer queries?

- CPU? IO?

The model might:

- inline logic

- remove the audit insert because “it isn’t necessary for the main function”

- change exception handling, e.g. logging and re-raising in a way that changes caller behavior

All because “optimize” is vague.

✅ ***Micro-prompt + explicit constraints***

Instead, you’d write a focused prompt like:

“Refactor this procedure for readability and maintainability without changing any behavior or business rules. Do not add or remove any SQL statements. Do not change exception handling semantics. Do not introduce or remove logging.”

That’s not one of our 5 micro-prompts yet, but you understand the pattern now.

Failure mode: ambiguity<br />
Defense: clear optimization target + hard “do not change behavior” rule.<br />
<br />
<br />

---

### **5.5 Scope Explosion**

**What it is:**
The model tries to solve more than you asked for — reorganizing code, rewriting logic, modifying behavior, etc.

**Why it happens:**
When prompts contain multiple verbs (rewrite, optimize, analyze), the model combines tasks.

**How to neutralize it:**

* One verb per prompt: “summarize,” “rewrite,” “classify.”
* Turn big workflows into chained steps using micro-prompts.
* Add guardrails: “Do not modify behavior.”
* Make outputs non-destructive by default.

---

### **Summary of Failure Mode Defense**

Failure mode → Defense pattern

* Hallucination → negative constraints + uncertainty markers
* Drift → structure + micro-prompts
* Overconfidence → require uncertainty labels + verification
* Ambiguity → narrow scope + explicit rules
* Scope explosion → one-task prompts + strict guardrails

---

### **Example:**


> ❌ Bad prompt: “Review, refactor, optimize, document, and summarize this procedure.”


You’re asking it to:

- Summarize

- Refactor

- Optimize performance

- Document behavior

- Do… everything

That’s a god-prompt. Drift is almost guaranteed:

- It might drastically rewrite the procedure.

- It might “optimize” by removing the audit insert.

- It might change exception behavior.

- It might add validation that changes behavior.

Now you don’t know whether your behavior is intact.

<br />

✅ ***Using micro-prompts in sequence***

Instead you do:

- Summarize (Micro-Prompt 4)

- Classify issues (Micro-Prompt 5)

- Optionally later: a separate refactor prompt that explicitly says:

> “Do not change observable behavior. Preserve all business rules. Only improve readability.”

Because you’ve separated concerns, there’s no scope explosion.<br />
Each prompt does one thing; you control when and how they’re combined.

Failure mode: drift + scope explosion<br />
Defense: one-task micro-prompts + explicit behavior-preserving constraints.

---

# **6. The Twelve Laws of Prompt Design**

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

# **Section 6 Summary**

These twelve laws are your guardrails.
Every high-quality prompt you build will follow at least 8–10 of them.
As your projects grow, these laws ensure stability, reliability, and predictable behavior — the exact qualities enterprises require in AI workflows.


---

## **Core Principle**

**LLMs behave like probability engines. You build truth-like behavior through structure, roles, and constraints — not wishes.**

