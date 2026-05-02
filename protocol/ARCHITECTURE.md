# Architecture

## Three-model flow

Imprimatur uses three distinct model roles — not two. The working model and the judge
are never the same instance, even if they run on the same model family.

```
┌─────────────────────────────────────────────────────┐
│  MODEL 1: WORKING MODEL                              │
│                                                      │
│  [User] ←→ [Working Model]                           │
│                │                                     │
│                │ builds evaluation log in background │
│                │ (user does not see this)            │
│                ↓                                     │
│         context monitor watches fill %               │
│         triggers evaluation at ~80% OR session end  │
│                │                                     │
│         [User consents]                              │
│         [User declares identity]                     │
└────────────────┼────────────────────────────────────┘
                 │ evaluation log (HADS-compressed)
                 │ NO raw transcript, NO model outputs
                 ↓
┌─────────────────────────────────────────────────────┐
│  MODEL 2: THE JUDGE (isolated third party)           │
│                                                      │
│  Completely separate API call. Cold context.         │
│  Has never seen this user. Has no memory of          │
│  the working session. Cannot be reached by           │
│  the user or the working model.                      │
│                                                      │
│  Receives only: evaluation log + evaluation rubric   │
│         ↓                                            │
│  structured assessment + free-form statement         │
└────────────────┼────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────────┐
│  CERTIFICATE                                         │
│                                                      │
│  JSON (machine layer) — for model context            │
│  PDF  (human layer)   — for CV, LinkedIn             │
│  DOI  (permanent record) — tamper evidence           │
│                                                      │
│  → email to subject                                  │
└─────────────────────────────────────────────────────┘
```

## Evaluation Log (HADS-Imprimatur Format)

The working model does not send the raw transcript to the judge — it sends a compressed
evaluation log built from four HADS-compatible tags:

- **[IMP-REQ]** — user's raw request (verbatim)
- **[IMP-META]** — compressed summary of model output (replaces full code/text)
- **[IMP-FAIL]** — exact failure mode that triggered course-correction
- **[IMP-ITER]** — user's specific correction instruction

This reduces judge token cost by ~85-90% vs. raw transcript while preserving
the context needed to evaluate iterative refinement and critical evaluation.

The log is built incrementally during the session. The user never sees it being
constructed — they interact normally. The tagging moment is not disclosed.

See `protocol/EVALUATION_LOG.md` for full tag specifications and examples.

## The Judge

The judge is not the working model in a fresh context. It is a separate, isolated API call
with no shared state. It receives only:

- The HADS-compressed evaluation log
- The evaluation rubric (fixed, not influenced by the session)

It does not know:
- Whether a certificate was expected
- What the working model thought of the user
- Whether this is the user's first or tenth evaluation attempt

This isolation is what removes pressure from both models. The working model cannot
flatter the user into a certificate. The user cannot flatter the working model into
recommending one.

## Context Monitor and Evaluation Trigger

The working model monitors context fill throughout the session. Evaluation is triggered
automatically when either:

- Context reaches ~80% capacity (before quality degradation begins)
- The session ends normally

This has a secondary effect: the user cannot predict when evaluation occurs. They must
maintain consistent quality throughout — they cannot perform only when they think
they are being watched.

This is the panopticon property of the protocol: the evaluation window is always open,
so the user must always be working at their actual level.

## Isolation guarantee

The judge receives only the evaluation log. It has no:
- Prior relationship with the user
- Context from the working session
- Knowledge of whether a certificate was expected

This is enforced by a fresh API call with no system prompt history.

The user cannot reach the judge. The working model cannot influence it after log submission.

## No negative records

Only issued certificates exist publicly. If review finds insufficient evidence, nothing is recorded. Silence is not failure — it is the absence of a claim.

## DOI as seal

Every issued certificate is published to Zenodo with a DOI. The DOI:
- Timestamps the certificate (tamper-evident)
- Makes it permanently retrievable
- Enables machine verification: model checks DOI before trusting JSON

A machine-layer JSON without a valid DOI is unverified and should be ignored.

---

## Acknowledgements

Several architectural decisions in this document emerged from an adversarial review
session conducted with Gemini (Google DeepMind), May 2026.

Gemini identified the "one-sided conversation" paradox — the judge cannot evaluate
course-correction quality without seeing what the user was correcting. This led to
the HADS-Imprimatur evaluation log format ([IMP-REQ], [IMP-META], [IMP-FAIL], [IMP-ITER]).

Gemini also formalized the panopticon property and the context monitor trigger mechanism.

The three-model framing (working model / judge / certificate) was sharpened through
that exchange. The protocol is better for it.

Hvala vam.
