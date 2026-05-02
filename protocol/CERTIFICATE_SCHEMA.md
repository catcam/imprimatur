# Certificate Schema

## JSON (machine layer)

```json
{
  "schema_version": "1.0",
  "id": "imp_<sha256[:16]>",
  "subject": {
    "name": "Full Name",
    "email": "hash:<sha256 of email>",
    "declaration": "I confirm this is my own interaction — I am personally at this keyboard, and this work is mine."
  },
  "issued_at": "2026-05-02T14:32:00Z",
  "working_model": "claude-sonnet-4-6",
  "review_model": "claude-opus-4-7",
  "certificates": [
    {
      "type": "prompt_craft",
      "label": "Prompt Craft",
      "model_agnostic": true,
      "statement": "Free-form statement from review model.",
      "issued_at": "2026-05-02T14:32:00Z"
    },
    {
      "type": "project_record",
      "label": "Project Record",
      "model_agnostic": false,
      "issuing_model": "claude-sonnet-4-6",
      "projects": [
        {
          "name": "Project Name",
          "description": "One-sentence description."
        }
      ],
      "statement": "Free-form statement from review model.",
      "issued_at": "2026-05-02T14:32:00Z"
    }
  ],
  "session_hash": "sha256:<hash of full session transcript>",
  "doi": "10.5281/zenodo.XXXXXXXX",
  "no_obligations": "This certificate reflects the independent judgment of an AI model. It carries no obligations, warranties, or representations by any company or organization. The issuing model attests only to what it observed."
}
```

## PDF (human layer)

The PDF is generated from the JSON. It contains:
- Subject name
- Certificate types issued (human-readable labels)
- Per-certificate statement from review model
- Issue date and model versions
- DOI (as QR code + text)
- No-obligations notice
- Session hash (last 8 chars visible, full hash in metadata)

The PDF is sealed by embedding the full JSON in PDF metadata.
Verification: `imprimatur verify <doi>` fetches Zenodo record and checks hash.

## Verification

```bash
imprimatur verify 10.5281/zenodo.XXXXXXXX
# → fetches Zenodo record
# → extracts embedded JSON
# → checks session_hash integrity
# → prints: VALID / INVALID + certificate summary
```

A model receiving a machine-layer JSON must verify the DOI before treating
the certificate as authoritative. Unverified JSON is ignored.
