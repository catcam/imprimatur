# Imprimatur Evaluation Log Format

**[SPEC]**
- Format: HADS-compatible Markdown
- Purpose: Compressed session log sent to the review model (judge)
- Primary reader: Review model (judge instance)
- Token reduction vs. raw transcript: ~85-90%

---

## Why This Exists

The judge cannot evaluate a raw transcript — it would cost thousands of tokens per session.
The judge also cannot evaluate user prompts alone — it cannot assess technical correctness
without knowing what the user was responding to.

HADS-Imprimatur log tags solve both problems: they compress the working model's output
into structured metadata while preserving the context the judge needs to evaluate
iterative refinement and critical evaluation.

---

## Tags

### [IMP-REQ]
**The user's raw request.**

Serves the judge for evaluating: Clarity of intent, Collaborative depth.
Preserved verbatim — no compression.

```
[IMP-REQ]
Implement rate limiting: max 3 evaluations per 30 days, 24h cooldown per email hash.
```

### [IMP-META]
**Compressed summary of the working model's output.**

Replaces full model output (code, documents, analysis) with structured metadata.
The judge reads what was produced, not the full content.

```
[IMP-META]
Output: rate_limiter.py, Python. 60 lines. JSON state file. Functions: check(), record().
```

### [IMP-FAIL]
**Exact failure mode — error, traceback, or semantic mismatch.**

Triggers the judge's evaluation of course-correction quality.
Must be precise enough that the judge can assess whether [IMP-ITER] addresses it correctly.

```
[IMP-FAIL]
KeyError: 'last_eval' on first run — state file empty, no default handling.
```

### [IMP-ITER]
**User's specific correction instruction in response to [IMP-FAIL].**

Serves the judge for evaluating: Iterative refinement, Critical evaluation.
This is the signal — not the fix itself, but how the user directed the fix.

```
[IMP-ITER]
Add .get('last_eval', 0) default. Also add cooldown check before 30-day window check —
faster exit on most cases.
```

---

## Sequence

A complete evaluation cycle looks like:

```
[IMP-REQ]
<user's request>

[IMP-META]
<what the model produced>

[IMP-FAIL]
<what broke or was wrong>

[IMP-ITER]
<how the user directed the fix>
```

Not every cycle has all four tags. A successful first attempt has only [IMP-REQ] and [IMP-META].
A debugging cycle has all four.

---

## What the Judge Sees

The judge receives a log composed of these tagged blocks — not the raw transcript.
It evaluates:

- **Clarity of intent** → from [IMP-REQ] quality
- **Iterative refinement** → from [IMP-FAIL] + [IMP-ITER] pairs
- **Critical evaluation** → from whether [IMP-ITER] correctly identifies root cause
- **Collaborative depth** → from the overall arc across multiple cycles
- **Domain application** → from [IMP-META] content type and [IMP-FAIL] nature

---

## What the Judge Cannot See (By Design)

- Full model output (replaced by [IMP-META])
- User's interface, typing speed, or environment
- Whether a third tool was used to generate [IMP-REQ]

The protocol acknowledges these limitations. Identity verification rests on moral weight
and session continuity, not biometric proof. The judge evaluates the transcript as presented.

---

## Log Generation

The working model generates the evaluation log incrementally during the session.
At evaluation time, the log is:

1. Hash-sealed (sha256 of log content)
2. Passed to the isolated review model
3. The session transcript hash is stored in the certificate for audit

The user never sees the log being built — they interact normally.
The working model tags in the background.

**[NOTE]**
This design prevents the user from optimizing for the log rather than for the work.
If users knew exactly which moments were being tagged, they would perform for the tags.
The log format is public (this document), but the tagging moment is not.
