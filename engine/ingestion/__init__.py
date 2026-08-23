"""Immutable provider-evidence ingestion adapters."""

from engine.ingestion.nflverse_pbp import (
    IngestionOutcome,
    IngestionResult,
    ingest_nflverse_pbp_season,
)

__all__ = [
    "IngestionOutcome",
    "IngestionResult",
    "ingest_nflverse_pbp_season",
]
