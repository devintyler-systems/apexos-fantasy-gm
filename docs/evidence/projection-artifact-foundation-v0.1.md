# Projection Artifact Foundation v0.1 Evidence

Status: passed fixture-only foundation. Contract: `contracts/projections/apexos-player-projection-artifact-v0.1.yaml` version `0.1`. Base: `28751c4eb686573c33503bac56138e83fc8fc878`.

The implementation accepts only local fixture/ApexOS-owned evidence carrying a SHA-256, provider, one approved source locator (an absolute HTTP/HTTPS URL or a non-network provider record ID), parser version, retrieval time, effective time, and approved role. Text fixture evidence is hashed over its Git-portable LF bytes so a Windows checkout cannot alter its declared identity. It deterministically derives an input snapshot ID and serializes byte-identical artifact and manifest JSON for identical inputs. It validates canonical player/team snapshot references and exact raw/final scoring-event schemas, while intentionally calculating no scoring.

Time-integrity boundary: v0.1 fails closed when source retrieval or effective time is after the artifact as-of timestamp; it validates temporal non-futurity only and does not certify source freshness. Artifact- and row-level `data_freshness_status` plus `known_limitations` must surface incomplete or stale conditions. A separately approved, source-specific freshness policy is a hard gate before non-fixture 2026 evidence or any live artifact may be authorized; this foundation does not invent a freshness threshold or source SLA.

Fixture boundary: `tests/fixtures/projection_artifact_v0_1/valid_input.json` is the sole supplied fixture input. It is not a live 2026 player projection artifact. External ranking, ADP, and analyst-projection roles are rejected as benchmark-only. No provider retrieval, network call, raw-data use, B-06, B-07, candidate, endpoint, external write, scoring, PRV, availability, roster fit, or recommendation behavior exists in v0.1.

Remediation verification executed with external pytest storage under `C:\tmp\apexos-pr50-remediation`:

```text
python -B -m pytest tests/acceptance/test_projection_artifact_v0_1.py -ra --basetemp C:\tmp\apexos-pr50-remediation\projection
26 passed in 0.30s

python -B -m pytest tests/acceptance/test_live_state_consumer.py -ra --basetemp C:\tmp\apexos-pr50-remediation\live-state
25 passed in 1.11s

python -B -m pytest tests/acceptance/test_league_rules_version_parsing.py -ra --basetemp C:\tmp\apexos-pr50-remediation\league-rules
8 passed in 0.20s

python -B -m pytest tests/acceptance -ra --basetemp C:\tmp\apexos-pr50-remediation\full-acceptance
345 passed in 6.01s
```

The CLI proof used only temporary output paths:

```text
python tools/build_projection_artifact_v0_1.py validate --input tests/fixtures/projection_artifact_v0_1/valid_input.json
python tools/build_projection_artifact_v0_1.py build --input tests/fixtures/projection_artifact_v0_1/valid_input.json --output <temporary-path>
```

PA01–PA13 cover schema-valid construction, byte identity, complete provenance (provider, locator, parser version), missing/hash/post-as-of retrieval/post-as-of effective-time/unapproved evidence, benchmark input rejection, canonical identity ambiguity, audited overrides, frozen overwrite, prohibited decision fields, B-06/B-07 isolation, and local deterministic CLI output. League Rules v0.6 delegates the sole planned schedule timestamp to the finalized v1.2 seat-assignment artifact; manual live events and validated B-05 session state remain authoritative over planned state.
