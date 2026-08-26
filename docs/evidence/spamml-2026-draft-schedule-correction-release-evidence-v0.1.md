# SPAMML 2026 Draft Schedule Correction — Release Evidence

- Artifact name: SPAMML 2026 Draft Schedule Correction Release Evidence
- Version: 0.1
- Owner: devintyler-systems / ApexOS Fantasy GM
- Status: accepted test evidence for PR amendment
- Pull request: [#49](https://github.com/devintyler-systems/apexos-fantasy-gm/pull/49)
- Base SHA: `f0cb286791683fd43932021bf19595d5f66a9838`
- Evidence-capture parent SHA: `024a528790d22fb00b004ea1fe36e7b2a21a28ab`
- Evidence-capture timestamp (UTC): `2026-08-26T23:21:07Z`

The amended commit SHA is intentionally not embedded in this document.
This document is bound by the Git commit that contains it and must be
verified against the updated GitHub PR #49 head after push.

## Raw-PDF Python Attestation

The authoritative verification is the fail-closed Python test
`test_raw_draft_order_pdf_integrity_and_manifest_attestation_fail_closed` in
`tests/acceptance/test_draft_round_order_map.py`. Its passing result is
included in the complete round-order suite output below.

- PDF path: `data/raw/draft_order/spamml_2026_draft_order.pdf`
- Expected SHA-256: `da7208e307a7fe6f56b06a5c8ae02291815f72a7424a8f8e1170820c98f40de6`
- Observed SHA-256: `da7208e307a7fe6f56b06a5c8ae02291815f72a7424a8f8e1170820c98f40de6` (the passing Python attestation asserts this digest)
- Expected byte count: `50339`
- Observed byte count: `50339` (the passing Python attestation asserts this length)
- Manifest: `data/raw/draft_order/spamml_2026_draft_order_manifest_v0.1.json`
- Manifest-attestation result: passed. The test fail-closes on a missing or changed PDF, digest, byte count, `all_league_order` role, preserved path, source SHA-256, or page-count evidence. It requires exactly one `all_league_order` record and page count `1`.

## Pytest Evidence

All commands used the external pytest base temporary root
`C:\Projects\apexos-fantasy-gm\.pytest-evidence-tmp-pr49\`. The following are the
complete unabridged captured stdout/stderr streams. Each suite completed with
no failures, errors, or skips; the final passed total is also its completed
test-item count.

### B-07 baseline

Command:

```text
python -m pytest tests/acceptance/test_b07_baseline.py -ra --basetemp C:\Projects\apexos-fantasy-gm\.pytest-evidence-tmp-pr49\b07-baseline
```

Collection/result summary: 54 passed; failures 0, errors 0, skips 0.

```text
......................................................                   [100%]
54 passed in 1.03s

```

### Draft round order and raw-PDF attestation

Command:

```text
python -m pytest tests/acceptance/test_draft_round_order_map.py -ra --basetemp C:\Projects\apexos-fantasy-gm\.pytest-evidence-tmp-pr49\round-order
```

Collection/result summary: 11 passed; failures 0, errors 0, skips 0.

```text
...........                                                              [100%]
11 passed in 2.50s

```

### Draft seat-assignment contract validation

Command:

```text
python -m pytest tests/acceptance/test_draft_seat_assignment_contract_validation.py -ra --basetemp C:\Projects\apexos-fantasy-gm\.pytest-evidence-tmp-pr49\seat-assignment
```

Collection/result summary: 29 passed; failures 0, errors 0, skips 0.

```text
.............................                                            [100%]
29 passed in 0.54s

```

### Live-state consumer

Command:

```text
python -m pytest tests/acceptance/test_live_state_consumer.py -ra --basetemp C:\Projects\apexos-fantasy-gm\.pytest-evidence-tmp-pr49\live-state
```

Collection/result summary: 25 passed; failures 0, errors 0, skips 0.

```text
.........................                                                [100%]
25 passed in 0.97s

```

### Full acceptance suite

Command:

```text
python -m pytest tests/acceptance -ra --basetemp C:\Projects\apexos-fantasy-gm\.pytest-evidence-tmp-pr49\full-acceptance
```

Collection/result summary: 318 passed; failures 0, errors 0, skips 0.

```text
........................................................................ [ 22%]
........................................................................ [ 45%]
........................................................................ [ 67%]
........................................................................ [ 90%]
..............................                                           [100%]
318 passed in 5.74s

```

## Accepted Map and Schedule Evidence

- Map result: 128 picks, 16 managers, eight picks per manager, with forward/inverse consistency.
- Professor FleX picks: `[4, 29, 45, 52, 68, 93, 109, 116]`
- Draft time (local): `2026-08-30 16:00 America/Los_Angeles`
- Draft time (UTC): `2026-08-30T23:00:00Z`
- Time-zone evidence: `PDT / -07:00`

## Protected Boundaries

No schedule, runtime, contract, raw PDF, B-06, B-07, dependency, CI,
provider, candidate, production, endpoint, pointer, recommendation, or
manual-live-event-precedence behavior changed in this amendment.
