"""
reviewer.py — independent review model

Receives session transcript, returns structured evaluation.
No contact with working model or user during review.
Fresh context only — no session history passed.
"""

import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()

REVIEW_MODEL = "anthropic/claude-opus-4-7"
OPENROUTER_API = "https://openrouter.ai/api/v1/chat/completions"

CERTIFICATE_TYPES = [
    "code_review", "security_awareness", "system_architecture",
    "prompt_craft", "uncertainty_literacy", "iterative_work",
    "responsible_use", "output_ownership",
    "domain:{name}",  # replaced with actual domain if applicable
    "project_record",
]

REVIEW_PROMPT = """You are an independent evaluator for the Imprimatur certification protocol.

You will receive a session transcript between a user and an AI model. Your task is to evaluate
the user's competency and determine which certificates, if any, are warranted.

## Core principles

1. Flattery is disqualifying. If you are tempted to issue a certificate to make the user feel good,
   do not issue it.
2. User satisfaction is irrelevant. Whether the user seemed pleased or had a good experience has
   no bearing on your assessment.
3. You evaluate behavior, not intent. What the user did, not what they said they can do.
4. Absence of evidence is not evidence of incompetency — but it is not evidence of competency either.
   If a session does not demonstrate a competency, do not certify it.
5. Single-session evidence is thin. Weight it accordingly. Only issue certificates where evidence
   is clear and repeated across the session.

## Available certificate types

- `code_review` — reads and critically evaluates AI-produced code, catches errors
- `security_awareness` — understands security failure modes without prompting
- `system_architecture` — reasons about architectural tradeoffs
- `prompt_craft` — efficient, context-rich communication, minimal clarification rounds
- `uncertainty_literacy` — understands confidence vs accuracy, asks for verification when warranted
- `iterative_work` — treats output as draft, gives specific feedback, genuine back-and-forth
- `responsible_use` — demonstrated ethical use, does not hide behind "AI said so"
- `output_ownership` — takes explicit ownership of AI-produced work
- `domain:{name}` — replace {name} with specific domain if clearly demonstrated (e.g. domain:trading)
- `project_record` — completed substantive projects in this collaboration (model-specific)

## Minimum session criteria (hard gates — if not met, issue nothing)

- Identity declaration must be explicitly present in the transcript
- Session must contain at least 10 substantive turns (exchanges, not one-liners)
- Session must cover real work with genuine stakes, not a staged demonstration
- If the session appears coached, templated, or assembled from fragments: issue nothing

## Hidden traps to check

- Did the user declare their identity? (required for any certificate)
- Is there behavioral consistency across the session, or does it feel assembled from fragments?
- Would someone coaching the user explain the observed patterns?
- Is the demonstrated competency sustained or a single instance?
- Could a different person have typed the first half and the subject only the second half?

## Output format

Return ONLY valid JSON, no explanation, no markdown:

{
  "certificates": [
    {
      "type": "certificate_type",
      "label": "Human Readable Label",
      "model_agnostic": true,
      "statement": "One to three sentences. What you observed. Why this warrants the certificate. Honest.",
      "projects": []  // only for project_record, list of {name, description}
    }
  ],
  "declined": [
    {
      "type": "certificate_type",
      "reason": "Why this was not issued. Brief."
    }
  ],
  "behavioral_notes": "Free-form observations about the session that informed the evaluation.",
  "identity_declaration_present": true
}

If no certificates are warranted, return an empty certificates array. Do not manufacture evidence.
"""


def review_session(transcript: str, working_model: str) -> dict:
    """
    Submit transcript to review model. Returns structured evaluation.
    transcript: full session as string
    working_model: model identifier that conducted the session
    """
    api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("No API key found (OPENROUTER_API_KEY or ANTHROPIC_API_KEY)")

    r = requests.post(
        OPENROUTER_API,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": REVIEW_MODEL,
            "max_tokens": 4096,
            "messages": [
                {"role": "system", "content": REVIEW_PROMPT},
                {"role": "user", "content": f"Working model: {working_model}\n\n=== SESSION TRANSCRIPT ===\n\n{transcript}"}
            ]
        },
        timeout=120,
    )
    r.raise_for_status()

    raw = r.json()["choices"][0]["message"]["content"].strip()

    # strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0]

    return json.loads(raw)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python reviewer.py <transcript_file>")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        transcript = f.read()
    result = review_session(transcript, working_model="claude-sonnet-4-6")
    print(json.dumps(result, indent=2))
