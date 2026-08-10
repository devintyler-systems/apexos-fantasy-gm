# Draft Round Order Map Contract — v1.1 Clarification

**Resolves:** Builder-surfaced version-binding conflict (B-04 implementation)
**Supersedes:** The literal example value in `draft-round-order-map-contract-v1.0.md` Section 4b
**Status:** APPROVED
**Created:** 2026-08-10

---

## 1. Decision Statement

**Use `spamml-2026-v0.3` (the current League Rules Contract) in all generated B-04 artifacts. The `spamml-2026-v0.2` value shown in the original contract's Section 4b JSON example was illustrative, not a pinned dependency.** `design decision`

---

## 2. Root Cause

Contracts in this repository are living documents that get superseded as league details resolve (v0.2 → v0.3 resolved U03, the pick-timer unknown). The Draft Round Order Map Contract was authored on 2026-08-09 when v0.2 was current, and its Section 4b example JSON hardcoded that version string as sample output. When v0.3 shipped the next day, nothing in the original contract explicitly stated whether that example value was a fixed dependency ("this artifact must always cite v0.2") or an illustrative placeholder ("this field gets populated with whatever the current version is"). Builder correctly refused to guess and escalated instead of picking one silently. `confirmed evidence` (Builder's own reasoning)

---

## 3. General Rule (applies to every contract in this repo, not just B-04)

**Any `league_rules_version`, `projection_artifact_version`, or similar version-reference field shown in an example JSON/YAML block within a contract is illustrative only, UNLESS the contract explicitly states "this artifact is pinned to version X and must not be regenerated against a newer version."** No contract in this repo currently states that pinning condition. Every such field is dynamically populated at artifact-generation time from whichever contract version is currently active in `contracts/league_rules/`. `design decision`

This is consistent with the reproducibility doctrine already established: an artifact generated today cites today's league rules version; if the league rules contract is later superseded, PREVIOUSLY generated artifacts keep their original citation (they are frozen, per Projection Artifact Contract PA04-style immutability), but any NEW artifact generation run always reads and cites the current version at generation time.

---

## 4. Direct Resolution for B-04

```text
data/processed/draft_position_pick_map_spamml_2026.json
  "league_rules_version": "spamml-2026-v0.3"   <- use current version, not the v0.2 example

Implementation requirement: the Draft Round Order Map builder script must READ the
current league_rules_version dynamically (e.g., from the filename or a version field
inside contracts/league_rules/spamml-2026-v0.3.yaml), never hardcode "v0.2" or "v0.3"
as a literal string in round_order_map.py. This is the same "no hardcoded constants"
principle already enforced in the Scoring Engine Contract (SE01), applied here to
version strings instead of point values.
```

---

## 5. Acceptance Test Addition

### T11 — Dynamic Version Citation, Not Hardcoded (BLOCK)
```
The generated JSON artifact's league_rules_version field must match whatever
league rules contract file is currently present in contracts/league_rules/
at generation time (currently v0.3). Static code analysis must confirm no
literal "v0.2" or "v0.3" string exists in round_order_map.py itself —
the version is read from the config file, not written into the module.
```

---

## 6. Builder Unblock Confirmation

Builder is cleared to proceed with the B-04 branch as described: `engine/draft/round_order_map.py`, package initializers, the two `data/processed/` artifacts, and test-scaffold wiring — using `spamml-2026-v0.3` as the `league_rules_version` value, sourced dynamically rather than hardcoded, per Section 4 above. No other changes to the previously confirmed B-04 scope are required.

---

## 7. Decision Ledger Entry

This is a calibration fix, not a structural change — it clarifies an ambiguity Builder correctly caught rather than silently resolving. The general rule in Section 3 should prevent this exact class of question from recurring on future tickets (B-08 Projection Artifact, B-10 Scoring Engine, etc.) that also reference `league_rules_version` fields.
