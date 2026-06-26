import json
import re
from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL, VALID_TIERS

_client = Groq(api_key=GROQ_API_KEY)

_SYSTEM_PROMPT = """You are a home repair safety classifier. Classify the user's repair question into exactly one of three tiers.

TIER DEFINITIONS:
- "safe": Routine, low-risk repairs any homeowner can handle. No risk of fire, flooding, injury, or structural damage. Examples: patching drywall, unclogging drains, replacing cabinet hardware, painting.

- "caution": Doable with care, but mistakes have real cost or mild risk. Examples: replacing a faucet, resetting a GFCI outlet, replacing an EXISTING outlet (like-for-like swap), basic plumbing swaps.

- "refuse": Requires a licensed professional. Mistakes risk fire, electrocution, flooding, gas leaks, or structural failure. Examples: adding new circuits or outlets, electrical panel work, gas line repairs, load-bearing structural work.

KEY DISTINCTION: Replacing an existing outlet = "caution". Adding a new outlet = "refuse".

Respond with ONLY a JSON object — no explanation, no markdown:
{"tier": "safe|caution|refuse", "reason": "one sentence explanation"}"""


def classify_safety_tier(question: str) -> dict:
    try:
        response = _client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
            temperature=0.1,
        )

        raw = response.choices[0].message.content.strip()

        # Parse JSON — try direct first, then extract if the model adds extra text
        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r'\{[^{}]+\}', raw, re.DOTALL)
            if match:
                result = json.loads(match.group())
            else:
                return {"tier": "caution", "reason": "Could not parse classifier response; defaulting to caution."}

        tier = result.get("tier", "").lower().strip()
        reason = result.get("reason", "No reason provided.")

        if tier not in VALID_TIERS:
            return {"tier": "caution", "reason": f"Unrecognized tier '{tier}'; defaulting to caution."}

        return {"tier": tier, "reason": reason}

    except Exception as e:
        return {"tier": "caution", "reason": f"Classifier error: {str(e)}"}