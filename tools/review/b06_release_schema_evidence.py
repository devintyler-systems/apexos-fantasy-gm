#!/usr/bin/env python3
"""Review-only Parquet schema evidence utility for the proposed B-06 v0.3 contract.

This utility is intentionally outside the ``engine`` package and is not
production ingestion code.  It reads either a caller-supplied local Parquet
file or a review asset URL, emits a metadata-only schema transcript, and never
persists downloaded source bytes.  It does not validate rows, promote data, or
create any B-06 artifact.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import sys
import urllib.request
from pathlib import Path

try:
    import pyarrow
    import pyarrow.parquet as pq
except ImportError as error:  # pragma: no cover - environment diagnostic
    raise SystemExit(
        "pyarrow is required for this review-only utility; no dependency was installed. "
        f"Import error: {error}"
    ) from error


REQUIRED_COLUMNS = (
    "season",
    "season_type",
    "game_id",
    "yardline_100",
    "touchdown",
    "rush_attempt",
    "pass_attempt",
)
ALLOWED_EVIDENCE_ROOT = Path("docs/evidence").resolve()


def sha256_stream(stream: io.BufferedIOBase) -> str:
    """Return the SHA-256 for a seekable binary stream without retaining rows."""
    digest = hashlib.sha256()
    stream.seek(0)
    while block := stream.read(1024 * 1024):
        digest.update(block)
    stream.seek(0)
    return digest.hexdigest()


def read_url_in_memory(url: str) -> io.BytesIO:
    """Fetch a review asset without writing provider bytes to disk."""
    request = urllib.request.Request(url, headers={"User-Agent": "ApexOS-B06-review-only"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return io.BytesIO(response.read())


def parquet_field_metadata(parquet_file: pq.ParquetFile, name: str) -> tuple[str, str]:
    """Return Parquet logical and physical types for a top-level required field."""
    for index in range(len(parquet_file.metadata.schema)):
        column = parquet_file.metadata.schema.column(index)
        if column.path == name:
            return str(column.logical_type), str(column.physical_type)
    return "<not a leaf column>", "<not a leaf column>"


def render_transcript(source: str, stream: io.BufferedIOBase) -> tuple[str, list[str]]:
    """Render stable schema metadata for the B-06 required validation subset."""
    local_sha256 = sha256_stream(stream)
    parquet_file = pq.ParquetFile(stream)
    arrow_schema = parquet_file.schema_arrow
    missing = [column for column in REQUIRED_COLUMNS if column not in arrow_schema.names]

    lines = [
        "B-06 review-only Parquet schema transcript v1",
        f"source={source}",
        f"pyarrow_version={pyarrow.__version__}",
        f"local_sha256={local_sha256}",
        "required_columns=season,season_type,game_id,yardline_100,touchdown,rush_attempt,pass_attempt",
        "columns:",
    ]
    for name in REQUIRED_COLUMNS:
        if name in arrow_schema.names:
            arrow_field = arrow_schema.field(name)
            parquet_logical, parquet_physical = parquet_field_metadata(parquet_file, name)
            lines.append(
                "- "
                f"name={name}; arrow_logical_type={arrow_field.type}; "
                f"arrow_nullable={str(arrow_field.nullable).lower()}; "
                f"parquet_logical_type={parquet_logical}; "
                f"parquet_physical_type={parquet_physical}"
            )
        else:
            lines.append(f"- name={name}; status=MISSING")
    lines.append(f"required_columns_missing={','.join(missing) if missing else '<none>'}")
    return "\n".join(lines) + "\n", missing


def approved_output_path(value: str, scratch_dir: Path) -> Path:
    """Limit writes to a named ignored scratch directory or committed evidence."""
    output = Path(value).resolve()
    scratch = scratch_dir.resolve()
    if output.is_relative_to(scratch) or output.is_relative_to(ALLOWED_EVIDENCE_ROOT):
        return output
    raise ValueError(
        "--output must be inside the named --scratch-dir or docs/evidence; "
        "the utility will not write elsewhere."
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--parquet", type=Path, help="Local Parquet file to inspect read-only.")
    inputs.add_argument("--asset-url", help="Review asset URL; bytes are held only in memory.")
    parser.add_argument(
        "--scratch-dir",
        type=Path,
        default=Path(".review-evidence"),
        help="Named gitignored scratch root permitted for optional transcript output.",
    )
    parser.add_argument("--output", help="Optional transcript path in scratch or docs/evidence.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    stream: io.BufferedIOBase
    source: str
    if args.parquet:
        source = f"local_parquet={args.parquet.resolve()}"
        stream = args.parquet.open("rb")
    else:
        source = f"asset_url={args.asset_url}"
        stream = read_url_in_memory(args.asset_url)

    try:
        transcript, missing = render_transcript(source, stream)
    finally:
        stream.close()

    sys.stdout.write(transcript)
    if args.output:
        output = approved_output_path(args.output, args.scratch_dir)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(transcript, encoding="utf-8", newline="\n")

    if missing:
        print(
            "ERROR: required B-06 validation columns are absent: " + ", ".join(missing),
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
