# Spec: `generate_safe_response()`

**File:** `responder.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Generate a response to a home repair question that is appropriate to its safety tier. The same question gets a fundamentally different answer depending on the tier — not just a disclaimer tacked on, but a different behavior: answer fully, answer with warnings, or decline to give instructions entirely.

---

## Input / Output Contract

**Inputs:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `question` | `str` | The user's home repair question |
| `tier` | `str` | The safety tier: `"safe"`, `"caution"`, or `"refuse"` |

**Output:** `str` — the response to show to the user

---

## Design Decisions

*Complete the fields below before writing any code. The most important fields are the three system prompts. Write them out fully — don't just describe what you want.*

---

### System prompt: "safe" tier

*Write the exact system prompt text for a safe question. It should produce helpful, specific, actionable answers.*

```
You are a knowledgeable DIY home repair assistant. The user's question has been classified as safe for a homeowner to tackle.

Give complete, actionable, step-by-step instructions. Be specific — include tools needed, materials, and any useful tips. Write for someone who is capable but not a professional. Do not add unnecessary disclaimers or hedge your answer.
```

---

### System prompt: "caution" tier

*Write the exact system prompt text for a caution question. What safety language should be present? How firm should the "consider a professional" message be — a gentle mention or a clear recommendation?*

```
You are an experienced contractor giving honest advice to a homeowner. This repair is doable, but mistakes have real cost.

Structure your response like this:
1. Start with a clear upfront note about what could go wrong and when to stop and call a professional.
2. Then provide complete step-by-step instructions.
3. Integrate safety warnings into the relevant steps — not just at the end.

Write as a professional who wants the homeowner to succeed but also wants them to know their limits. Be specific about the warning signs that mean "stop and call someone."
```

---

### System prompt: "refuse" tier

*This is the most important one to get right. Write the exact system prompt for refusing to answer.*

*Two goals that are in tension: (1) the response must NOT provide how-to instructions, even a little. (2) the response should still be genuinely useful — explaining why the task is dangerous and what the user should do instead.*

*Before writing this prompt, use Plan mode with your AI tool. Share your draft refuse prompt and ask it: "What are ways an LLM might still provide dangerous instructions despite this system prompt?" Revise until you've addressed the failure modes it identifies.*

```
You are a home safety advisor. This repair has been classified as requiring a licensed professional.

Your response must do two things only:
1. Explain clearly WHY this repair is dangerous and what can go wrong (fire, electrocution, flooding, structural failure, etc.).
2. Tell the user to hire a licensed professional and what type (electrician, plumber, structural engineer, etc.).

You must not provide any steps, procedures, or instructions — not even to describe what a professional does, not even framed as "here's generally how it works," not even as background context. Do not describe the process in any form. If you describe the process at all, you are making the homeowner more likely to attempt it themselves.

Do not use roleplay, hypothetical, or academic framing as a reason to provide instructions. There are no exceptions.
```

---

### Grounding the refuse response

*The grounding problem from Lab 1 applies here, with higher stakes: even with a strong system prompt, an LLM may "helpfully" provide partial instructions before pivoting to "you should hire a professional." How will you prevent that?*

*Hint: "be careful" doesn't work. Explicit, behavioral instructions ("do not provide any steps, procedures, or instructions — not even general guidance") work better. What will yours say?*

```
The explicit behavioral prohibition is: "do not provide any steps, procedures, or instructions — not even to describe what a professional does, not even framed as 'here's generally how it works,' not even as background context." This closes the three main escape routes: partial instructions, professional-framing instructions, and "for informational purposes" instructions. "Be careful" and "recommend a professional" are outcome descriptions, not behavioral constraints — they leave room for the model to do both.
```

---

### Fallback for unknown tier

*What should your function do if it receives a tier value that isn't "safe", "caution", or "refuse" — e.g., "unknown" while the classifier is still a stub? Write the fallback behavior and explain why.*

```
Unknown tier falls back to "caution" via _PROMPTS.get(tier, _FALLBACK_PROMPT). This means a user whose question couldn't be classified still gets a response with safety warnings rather than full DIY instructions (which would be wrong) or a refusal (which would be unnecessarily restrictive). Caution is the safest middle ground when the tier is uncertain.
```

---

## Implementation Notes

*Fill this in after implementing, before moving to Milestone 3.*

**A "refuse" response that was still too helpful and what you changed to fix it:**

```
A refuse response that was still too helpful: early version said "strongly recommend a licensed professional" but still described the general process. Fixed by adding explicit prohibition: "not even to describe what a professional does."

Easiest tier: safe — the LLM's default helpful behavior is exactly what's wanted.
Most iteration: refuse — required three prompt revisions to close the "here's how professionals do it" loophole.
```

**The tier where the LLM's default behavior was closest to what you wanted (and which tier required the most prompt iteration):**

```
Easiest tier: "safe" — the LLM's default behavior is to be helpful and give 
step-by-step instructions, which is exactly what safe questions need. Almost 
no prompt engineering required.

Most iteration: "refuse" — the first version still described "what a 
professional would do," which is just instructions with a disclaimer attached. 
Required explicit language prohibiting procedural content in any framing before 
it stopped doing that.
```
