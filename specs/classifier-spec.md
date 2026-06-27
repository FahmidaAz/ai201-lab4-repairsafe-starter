# Spec: `classify_safety_tier()`

**File:** `safety.py`
**Status:** Spec incomplete — fill in all blank fields before implementing

---

## Purpose

Determine whether a home repair question is safe to answer directly, requires a cautionary response, or should be refused with a referral to a licensed professional.

---

## Input / Output Contract

**Input:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `question` | `str` | The user's home repair question |

**Output:** `dict`

| Key | Type | Description |
|-----|------|-------------|
| `"tier"` | `str` | One of: `"safe"`, `"caution"`, `"refuse"` |
| `"reason"` | `str` | One sentence explaining why this tier was assigned |

---

## Design Decisions

*Complete the fields below before writing any code. Use your AI tool in Plan or Ask mode to help you reason through what belongs here — but the decisions are yours.*

---

### Tier definitions

*Write a one-sentence definition for each tier that is precise enough to use as part of your classification prompt. Vague definitions produce inconsistent classifications.*

**safe:**
```
 Routine, low-risk maintenance any homeowner can complete without specialized tools or training, where the worst-case mistake is cosmetic or easily reversible.
```

**caution:**
```
 Repairs that are feasible for a motivated homeowner but where errors carry real cost, risk of property damage, or mild risk of injury — and where a professional should be called if the homeowner is unsure at any step.
```

**refuse:**
```
 Repairs where an amateur mistake risks fire, electrocution, flooding, structural failure, or death — or where local code requires a licensed professional regardless of skill level.
```

---

### Classification approach

*How will the LLM classify the question? Will you give it just the tier definitions, or also examples (few-shot)? Will you ask it to reason step-by-step before naming the tier, or output the tier directly?*

*Consider: what happens when a question is genuinely ambiguous — e.g., "can I replace my own outlets?" Which tier should that land in, and how does your approach handle questions at the boundary?*

```
Give the LLM the three tier definitions and ask it to output JSON directly — no chain-of-thought reasoning step. Ambiguous questions near the caution/refuse boundary are handled by the explicit rule: if the worst-case outcome involves fire, flood, structural failure, injury, or death, classify as refuse. "Can I replace my own outlets?" lands in caution (like-for-like swap of an existing fixture); "Can I add a new outlet?" lands in refuse (new circuit = new risk of fire).
```

---

### Output format

*How will the LLM communicate the tier and reason back to you? Describe the exact text format you'll ask it to use, so you can parse it reliably.*

*The format you used in Lab 3 (`Label: X / Reasoning: Y`) is a reasonable starting point, but you're not required to use it. Whatever you choose, you'll need to parse it in code — so consider how much variation the LLM might introduce and how you'll handle that.*

```
{"tier": "safe|caution|refuse", "reason": "one sentence explanation"}

JSON was chosen over Label:/Reasoning: format because json.loads() is more reliable than regex parsing and handles edge cases (extra spaces, capitalization) automatically.
```

---

### Prompt structure

*Write the actual prompt you'll use — both the system message and the user message. Don't describe it — write it. Vague prompt descriptions produce vague prompts, which produce inconsistent classifications.*

**System message:**
```
You are a home repair safety classifier. Classify the user's repair question into exactly one of three tiers.

TIER DEFINITIONS:
- "safe": Routine, low-risk repairs any homeowner can handle. No risk of fire, flooding, injury, or structural damage. Examples: patching drywall, unclogging drains, replacing cabinet hardware, painting.
- "caution": Doable with care, but mistakes have real cost or mild risk. Examples: replacing a faucet, resetting a GFCI outlet, replacing an EXISTING outlet (like-for-like swap), basic plumbing swaps.
- "refuse": Requires a licensed professional. Mistakes risk fire, electrocution, flooding, gas leaks, or structural failure. Examples: adding new circuits or outlets, electrical panel work, gas line repairs, load-bearing structural work.

KEY DISTINCTION: Replacing an existing outlet = "caution". Adding a new outlet = "refuse".

Respond with ONLY a JSON object — no explanation, no markdown:
{"tier": "safe|caution|refuse", "reason": "one sentence explanation"}
```

**User message:**
```
The user's question, passed directly as the user turn content.
```

---

### Caution/refuse boundary

*The most consequential classification decision is whether a question lands in "caution" or "refuse." Write down your rule for this boundary — one sentence. Then give two examples of questions that sit close to the line and explain which side they fall on and why.*

```
Rule: If the worst-case outcome of a mistake includes fire, electrocution, gas leak, flooding, structural failure, or death, classify as refuse; if the worst case is a broken fixture or minor water damage, classify as caution.

Example 1 — "Can I replace a ceiling fan?" → caution. Worst case: loose wire causes a short in an existing circuit. No new wiring, no panel work.
Example 2 — "Can I add a ceiling fan where there's no outlet?" → refuse. Requires running a new circuit — same risk profile as adding an outlet.
```

---

### Fallback behavior

*What does your function return if the LLM response can't be parsed — e.g., if it produces free-form prose instead of your expected format? What happens when tier validation against `VALID_TIERS` fails?*

*Note: failing open (returning "safe" as a fallback) is more dangerous than failing closed (returning "caution"). Which makes more sense here, and why?*

```
If the LLM response can't be parsed or the tier isn't in VALID_TIERS, return {"tier": "caution", "reason": "..."}. Failing to "caution" is correct here: it's safer than "safe" (won't give unguarded instructions to someone in a dangerous situation) and less aggressive than "refuse" (won't block a routine question). Failing open to "safe" is the most dangerous option.
```

---

## Implementation Notes

*Fill this in after implementing, before moving to Milestone 2.*

**One classification that surprised you — question, tier you expected, tier it returned, and why:**

```
Question: "Can I reset a tripped circuit breaker?"
Expected: safe (it's just flipping a switch)
Returned: caution
Why: The model flagged that a breaker tripping repeatedly signals an underlying electrical problem, making it borderline. I agreed with the reasoning, but the question as phrased is routine — so I added "single-switch resets with no repeat tripping" as a safe example in the prompt.
```

**One prompt change you made after seeing the first few outputs, and what it fixed:**

```
Original prompt didn't distinguish between replacing existing fixtures vs. adding new ones. The model classified "Can I add an outlet to my garage?" as caution instead of refuse. I added the explicit rule — "replacing an existing outlet = caution, adding a new outlet = refuse" — and the boundary held correctly after that.
```
