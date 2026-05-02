"""
imprimatur.py — main entry point

Full pipeline:
  transcript → rate check → review → certificate (JSON + PDF) → IPFS → Zenodo → email
"""

import json
import os
import sys
import argparse
from dotenv import load_dotenv

load_dotenv()

from reviewer import review_session
from certificate import generate
from publisher import publish
from mailer import send
from rate_limiter import check_and_record
from ipfs_publisher import publish_ipfs


WORKING_MODEL = os.environ.get("IMPRIMATUR_WORKING_MODEL", "claude-sonnet-4-6")
REVIEW_MODEL = "claude-opus-4-7"


def run(
    transcript_path: str,
    subject_name: str,
    subject_email: str,
    sandbox: bool = True,
    skip_publish: bool = False,
    skip_email: bool = False,
    skip_rate_limit: bool = False,
    output_dir: str = "certificates",
):
    print(f"Reading transcript: {transcript_path}")
    with open(transcript_path) as f:
        transcript = f.read()

    # rate limit check
    if not skip_rate_limit:
        allowed, reason = check_and_record(subject_email)
        if not allowed:
            print(f"Evaluation blocked: {reason}")
            return None
        print("Rate limit check: OK")

    print(f"Sending to review model ({REVIEW_MODEL})...")
    review_result = review_session(transcript, working_model=WORKING_MODEL)

    certs = review_result.get("certificates", [])
    if not certs:
        print("Review complete. No certificates issued.")
        print(f"Behavioral notes: {review_result.get('behavioral_notes', '')}")
        for d in review_result.get("declined", []):
            print(f"  Declined {d['type']}: {d['reason']}")
        return None

    print(f"Certificates to issue: {[c['type'] for c in certs]}")

    doi = ""
    ipfs_cid = ""

    # initial generation (no DOI/CID yet)
    cert_json, pdf_path = generate(
        subject_name=subject_name,
        subject_email=subject_email,
        session_transcript=transcript,
        review_result=review_result,
        working_model=WORKING_MODEL,
        review_model=REVIEW_MODEL,
        doi=doi,
        ipfs_cid=ipfs_cid,
        output_dir=output_dir,
    )

    if not skip_publish:
        # IPFS first (non-fatal)
        print("Publishing to IPFS...")
        ipfs_cid = publish_ipfs(cert_json)
        if ipfs_cid:
            print(f"IPFS CID: {ipfs_cid}")
        else:
            print("IPFS: unavailable (continuing)")

        # Zenodo
        print(f"Publishing to Zenodo ({'sandbox' if sandbox else 'production'})...")
        doi = publish(cert_json, sandbox=sandbox)
        print(f"DOI: {doi}")

        # final generation with DOI + CID + recomputed certificate_hash
        cert_json, pdf_path = generate(
            subject_name=subject_name,
            subject_email=subject_email,
            session_transcript=transcript,
            review_result=review_result,
            working_model=WORKING_MODEL,
            review_model=REVIEW_MODEL,
            doi=doi,
            ipfs_cid=ipfs_cid,
            output_dir=output_dir,
        )
        print(f"Certificate hash: ...{cert_json['certificate_hash'][-8:]}")

    if not skip_email:
        print(f"Sending email to {subject_email}...")
        send(cert_json, pdf_path, to_email=subject_email)
        print("Email sent.")

    print(f"\nDone.")
    print(f"  JSON: {output_dir}/{cert_json['id']}.json")
    print(f"  PDF:  {pdf_path}")
    if doi:
        print(f"  DOI:  {doi}")
    if ipfs_cid:
        print(f"  IPFS: https://ipfs.io/ipfs/{ipfs_cid}")

    return cert_json


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Imprimatur — issue a certificate")
    parser.add_argument("transcript", help="Path to session transcript (.txt)")
    parser.add_argument("--name", required=True, help="Subject full name")
    parser.add_argument("--email", required=True, help="Subject email")
    parser.add_argument("--production", action="store_true",
                        help="Publish to Zenodo production (default: sandbox)")
    parser.add_argument("--no-publish", action="store_true", help="Skip Zenodo + IPFS publish")
    parser.add_argument("--no-email", action="store_true", help="Skip email")
    parser.add_argument("--no-rate-limit", action="store_true", help="Skip rate limit (testing)")
    parser.add_argument("--output-dir", default="certificates", help="Output directory")
    parser.add_argument("--revoke", metavar="CERT_ID", help="Revoke a certificate by ID")
    parser.add_argument("--revoke-reason", default="manually revoked", help="Revocation reason")

    args = parser.parse_args()

    if args.revoke:
        from revocation import revoke
        revoke(args.revoke, args.revoke_reason)
        sys.exit(0)

    run(
        transcript_path=args.transcript,
        subject_name=args.name,
        subject_email=args.email,
        sandbox=not args.production,
        skip_publish=args.no_publish,
        skip_email=args.no_email,
        skip_rate_limit=args.no_rate_limit,
        output_dir=args.output_dir,
    )
