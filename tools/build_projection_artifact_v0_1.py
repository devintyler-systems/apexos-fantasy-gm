"""Local, standard-library CLI for fixture-only projection artifact v0.1."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engine.projections.projection_artifact_v0_1 import ProjectionArtifactError, build_artifact


def _load_input(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProjectionArtifactError("PA01_INPUT_UNREADABLE", f"could not read input: {path}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fixture-only ApexOS projection artifact builder v0.1")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "build"):
        command = subparsers.add_parser(name)
        command.add_argument("--input", required=True)
        if name == "build":
            command.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    input_path = Path(args.input).resolve()
    try:
        document = _load_input(input_path)
        if args.command == "validate":
            artifact, _, _ = build_artifact(document, input_path.parent)
            print(f"VALIDATION_PASSED input_snapshot_id={artifact['input_snapshot_id']}")
            return 0
        output = Path(args.output).resolve()
        if "data/processed" in output.as_posix():
            raise ProjectionArtifactError("PA13_LIVE_OUTPUT_PROHIBITED", "v0.1 may not write data/processed")
        existing = None
        artifact_path = output / "projection_artifact.json"
        if artifact_path.exists():
            existing = json.loads(artifact_path.read_text(encoding="utf-8"))
        artifact, artifact_bytes, manifest_bytes = build_artifact(document, input_path.parent, existing)
        output.mkdir(parents=True, exist_ok=True)
        artifact_path.write_bytes(artifact_bytes)
        (output / "projection_artifact.manifest.json").write_bytes(manifest_bytes)
        print(f"BUILD_PASSED input_snapshot_id={artifact['input_snapshot_id']} output={output}")
        return 0
    except ProjectionArtifactError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
