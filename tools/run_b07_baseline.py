"""Local-only B-07 v0.1 baseline validation runner and inspector."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from engine.projections.b07_baseline import (
    BaselineValidationError,
    SourceSpec,
    inspect_validation_artifact,
    run_baseline_validation,
    what_if,
)


RETAINED_PACKAGE_FILES = (
    "lookup-tables.json",
    "metrics.json",
    "review-report.md",
    "scored-events.jsonl",
)
MUTABLE_POINTER_NAMES = frozenset(("current.json", "latest", "latest.json"))


def retained_inspection_evidence(root: str | Path) -> dict:
    """Return review-surface evidence after fail-closed package inspection."""
    path = Path(root).resolve()
    result = inspect_validation_artifact(path)
    artifact_files = result.get("artifact_files")
    if not isinstance(artifact_files, dict) or set(artifact_files) != set(
        RETAINED_PACKAGE_FILES
    ):
        raise BaselineValidationError(
            "B07_ARTIFACT_PACKAGE_FILE_SET_MISMATCH",
            f"expected={list(RETAINED_PACKAGE_FILES)} actual={sorted(artifact_files or {})}",
        )

    pointer_paths = sorted(
        str(candidate)
        for candidate in path.iterdir()
        if candidate.name.casefold() in MUTABLE_POINTER_NAMES
        and (candidate.exists() or candidate.is_symlink())
    )
    if pointer_paths:
        raise BaselineValidationError(
            "B07_ARTIFACT_MUTABLE_POINTER_PRESENT",
            f"paths={pointer_paths}",
        )

    package_digests = {
        name: artifact_files[name]["sha256"] for name in RETAINED_PACKAGE_FILES
    }
    package_digests.update(
        {
            "manifest.json": result["manifest_sha256"],
            "validation-artifact.json": result["validation_artifact_sha256"],
        }
    )
    return {
        "artifact_root": str(path),
        "current_or_latest_pointer_exists": False,
        "current_or_latest_pointer_paths": [],
        "package_digests": package_digests,
        **result,
    }


def _source(value: str) -> SourceSpec:
    parts = value.split("|", 3)
    if len(parts) != 4:
        raise argparse.ArgumentTypeError(
            "source must be SEASON|PAYLOAD_PATH|MANIFEST_PATH|POINTER_PATH"
        )
    try:
        season = int(parts[0])
    except ValueError as exc:
        raise argparse.ArgumentTypeError("source season must be an integer") from exc
    return SourceSpec(
        season=season,
        payload_path=Path(parts[1]),
        manifest_path=Path(parts[2]),
        pointer_path=Path(parts[3]),
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--what-if", action="store_true")
    mode.add_argument("--execute", action="store_true")
    mode.add_argument("--inspect", metavar="ARTIFACT_ROOT")
    parser.add_argument(
        "--contract",
        type=Path,
        default=Path("contracts/projections/b07_v0_1_contract.yaml"),
    )
    parser.add_argument("--source", action="append", type=_source, default=[])
    parser.add_argument(
        "--source-config",
        type=Path,
        help="Local JSON array of season/payload_path/manifest_path/pointer_path mappings.",
    )
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--repository-sha")
    parser.add_argument("--repository-worktree")
    parser.add_argument("--run-id")
    return parser


def _sources_from_args(args: argparse.Namespace) -> list[SourceSpec]:
    if args.source and args.source_config:
        _parser().error("use --source or --source-config, not both")
    if args.source_config:
        try:
            values = json.loads(args.source_config.read_text(encoding="utf-8"))
            return [
                SourceSpec(
                    season=int(value["season"]),
                    payload_path=Path(value["payload_path"]),
                    manifest_path=Path(value["manifest_path"]),
                    pointer_path=Path(value["pointer_path"]),
                )
                for value in values
            ]
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            _parser().error(f"invalid --source-config: {exc}")
    return list(args.source)


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    sources = _sources_from_args(args)
    try:
        if args.inspect:
            result = retained_inspection_evidence(args.inspect)
        elif args.what_if:
            if args.output_root is None or len(sources) != 3:
                _parser().error("--what-if requires exactly three --source values and --output-root")
            result = what_if(args.contract, sources, args.output_root)
        else:
            required = {
                "--output-root": args.output_root,
                "--repository-sha": args.repository_sha,
                "--repository-worktree": args.repository_worktree,
                "--run-id": args.run_id,
            }
            missing = [name for name, value in required.items() if not value]
            if len(sources) != 3:
                missing.append("exactly three --source values")
            if missing:
                _parser().error(f"--execute missing: {', '.join(missing)}")
            result = run_baseline_validation(
                contract_path=args.contract,
                sources=sources,
                output_root=args.output_root,
                repository_sha=args.repository_sha,
                repository_worktree=args.repository_worktree,
                run_id=args.run_id,
            )
    except BaselineValidationError as exc:
        print(
            json.dumps(
                {
                    "status": "failed_or_stale",
                    "reason_code": exc.reason_code,
                    "detail": exc.detail,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
