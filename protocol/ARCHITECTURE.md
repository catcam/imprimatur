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
                 │ transcript only
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

## Isolation guarantee

The review model receives only the session transcript. It has no:
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
