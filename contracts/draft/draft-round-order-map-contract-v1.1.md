# Draft Round Order Map Contract v1.1

**Status:** Approved structural correction
**Effective season:** 2026
**Authority:** `contracts/draft/spamml-2026-round-order-map-v1.0.yaml`

## Decision

The finalized SPAMML 2026 all-league order is the sole planned-schedule authority. Runtime must load the versioned 128-pick artifact; it must not present the generic pivot formula as the finalized 2026 schedule.

The raw-evidence manifest retains the accepted all-league PDF digest, the Professor FleX reconciliation-PDF digest, extraction identity, and the 2026-08-25 operator confirmation. The artifact normalizes all 128 pick assignments and provides forward and inverse mappings.

## Selection and fallback

For SPAMML 2026, `engine/draft/round_order_map.py` loads only `spamml-2026-round-order-map-v1.0.yaml`. Missing, malformed, incomplete, duplicate, or non-invertible finalized data fails closed as unavailable; no generic formula may substitute for it.

Manual live-draft events and validated B-05 session state outrank this planned schedule. The artifact has no live-status authority and cannot create an external action, recommendation, or platform sync.

## Migration

The prior unversioned processed CSV and JSON remain preserved as non-consumable superseded generic-model outputs. New versioned CSV and JSON derivatives retain the same accepted source identity and are derived only from the versioned 2026 authority.

## Acceptance

- Exactly 128 unique picks span 1 through 128.
- Exactly 16 canonical managers receive exactly 8 picks each.
- Forward and inverse mappings agree.
- Professor FleX at seat 4 resolves to `[4, 29, 45, 52, 68, 93, 109, 116]`.
- The 2026 draft start is derived from `2026-08-30 16:00 America/Los_Angeles`, producing `2026-08-30T23:00:00Z`.
