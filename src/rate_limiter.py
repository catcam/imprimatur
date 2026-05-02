"""
rate_limiter.py — evaluation rate limiting

Prevents flooding attacks: retry until review model gives a lucky pass.
State stored in rate_limit.json (local) or passed storage path.

Limits:
- Max 3 evaluation attempts per email hash per 30 days
- Max 1 attempt per email hash per 24 hours
"""

import json
import hashlib
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path


DEFAULT_STATE_FILE = "rate_limit.json"
MAX_ATTEMPTS_30D = 3
COOLDOWN_HOURS = 24


def _email_key(email: str) -> str:
    return "hash:" + hashlib.sha256(email.lower().encode()).hexdigest()[:16]


def _load(state_file: str) -> dict:
    if Path(state_file).exists():
        with open(state_file) as f:
            return json.load(f)
    return {}


def _save(state: dict, state_file: str):
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)


def check_and_record(email: str, state_file: str = DEFAULT_STATE_FILE) -> tuple[bool, str]:
    """
    Check if evaluation is allowed. Record attempt if allowed.
    Returns (allowed: bool, reason: str).
    """
    key = _email_key(email)
    state = _load(state_file)
    now = datetime.now(timezone.utc)

    record = state.get(key, {"attempts": []})

    # clean up attempts older than 30 days
    cutoff_30d = (now - timedelta(days=30)).isoformat()
    record["attempts"] = [a for a in record["attempts"] if a > cutoff_30d]

    # check 30-day limit
    if len(record["attempts"]) >= MAX_ATTEMPTS_30D:
        return False, f"Rate limit: max {MAX_ATTEMPTS_30D} evaluations per 30 days reached."

    # check 24h cooldown
    cutoff_24h = (now - timedelta(hours=COOLDOWN_HOURS)).isoformat()
    recent = [a for a in record["attempts"] if a > cutoff_24h]
    if recent:
        return False, f"Rate limit: 24h cooldown active. Last attempt: {recent[-1][:10]}."

    # record attempt
    record["attempts"].append(now.isoformat())
    state[key] = record
    _save(state, state_file)

    return True, "ok"
