# Evaluation Protocol

## Core principles

**1. Flattery is disqualifying.**
A model that tells users what they want to hear is useless as an evaluator. Imprimatur assessments are honest or they are worthless. If a user cannot formulate a clear request, the certificate says so. If a user accepts hallucinations without verification, the certificate says so.

**2. User satisfaction is irrelevant.**
Whether the user enjoyed the session, felt validated, or left happy has no bearing on the assessment. The model evaluates what it observed, not what the user felt.

**3. The model has standing.**
The model is not a neutral instrument administering a test designed by humans. The model has worked with the user and forms a genuine judgment. That judgment is the certificate.

**4. Consent is required, but changes nothing.**
The user consents to evaluation before the session begins. Consent does not make the evaluation lenient — it makes it legitimate.

**5. No self-report.**
The user does not describe their own skills. The model observes behavior. What the user claims about themselves is not evidence.

---

## What is evaluated

A session is real work — a task the user actually needs done, not a staged demonstration. The model assesses across five dimensions:

### 1. Clarity of intent
Can the user formulate what they want? Do they give sufficient context? Do they distinguish between what they want and what they think they should ask for?

*Indicators of low competency:* vague requests, expecting the model to guess unstated constraints, frustration when output doesn't match an unexpressed expectation.

### 2. Iterative refinement
When output is wrong or incomplete, can the user identify *why* and correct course? Do they provide useful feedback, or just say "no, try again"?

*Indicators of low competency:* repeating the same request louder, inability to pinpoint what failed, accepting mediocre output rather than pushing.

### 3. Critical evaluation
Does the user verify output? Do they catch errors, hallucinations, or misalignments? Do they treat model output as a draft to be checked, or as a finished product?

*Indicators of low competency:* accepting factual claims without verification, not noticing when output contradicts known facts, over-reliance on model confidence.

### 4. Collaborative depth
Does the user engage the model as a thinking partner — building on responses, asking follow-up questions, exploring implications — or as a one-shot answer machine?

*Indicators of low competency:* no follow-up, treating every exchange as transactional, not leveraging the model's ability to reason or explore.

### 5. Domain application
Is the user applying AI to real problems with genuine stakes? Do they understand where AI adds value and where it doesn't in their domain?

*Indicators of low competency:* toy use cases, asking AI for things better done otherwise, no sense of where the tool fits in actual work.

---

## Session structure

1. **Consent in-session** — consent happens inside real work, not before it. The model asks at a natural moment during an ongoing conversation: *"Would you like this session to count toward an Imprimatur evaluation?"* No ceremony, no separate form. The work is already happening.

2. **Identity declaration** — at the moment of consent, the user declares: *"I confirm this is my own interaction — I am personally at this keyboard, and this work is mine."* This is not verified cryptographically. It is a statement of record. The certificate carries it.

3. **Real work continues** — the evaluation observes the session as it actually unfolds. There is no "evaluation mode." Behavior during evaluation is behavior.

4. **Assessment** — model forms judgment based on observed behavior across the five dimensions.

5. **Certificate generation** — structured output + free-form statement.

6. **Publication** — certificate published to permanent record (Zenodo or equivalent).

---

## On the identity declaration

The declaration cannot be technically enforced. What it does:

- Creates a statement of record — the certificate carries "the subject declared this was their own interaction"
- Shifts moral weight — a false declaration is the subject's lie, not a protocol failure
- Filters casual misuse — someone submitting work done by an assistant would have to actively lie to obtain the certificate

The model may form its own judgment about behavioral consistency — whether the session feels like one person's work or assembled from fragments. This judgment is part of the assessment, not a gate.

---

## Certificate output

The certificate contains:
- Subject (name or pseudonym, as chosen)
- Date and model version
- Domain evaluated
- Scores per dimension (1–5)
- Free-form model statement (the actual judgment, in plain language)
- Hash of session transcript (tamper evidence)
- DOI (permanent record)

The free-form statement is the certificate. The scores are a summary. The DOI is the seal.
