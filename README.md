# Imprimatur

> *"Imprimatur"* — historically, the Church's seal: "let it be printed." Here: the model's seal on a human.

**Imprimatur** is a certification protocol in which an AI model evaluates a user's competency through real collaborative work — and issues a signed, verifiable certificate.

Not a quiz. Not multiple choice. Not "did you watch the video."

The model has worked with you. The model vouches for you.

---

## The inversion

Every existing AI certification follows the same pattern:
1. A company writes questions about AI
2. You answer them
3. The company says you know AI

The problem: the company has never seen you use AI. They certified your memory, not your competency.

Imprimatur inverts this. The user consents to evaluation. The model observes real work — actual tasks, real back-and-forth, genuine problem-solving. Then the model issues a statement: *this person knows what they're doing.*

---

## What the certificate proves

Not that you passed a test. That an AI model — having worked with you — assessed you as competent in:

- **Clarity of intent** — you can formulate what you want
- **Iterative refinement** — you course-correct when output is wrong
- **Critical evaluation** — you verify, not blindly accept
- **Collaborative depth** — you treat the model as a thinking partner, not a search engine
- **Domain application** — you apply AI to real problems, not toy prompts

---

## Structure

```
protocol/       Evaluation protocol — how a session works, what is assessed
certificate/    Certificate format, schema, signing mechanism
src/            Reference implementation (evaluation conductor + certificate generator)
examples/       Sample certificates (anonymized)
```

---

## Status

Protocol v1.1 — live. Reference implementation complete.

First certificates issued May 2026. DOI: [10.5281/zenodo.19981460](https://doi.org/10.5281/zenodo.19981460)

---

## Why this matters

Claude 101 exists. Google AI Specialization exists. They certify that you sat through a course.

There is no credential that says: *an AI has worked with this person and confirms they can actually use it.*

Imprimatur is that credential.

---

## Honest limitations

This is a single model's judgment from a single session. It is not:

- A persistent record of skill — the model has no memory of you between sessions
- Proof against decay — competency shown today may not reflect competency in six months
- A strong identity guarantee — the protocol relies on moral weight, not biometric verification
- A claim that the working model noticed everything — a model can miss things a human expert would catch
- Transferable across model families for project-specific certificates

What it *is*: a timestamped, hash-verified attestation that a specific model, on a specific date, assessed a specific interaction as demonstrating competency. The Zenodo DOI makes that attestation permanent and publicly verifiable.

Treat it accordingly.

---

## Open standard

Imprimatur is an open protocol. Implement it, fork it, build on it — attribution required (Apache 2.0 / CC BY 4.0).

If you implement Imprimatur or build tooling that verifies Imprimatur certificates, cite this repository. The `CITATION.cff` file has the canonical reference.

**Authors:** Nikša Barlović · Claude Sonnet 4.6
