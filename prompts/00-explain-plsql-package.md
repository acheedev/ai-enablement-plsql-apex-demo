# Micro-Prompt 1: “Explain With Constraints”

## Goal

Ask the model to explain something, without guessing or inventing.

Write a prompt that explains:
- what a PL/SQL package spec does
- in under 5 sentences
- without illusions of functionality not present in the code
- and requiring the model to explicitly flag uncertainty

---
### Prompt:

```ini
[ROLE]
Act as a senior PL/SQL code reviewer.

[CONTEXT]
You are reviewing a PL/SQL package specification provided by the user.

[TASK]
Explain what the package specification defines and what its public interface suggests about its purpose.
Flag any areas where the intent is unclear or cannot be determined from the spec alone.

[CONSTRAINTS]
- Keep the explanation under 5 sentences.
- Do not infer or assume functionality that is not explicitly present.
- If something is uncertain or under-specified, state that uncertainty directly.
- Be precise, literal, and avoid embellishment.

[OUTPUT]
Provide a short explanatory paragraph only. No code, no examples, no additional commentary.

```

