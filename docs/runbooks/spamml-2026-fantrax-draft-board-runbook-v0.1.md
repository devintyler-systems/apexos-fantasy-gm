# SPAMML 2026 Fantrax Draft Board Runbook v0.1

1. Operator stages the immutable user-provided CSVs outside Git.
2. Verify exact headers and record SHA-256/byte length; never copy CSVs into
   the repository.
3. Build locally with `tools/build_fantrax_draft_board.py`; output is a new
   timestamped artifact under `artifacts/draft_board/spamml-2026/`.
4. Open `spamml_2026_draft_board.html` directly as `file://`. It has no server,
   API, storage, automatic update, or draft-action path.
5. Enter availability manually in the browser. It is local/in-memory only,
   discarded on reload, and recalculates the displayed choice deterministically;
   it is never a claim of provider freshness or live draft state.

Inspect output provenance before use: `as_of_timestamp`, input snapshot ID,
projection version, league ID (`spamml-2026`), manager seat (`4`), configuration
and optimizer versions, degraded source mode, uncertainty, and limitations must
be present. The projection version identifies the deterministic local artifact,
not a provider methodology version.

For a selected candidate, verify replacement anchor score, marginal replacement
value, scarcity component, roster-fit component, suppression penalty, and the
reconciled recommendation score. Manual changes recalculate in-memory from
embedded normalized inputs; they do not reuse a stale fallback, wait cost,
availability count, or recommendation value.

After each manual drafted/unavailable action, verify both the row's visible
`Local/manual` status badge and its selected availability control. Then verify
the revised recommendation, fallback, wait cost, anchor, marginal replacement,
scarcity, fit, penalty, and reconciled value before acting. Reload clears local
manual state.

Persistent limitations: Fantrax FPts is a provider league-score projection,
not decomposed scoring-event data; source exports omit export timestamp and
provider methodology version; two-point projection details are unavailable;
the planned sequence is not live-state evidence; and the 2025 file is context
only. If input/config validation fails, stop and use no recommendation.
