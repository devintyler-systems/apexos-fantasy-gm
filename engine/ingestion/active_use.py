"""Scoped active-use scanning for prohibited B-06 dependencies."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


_PROHIBITED_TERM = "nfl_" + "data_py"
_ACTIVE_SUFFIXES = {".py", ".ps1", ".sh", ".bat", ".cmd", ".yml", ".yaml", ".toml"}
_DEPENDENCY_NAMES = {
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "poetry.lock",
    "pdm.lock",
    "uv.lock",
    "pipfile",
    "pipfile.lock",
}
_HISTORICAL_PARTS = {
    "audit",
    "audits",
    "contracts",
    "fixtures",
    "evidence",
    "migration",
    "migrations",
    "review",
    "reviews",
}
_PERMITTED_CONTEXT = re.compile(
    r"\b(prohibit(?:ed|ion)?|must\s+be\s+absent|must\s+not|"
    r"historical|formerly|former|supersed(?:e|ed|es)|negative\s+(?:test|fixture)|"
    r"migrat(?:e|ed|ion)|remov(?:e|ed|al)|zero\s+[^\r\n]*references)\b"
    r"|\bno\b[^\r\n]{0,12}"
    + re.escape(_PROHIBITED_TERM),
    re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class ActiveUseViolation:
    path: Path
    line_number: int
    line: str


def scan_prohibited_active_use(root: Path) -> tuple[ActiveUseViolation, ...]:
    """Return active source/dependency/instruction references under ``root``.

    Historical contracts, fixtures, audits, reviews, migration records, and
    explicit prohibition statements are evidence rather than active use.
    """

    root = Path(root)
    violations: list[ActiveUseViolation] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or _skip(path, root):
            continue
        relative = path.relative_to(root)
        if not _is_scanned_file(relative):
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for line_number, line in enumerate(lines, start=1):
            if _PROHIBITED_TERM not in line.lower():
                continue
            context_start = max(0, line_number - 3)
            context_end = min(len(lines), line_number + 2)
            if _is_permitted_evidence(relative, "\n".join(lines[context_start:context_end])):
                continue
            violations.append(ActiveUseViolation(relative, line_number, line.strip()))
    return tuple(violations)


def _skip(path: Path, root: Path) -> bool:
    relative_parts = {part.lower() for part in path.relative_to(root).parts}
    return bool(relative_parts & {".git", ".pytest_cache", "__pycache__", ".venv", "venv"})


def _is_scanned_file(path: Path) -> bool:
    name = path.name.lower()
    parts = {part.lower() for part in path.parts}
    if name in _DEPENDENCY_NAMES or name.endswith(".lock"):
        return True
    if path.suffix.lower() in _ACTIVE_SUFFIXES:
        return True
    return bool(parts & {"docs", ".github"}) and path.suffix.lower() in {".md", ".txt"}


def _is_permitted_evidence(path: Path, line: str) -> bool:
    parts = {part.lower() for part in path.parts}
    name = path.name.lower()
    if parts & _HISTORICAL_PARTS:
        return True
    if any(marker in name for marker in ("ledger", "addendum", "prohibition")):
        return True
    return _PERMITTED_CONTEXT.search(line) is not None
