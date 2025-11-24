# **9. LLM Debugging Guide**

*How to diagnose, isolate, and fix incorrect or unstable LLM behavior*

LLMs fail in **predictable** ways.
The key to mastery is treating LLM output like software output:
you debug the **prompt**, the **structure**, or the **constraints**, not the model.

This guide gives you a systematic process for diagnosing failures.

---

# **9.1 Step Zero — Identify the Failure Type**

LLM failures almost always fall into one of these categories:

1. **Hallucination** → invented objects, tables, logic
2. **Overreach** → rewriting or changing behavior
3. **Omission** → missing required output fields
4. **Drift** → wandering off-task
5. **Format Violation** → JSON invalid, prose added
6. **Ambiguity Interpretation** → AI picks the wrong meaning
7. **Overconfidence** → incorrect statements asserted as fact
8. **Under-Specification** → vague prompt = vague answer
9. **Context Loss** → model forgets constraints mid-output

Recognizing the failure type tells you which fix to apply.

---

# **9.2 Debugging Method #1 — Strip the Prompt to the Skeleton**

If the model behaves unpredictably, remove everything except:

* role
* task
* output shape

Example skeleton:

```
Act as a PL/SQL reviewer.
Identify issues in the code.
Return them in this JSON:
{ "issues": ["string"] }
```

If this works, the problem is in your **extra instructions**, not the model.

---

# **9.3 Debugging Method #2 — Add Negative Constraints**

If the model invents details:

Add explicit prohibitions:

* “Do NOT invent schema objects.”
* “Do NOT infer behavior not in the code.”
* “If uncertain, say ‘UNKNOWN.’”

Negative constraints reduce the model’s probability space — fewer hallucinations.

---

# **9.4 Debugging Method #3 — Lock Output Strictly**

If the model violates format or mixes prose with JSON:

Add these constraints:

* “Output **only** JSON.”
* “No explanations.”
* “No commentary.”
* “JSON must be syntactically valid.”

If needed, enforce a schema:

```
Your output must contain exactly these keys:
summary, risks, assumptions
```

This is the LLM equivalent of a type system.

---

# **9.5 Debugging Method #4 — Break Tasks Apart**

When a prompt tries to do too much, the model mixes tasks.

Fix:
Split one big prompt into multiple micro-prompts:

* summarize
* classify
* transform
* extract intent
* refactor
* document

Then chain them manually or via script.

This is the same as splitting a giant PL/SQL procedure into smaller ones.

---

# **9.6 Debugging Method #5 — Require Uncertainty**

If the model confidently bullshits:

Add:

* “If any claim is uncertain, say ‘UNCERTAIN’.”
* “Flag unclear logic explicitly.”
* “List assumptions you made.”

This forces self-auditing.

---

# **9.7 Debugging Method #6 — Supply More Context**

If the model is vague:

Add:

* schema
* business rules
* sample inputs/outputs
* constraints
* examples

LLMs don’t “know” your environment — you must feed it information explicitly.

---

# **9.8 Debugging Method #7 — Reduce Context**

If the model is acting *too* broadly:

Trim the input.

Give only:

* the procedure
* the block with issues
* the relevant portion

Large inputs increase hallucination and drift.

---

# **9.9 Debugging Method #8 — Reorder Instructions**

LLMs prioritize the **top** of a prompt.

If constraints are ignored, move them higher:

Bad order:

```
TASK
OUTPUT
CONSTRAINTS
```

Better:

```
ROLE
CONSTRAINTS
TASK
OUTPUT
```

Put “no hallucinations / no inventions / strict behavior-preservation” *early in the prompt*.

---

# **9.10 Debugging Method #9 — Force a Self-Check**

Tell the model to validate its own output:

```
Before returning output, verify:
- JSON is valid
- No invented objects
- Summary is grounded in provided code
```

This rarely fails and drastically improves reliability.

---

# **9.11 Debugging Method #10 — Temperature Control (for scripts)**

In API-based workflows:

* **low temperature (0.1–0.3)** → strict, deterministic
* **high temperature (0.7–1.0)** → creative, risky

For PL/SQL, APEX, DBA work:
**always use low temperature**.

---

# **9.12 Debugging Checklist**

When debugging, ask:

* What failure mode is this?
* Does the prompt violate “one task per prompt”?
* Is the output shape clearly defined?
* Are constraints clear and early?
* Are negative constraints included?
* Is uncertainty explicitly allowed?
* Does the prompt mix tasks?
* Is there too much or too little context?
* Are examples causing drift?
* Does this need chaining through micro-prompts?

This checklist solves ~90% of prompt bugs.

---

# **Section 9 Summary**

Debugging an LLM is about:

* controlling scope
* tightening constraints
* enforcing structure
* isolating tasks
* ensuring uncertainty
* validating output

This is engineering, not guesswork.
You now have a full debugging playbook that mirrors how senior engineers debug real systems.

---
