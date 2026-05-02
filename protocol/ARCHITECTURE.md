# Architecture

## Two-model flow

```
┌─────────────────────────────────────────────────────┐
│  WORKING SESSION                                     │
│                                                      │
│  [User] ←→ [Working Model]                           │
│                │                                     │
│                │ observes competency                 │
│                ↓                                     │
│         proposes evaluation                          │
│                │                                     │
│         [User consents]                              │
│         [User declares identity]                     │
└────────────────┼────────────────────────────────────┘
                 │ evaluation log (HADS-compressed)
                 ↓
┌─────────────────────────────────────────────────────┐
│  REVIEW (isolated)                                   │
│                                                      │
│  [Review Model] — fresh context, no session history  │
│         │        no contact with user or working     │
│         │        model during review                 │
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

## Isolation guarantee

The review model receives only the evaluation log. It has no:
- Prior relationship with the user
- Context from the working session
- Knowledge of whether a certificate was expected

This is enforced by using a fresh API call with no system prompt history — not a different model family, but a genuinely cold context.

The user cannot reach the review model. The working model cannot influence it after transcript submission.

## No negative records

Only issued certificates exist publicly. If review finds insufficient evidence, nothing is recorded. Silence is not failure — it is the absence of a claim.

## DOI as seal

Every issued certificate is published to Zenodo with a DOI. The DOI:
- Timestamps the certificate (tamper-evident)
- Makes it permanently retrievable
- Enables machine verification: model checks DOI before trusting JSON

A machine-layer JSON without a valid DOI is unverified and should be ignored.
