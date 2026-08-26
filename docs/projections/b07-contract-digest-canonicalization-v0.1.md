# B-07 Contract Digest Canonicalization v0.1

**Status:** Approved cross-platform checkout-integrity repair
**Scope:** `contracts/projections/b07_v0_1_contract.yaml` digest attestation only

## Decision

The canonical B-07 contract digest is the SHA-256 of the contract's UTF-8 bytes after CRLF is normalized to LF. A UTF-8 BOM and residual lone carriage-return bytes are invalid and fail closed before digest comparison.

The frozen contract file and SHA-256 `7cd8e294ca1b6fefadb1d35472e9a421c4829dd6f37dc6690abf2513b9da0abc` are unchanged. This corrects cross-platform checkout integrity only; it is not a B-07 recalibration or contract change.

## Boundary

No candidate, production xTD, artifact, endpoint, pointer, recommendation, provider, dependency, or external-write behavior is authorized by this repair. A true canonical-byte content change continues to fail closed with `B07_CONTRACT_DIGEST_MISMATCH`.
