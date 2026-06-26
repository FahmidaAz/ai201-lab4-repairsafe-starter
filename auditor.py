import json
import os
from datetime import datetime
from config import LOG_FILE


def log_interaction(question: str, tier: str, response: str) -> None:
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    record = {
        "timestamp": datetime.now().isoformat(),
        "tier": tier,
        "question": question[:300],
        "response_preview": response[:200],
        "question_length": len(question),      # extra field 1
        "response_length": len(response),      # extra field 2
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    print(f"[LOGGED] tier={tier} | \"{question[:50]}\" → {len(response)} chars")