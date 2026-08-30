"""Immutable provider-evidence ingestion adapters."""

from engine.ingestion.nflverse_pbp import (
    IngestionOutcome,
    IngestionResult,
    ingest_nflverse_pbp_season,
)
from engine.ingestion.nflverse_raw_evidence import (
    EvidenceLineage,
    HttpFetchResponse,
    HttpTransport,
    HttpxHttpTransport,
    IdentityQuarantineRecord,
    NflverseAssetRequest,
    RawEvidenceCaptureResult,
    capture_nflverse_raw_evidence,
    result_to_dict,
)

__all__ = [
    "EvidenceLineage",
    "HttpFetchResponse",
    "HttpTransport",
    "HttpxHttpTransport",
    "IdentityQuarantineRecord",
    "IngestionOutcome",
    "IngestionResult",
    "NflverseAssetRequest",
    "RawEvidenceCaptureResult",
    "capture_nflverse_raw_evidence",
    "ingest_nflverse_pbp_season",
    "result_to_dict",
]
