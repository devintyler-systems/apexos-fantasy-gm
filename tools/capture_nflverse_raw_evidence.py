"""JSON-only CLI for one explicit nflverse raw-evidence asset capture."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from engine.ingestion.nflverse_raw_evidence import (
    HttpxHttpTransport,
    NflverseAssetRequest,
    RawEvidenceCaptureResult,
    capture_nflverse_raw_evidence,
    result_to_dict,
)


class _JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        result = RawEvidenceCaptureResult(
            status="failed",
            reason_codes=("INVALID_ASSET_IDENTITY",),
            snapshot_id=None,
            raw_asset_path=None,
            manifest_path=None,
            lineage=None,
            parsed_row_count=None,
            quarantined_identity_count=0,
            quarantine_path=None,
            known_limitations=("Invalid CLI invocation: " + " ".join(message.split()),),
            degraded_mode=True,
        )
        print(json.dumps(result_to_dict(result), sort_keys=True))
        raise SystemExit(2)


def _parser() -> argparse.ArgumentParser:
    parser = _JsonArgumentParser(description=__doc__)
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--asset-url", required=True)
    parser.add_argument("--as-of-timestamp", required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--expected-byte-count", type=int)
    parser.add_argument("--fixture-mode", action="store_true")
    parser.add_argument("--allow-unsigned-for-local-fixture", action="store_true")
    parser.add_argument(
        "--source-contract-version",
        default="nflverse-play-by-play-ingestion-contract-v0.2",
    )
    parser.add_argument("--parser-version", default="nflverse-raw-evidence-v0.1")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    if args.allow_unsigned_for_local_fixture and not args.fixture_mode:
        parser.error(
            "--allow-unsigned-for-local-fixture requires --fixture-mode"
        )
    if args.expected_sha256 is None and not (
        args.fixture_mode and args.allow_unsigned_for_local_fixture
    ):
        parser.error(
            "--expected-sha256 is required unless explicit local fixture mode is enabled"
        )

    request = NflverseAssetRequest(
        season=args.season,
        release_tag="pbp",
        asset_name=f"play_by_play_{args.season}.parquet",
        asset_url=args.asset_url,
        expected_sha256=args.expected_sha256,
        expected_byte_count=args.expected_byte_count,
        as_of_timestamp=args.as_of_timestamp,
        source_contract_version=args.source_contract_version,
        parser_version=args.parser_version,
    )
    result = capture_nflverse_raw_evidence(
        request,
        args.output_root,
        HttpxHttpTransport(),
        fixture_mode=args.fixture_mode,
    )
    print(json.dumps(result_to_dict(result), sort_keys=True))
    return 0 if result.status.startswith("success") else 1


if __name__ == "__main__":
    sys.exit(main())
