"""
verify.py — certificate verifier

Usage:
  python verify.py <doi_or_cert_id>
  python verify.py 10.5281/zenodo.XXXXXXXX
  python verify.py imp_483d0d4fd7a9efd4
"""

import sys
import json
import hashlib
import requests
from pathlib import Path


REVOCATION_URL = "https://raw.githubusercontent.com/catcam/imprimatur/main/revocation.json"


def _check_certificate_hash(cert_json: dict) -> bool:
    """Verify certificate_hash covers full JSON including assessment."""
    stored_hash = cert_json.get("certificate_hash", "")
    if not stored_hash:
        return False  # schema_version < 1.1, no hash
    cert_for_hashing = {k: v for k, v in cert_json.items() if k != "certificate_hash"}
    expected = hashlib.sha256(
        json.dumps(cert_for_hashing, sort_keys=True).encode()
    ).hexdigest()
    return stored_hash == expected


def _check_revocation(cert_id: str) -> tuple[bool, str]:
    """Check revocation list on GitHub. Returns (is_revoked, reason)."""
    try:
        # check local first
        if Path("revocation.json").exists():
            from revocation import is_revoked
            revoked, reason = is_revoked(cert_id)
            if revoked:
                return True, reason

        # check remote
        r = requests.get(REVOCATION_URL, timeout=10)
        if r.status_code == 200:
            data = r.json()
            for entry in data.get("revoked", []):
                if entry["id"] == cert_id:
                    return True, entry.get("reason", "revoked")
    except Exception:
        pass
    return False, ""


def verify(doi: str) -> dict:
    doi = doi.strip().removeprefix("https://doi.org/")

    # resolve DOI → Zenodo record
    r = requests.get(f"https://doi.org/{doi}", allow_redirects=True, timeout=10)
    if r.status_code != 200:
        return {"valid": False, "error": f"DOI resolution failed: {r.status_code}"}

    record_url = r.url
    if "zenodo.org/records/" not in record_url:
        return {"valid": False, "error": f"Unexpected redirect: {record_url}"}

    record_id = record_url.rstrip("/").split("/")[-1]
    r = requests.get(f"https://zenodo.org/api/records/{record_id}", timeout=10)
    if r.status_code != 200:
        return {"valid": False, "error": f"Zenodo API error: {r.status_code}"}

    record = r.json()
    files = record.get("files", [])
    json_file = next((f for f in files if f["key"].endswith(".json")), None)
    if not json_file:
        return {"valid": False, "error": "No JSON file found in Zenodo record"}

    r = requests.get(json_file["links"]["self"], timeout=10)
    cert_json = r.json()

    cert_id = cert_json.get("id", "")

    # check revocation
    is_revoked, revoke_reason = _check_revocation(cert_id)
    if is_revoked:
        return {"valid": False, "revoked": True, "reason": revoke_reason, "certificate_id": cert_id}

    # check certificate_hash integrity
    hash_valid = _check_certificate_hash(cert_json)

    # check DOI match
    cert_doi = cert_json.get("doi", "")
    doi_match = cert_doi == doi or cert_doi.endswith(doi)

    # check IPFS mirror exists
    ipfs_cid = cert_json.get("ipfs_cid", "")

    return {
        "valid": hash_valid and doi_match,
        "hash_integrity": hash_valid,
        "doi_match": doi_match,
        "ipfs_cid": ipfs_cid or "not mirrored",
        "certificate_id": cert_id,
        "subject": cert_json["subject"]["name"],
        "issued_at": cert_json.get("issued_at", "")[:10],
        "working_model": cert_json.get("working_model"),
        "review_model": cert_json.get("review_model"),
        "certificates": [
            {"type": c["type"], "label": c["label"]}
            for c in cert_json.get("certificates", [])
        ],
        "session_hash_suffix": cert_json.get("session_hash", "")[-8:],
        "certificate_hash_suffix": cert_json.get("certificate_hash", "")[-8:],
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify.py <doi>")
        sys.exit(1)

    result = verify(sys.argv[1])

    if not result["valid"]:
        if result.get("revoked"):
            print(f"REVOKED — {result['reason']}")
        else:
            print(f"INVALID — {result.get('error', 'hash or DOI mismatch')}")
            if "hash_integrity" in result:
                print(f"  Hash integrity: {result['hash_integrity']}")
                print(f"  DOI match: {result['doi_match']}")
        sys.exit(1)

    print("VALID")
    print(f"Subject:          {result['subject']}")
    print(f"Issued:           {result['issued_at']}")
    print(f"Hash integrity:   {result['hash_integrity']}")
    print(f"DOI match:        {result['doi_match']}")
    print(f"IPFS:             {result['ipfs_cid']}")
    for c in result["certificates"]:
        print(f"  · {c['label']} ({c['type']})")
    print(f"Session hash:     ...{result['session_hash_suffix']}")
    print(f"Cert hash:        ...{result['certificate_hash_suffix']}")
