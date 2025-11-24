# **10. Failure-Resistant Workflow Patterns**

*How to design AI pipelines that remain stable even when LLM output is imperfect*

AI workflows fail when prompts, context, or output handling allow ambiguity or drift.
Failure-resistant workflows are engineered like **fault-tolerant systems**: small components, strict contracts, validation gates, and fallback paths.

Below are the core patterns.

---

# **10.1 Pattern: Micro-Prompt Chaining (“Atomic Steps”)**

Instead of one giant prompt, break work into micro-steps:

1. summarize
2. classify
3. analyze (JSON)
4. optional: refactor
5. optional: test-outline

Each step validates the previous one before continuing.

**Benefits:**

* isolates risk
* prevents cross-contamination of tasks
* reduces hallucination
* easier to debug
* reproducible in automation

This is the exact workflow shape used in enterprise AI systems.

---

# **10.2 Pattern: Sandwich Structure (Constraints → Task → Structure)**

LLMs obey the beginning and end more than the middle.

Best pattern:

```
ROLE
CONSTRAINTS
TASK
OUTPUT SHAPE
```

Worst pattern:

```
TASK
EXPLANATION
ROLE
OUTPUT
CONSTRAINTS (ignored)
```

Forcing constraints *up front* reduces hallucination by >50%.

---

# **10.3 Pattern: Two-Stage Validation (Human or Script)**

Stage 1: LLM produces structured output
Stage 2: Script or human validates:

* JSON syntax
* no invented tables/columns
* required fields present
* values within allowed vocabulary
* no commentary

If the output fails, re-prompt with:

> “Correct the output to satisfy the schema without modifying content.”

This pattern guarantees **machine-safe** output.

---

# **10.4 Pattern: Uncertainty-First Reasoning**

Before doing anything else, force the model to identify unclear areas.

```
List anything that cannot be determined from the code.
```

Then feed that list back into the next prompt.

This pattern prevents false assumptions from polluting later steps.
It’s equivalent to validating preconditions before executing a function.

---

# **10.5 Pattern: Guardrail Sandwich (Two Layers of Constraint)**

Use constraints both:

1. **before the task**
2. **after the task** as a self-check

Example:

```
Before writing output:
- verify no invented objects
- verify all fields are filled
- verify only provided code is referenced
```

Self-checks force the model to reject its own hallucinations.

---

# **10.6 Pattern: Context Window Budgeting**

Never feed unnecessary code or metadata.

Feed only:

* one function/procedure
* or one package
* or one APEX component

Large contexts increase hallucination probability and make outputs less deterministic.

This is the AI equivalent of minimizing surface area in API design.

---

# **10.7 Pattern: Multi-Prompt Fallback (Fail-Safe Mode)**

If a complex prompt fails, fall back to a simpler one.

Example fallback chain:

1. full structured review → fails
2. issue extraction → works
3. classification → works
4. summary → always works

This pattern gives you graceful degradation instead of pipeline crash.

---

# **10.8 Pattern: Strict Output Contracts (Schema-Driven Design)**

Define schema first → then prompt around it.

Example:

```
{
  "summary": "string",
  "risks": ["string"],
  "assumptions": ["string"]
}
```

Advantages:

* stable automation
* easy validation
* zero ambiguity
* predictable token shape

This is the AI equivalent of designing a table schema before writing queries.

---

# **10.9 Pattern: No-Rewrite Layers (Encapsulation)**

In AI workflows touching PL/SQL or APEX:

* summary = NEVER rewrites
* classification = NEVER rewrites
* risk assessment = NEVER rewrites
* refactor = ONLY rewrite layer

You isolate the dangerous step into **one dedicated layer** so it cannot contaminate others.

This is the same concept as encapsulation in packages:
only one layer owns behavior mutation.

---

# **10.10 Pattern: Explicit Role Switching**

Different stages require different mental modes.

Example:

* Reviewer → strict, literal
* Classifier → analytical
* Refactorer → structural
* Test Designer → hypothetical

Changing the role between steps prevents cognitive bleed between reasoning styles.

---

# **10.11 Pattern: Controlled Amplification (Feedback Loop)**

Use this structure:

1. extract
2. classify
3. summarize
4. re-summarize the summary

This stabilizes meaning by compressing it twice — it forces the model into a corner where drift becomes unlikely.

It’s similar to normalizing database fields: eliminating redundancy and ambiguity.

---

# **10.12 Pattern: Immutable Inputs**

Once code is analyzed, **never let the LLM rewrite the input** unless explicitly asked.

Immutable input patterns prevent:

* “creative rewrites”
* unintended logic changes
* accidental SQL modification

This is crucial for database-centric codebases (PL/SQL especially).

---

# **Section 10 Summary**

Failure-resistant workflows depend on:

* atomic steps
* strict output schemas
* early constraints
* controlled role shifts
* multi-stage validation
* uncertainty-before-reasoning
* fallback paths
* immutable inputs

When these patterns are combined, you get enterprise-grade AI systems that behave consistently — not “chatbot unpredictably.”

This is the exact skillset organizations are missing right now.

---
