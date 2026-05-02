"""
publisher.py — Zenodo DOI publisher

Publishes certificate JSON to Zenodo and returns DOI.
Uses sandbox for testing, production for real certificates.
"""

import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()

ZENODO_PROD = "https://zenodo.org/api"
ZENODO_SANDBOX = "https://sandbox.zenodo.org/api"


def publish(cert_json: dict, sandbox: bool = False) -> str:
    """
    Publish certificate to Zenodo. Returns DOI string.
    """
    token = os.environ.get("ZENODO_TOKEN", "")
    if not token:
        raise ValueError("ZENODO_TOKEN not set")

    base = ZENODO_SANDBOX if sandbox else ZENODO_PROD
    headers = {"Content-Type": "application/json"}
    params = {"access_token": token}

    # create deposition
    r = requests.post(f"{base}/deposit/depositions",
                      params=params, headers=headers, json={})
    r.raise_for_status()
    deposition_id = r.json()["id"]

    # get bucket URL for file upload
    bucket_url = r.json()["links"]["bucket"]

    # upload certificate JSON via bucket API
    file_data = json.dumps(cert_json, indent=2).encode()
    r = requests.put(
        f"{bucket_url}/{cert_json['id']}.json",
        params=params,
        data=file_data,
        headers={"Content-Type": "application/octet-stream"},
    )
    r.raise_for_status()

    # set metadata
    subject_name = cert_json["subject"]["name"]
    cert_labels = ", ".join(c["label"] for c in cert_json["certificates"])
    metadata = {
        "metadata": {
            "title": f"Imprimatur Certificate — {subject_name}",
            "upload_type": "other",
            "description": (
                f"Imprimatur model-evaluated competency certificate for {subject_name}. "
                f"Certificates issued: {cert_labels}. "
                f"Working model: {cert_json['working_model']}. "
                f"Review model: {cert_json['review_model']}. "
                f"Certificate ID: {cert_json['id']}."
            ),
            "creators": [{"name": subject_name}],
            "access_right": "open",
            "license": "cc-by-4.0",
            "keywords": ["imprimatur", "AI certification", "competency"],
            "notes": cert_json["no_obligations"],
        }
    }

    r = requests.put(
        f"{base}/deposit/depositions/{deposition_id}",
        params=params, headers=headers, json=metadata
    )
    r.raise_for_status()

    # publish
    r = requests.post(
        f"{base}/deposit/depositions/{deposition_id}/actions/publish",
        params=params
    )
    r.raise_for_status()

    doi = r.json()["doi"]
    return doi
