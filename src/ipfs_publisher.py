"""
ipfs_publisher.py — IPFS mirror via w3s.link (web3.storage compatible)

Free, no API key needed for small uploads via public gateway.
Fallback: pin via nftstorage.link if primary fails.
Returns CID string or empty string on failure (non-fatal).
"""

import json
import requests


def publish_ipfs(cert_json: dict) -> str:
    """Pin certificate JSON to IPFS. Returns CID or '' on failure."""
    data = json.dumps(cert_json, indent=2).encode()

    # Try w3s.link public upload endpoint
    try:
        r = requests.post(
            "https://api.web3.storage/upload",
            headers={"Content-Type": "application/json"},
            data=data,
            timeout=30,
        )
        if r.status_code == 200:
            return r.json().get("cid", "")
    except Exception:
        pass

    # Fallback: nft.storage public endpoint
    try:
        r = requests.post(
            "https://api.nft.storage/upload",
            headers={"Content-Type": "application/json"},
            data=data,
            timeout=30,
        )
        if r.status_code == 200:
            return r.json().get("value", {}).get("cid", "")
    except Exception:
        pass

    return ""
