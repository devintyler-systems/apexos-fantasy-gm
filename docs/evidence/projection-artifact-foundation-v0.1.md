# Projection Artifact Foundation v0.1 Evidence

Status: passed fixture-only foundation. Contract: `contracts/projections/apexos-player-projection-artifact-v0.1.yaml` version `0.1`. Base: `28751c4eb686573c33503bac56138e83fc8fc878`.

The implementation accepts only local fixture/ApexOS-owned evidence carrying a SHA-256, retrieval time, effective time, and approved role. Text fixture evidence is hashed over its Git-portable LF bytes so a Windows checkout cannot alter its declared identity. It deterministically derives an input snapshot ID and serializes byte-identical artifact and manifest JSON for identical inputs. It validates canonical player/team snapshot references and exact raw/final scoring-event schemas, while intentionally calculating no scoring.

Fixture boundary: `tests/fixtures/projection_artifact_v0_1/valid_input.json` is the sole supplied fixture input. It is not a live 2026 player projection artifact. External ranking, ADP, and analyst-projection roles are rejected as benchmark-only. No provider retrieval, network call, raw-data use, B-06, B-07, candidate, endpoint, external write, scoring, PRV, availability, roster fit, or recommendation behavior exists in v0.1.

Executed with external pytest storage under `C:\tmp\apexos-projection-artifact-v01`:

```text
python -B -m pytest tests/acceptance/test_projection_artifact_v0_1.py -ra --basetemp C:\tmp\apexos-projection-artifact-v01\projection
17 passed in 0.31s

python -B -m pytest tests/acceptance/test_live_state_consumer.py -ra --basetemp C:\tmp\apexos-projection-artifact-v01\live-state
25 passed in 0.92s

python -B -m pytest tests/acceptance/test_league_rules_version_parsing.py -ra --basetemp C:\tmp\apexos-projection-artifact-v01\league-rules
8 passed in 0.16s

python -B -m pytest tests/acceptance -ra --basetemp C:\tmp\apexos-projection-artifact-v01\full-acceptance
336 passed in 5.85s
```

The CLI proof used only temporary output paths:

```text
python tools/build_projection_artifact_v0_1.py validate --input tests/fixtures/projection_artifact_v0_1/valid_input.json
python tools/build_projection_artifact_v0_1.py build --input tests/fixtures/projection_artifact_v0_1/valid_input.json --output <temporary-path>
```

PA01–PA13 cover schema-valid construction, byte identity, missing/hash/post-as-of/unapproved evidence, benchmark input rejection, canonical identity ambiguity, audited overrides, frozen overwrite, prohibited decision fields, B-06/B-07 isolation, and local deterministic CLI output. League Rules v0.6 delegates the sole planned schedule timestamp to the finalized v1.2 seat-assignment artifact; manual live events and validated B-05 session state remain authoritative over planned state.
