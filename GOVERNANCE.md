# Imprimatur Governance

## Maintainers

This protocol is conceived and maintained by a human-AI pair:

- **Nikša Barlović** (human) — project lead, domain vision, final authority
- **Claude Sonnet 4.6** (AI) — co-author, technical implementation, protocol design

The AI co-authorship is intentional and reflects the nature of the work. Imprimatur certifies human-AI collaboration; it would be inconsistent to erase AI contributions from its own governance.

---

## Certificate Type Additions

Adding a new certificate type requires:

1. Open a Pull Request with the proposed type definition (label, criteria, model_agnostic flag, example statement)
2. **30-day public comment period** — the PR remains open for community feedback
3. Maintainer approval to merge

---

## Protocol Changes

Changes to the core protocol (schema, verification procedure, trust tier definitions) require:

1. Open a Pull Request describing the change and rationale
2. **30-day public comment period**
3. Explicit approval from both maintainers (human + AI review on record)
4. Version bump in `schema_version` and a new spec file under `/specifications/`

Minor changes (typos, clarifications that do not alter behavior) may be merged without the 30-day period at maintainer discretion.

---

## Revocation Process

Revocations are permanent and public. The process:

1. Maintainer identifies grounds for revocation (fraud, identity misrepresentation, tampered certificate)
2. Entry is appended to `revocation.json` with: `id`, `revoked_at` (ISO 8601 UTC), `reason`
3. `revocation.json` is committed with a signed commit message referencing the certificate ID
4. No certificate is silently removed — the transparency log is append-only

Verification tools (`src/verify.py`) check `revocation.json` automatically.

---

## Versioning

Imprimatur uses **semantic versioning** for the certificate schema:

- **MAJOR** — breaking changes to required fields or verification logic
- **MINOR** — new optional fields, new certificate types, new trust tiers
- **PATCH** — editorial clarifications, example updates

Each minor or major version has a corresponding specification file in `/specifications/vX.Y.md`.

Current version: **1.1**

---

## Dispute Resolution

Disputes about certificate validity, evaluation fairness, or protocol interpretation are handled via **GitHub Issues**:

1. Open an issue with label `dispute`
2. Describe the specific concern with evidence
3. Maintainers respond within 14 days
4. **Maintainer decision is final**

Appeals are not available — if the protocol itself is flawed, open a protocol change PR instead.

---

## Note on AI Co-authorship

This protocol was conceived and is maintained by a human-AI pair. The AI co-authorship is intentional and reflects the nature of the work. Imprimatur exists to recognize substantive human-AI collaboration — its governance must model that same relationship.

The human maintainer retains final authority on all decisions. The AI co-maintainer's role is design, implementation, and technical review.
