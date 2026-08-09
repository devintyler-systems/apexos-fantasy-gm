# Fantasy Football Architect — Model Stack & Planning Ideas (Design Reference)

> **Status: design-reference.** Brainstorm notes on AI model stack selection and architecture principles for the ApexOS build. Informs Builder/Operator tooling choices, not league-specific decisions.

## Recommended Model Stack (per original notes)

| Job | Best Fit | Why |
|---|---|---|
| Product architecture, build plan | Claude Opus | Long-context reasoning, clear specs, requirements decomposition |
| Full-stack coding, debugging, tool calling | GPT-5 | Implementation loops: Python/SQL/API, tests, refactors |
| Fast/cheap extraction, classification | GPT-5 mini / Claude Sonnet | News ingestion, player-note summarization, tagging |
| Google ecosystem/research cross-check | Gemini 2.5 Pro | Second opinion, large document ingestion |

## One Important Design Rule

> Treat the LLM as the front office, not the quarterback. It can explain, plan, detect ambiguity, ask for league settings, narrate recommendations — but every actual draft pick, waiver priority, or lineup recommendation should be traceable to projections, simulations, roster constraints, and live data.

This is the same separation enforced in ApexOS shared doctrine (LLMs plan/extract/orchestrate/explain; deterministic services/projections/optimizers recommend).

## ROI Priority (per original notes)

| Initiative | ROI | Build Verdict |
|---|---|---|
| League settings + projections + draft optimizer | Very high | Build first |
| Platform sync (Sleeper-first) | Very high | Start Sleeper-first (N/A for SPAMML — custom manual platform) |
| Draft recommendation engine | Very high | Build as MVP centerpiece |
| Weekly waiver/start-sit/trade tools | High | Build after draft core |
| Explainability layer | High | Build alongside recommendations |

## Recommendation Payload Shape (illustrative example from original notes)

```json
{
  "recommendation": "Player X",
  "alternatives": ["Player Y", "Player Z"],
  "projected_points": 214.8,
  "value_over_replacement": 31.4,
  "roster_fit_score": 0.87,
  "availability_next_round": 0.22,
  "confidence": 0.71,
  "reason_codes": ["RB scarcity", "team need", "ADP value"]
}
```

This is a template only — field names and exact structure are finalized in the ApexOS Recommendation Artifact Contract, not this document.

## Gaps Flagged in Original Notes (still relevant)

- Data-source audit: source, cost, rate limit, freshness, ToS, coverage, historical depth, fallback — addressed via ApexOS Data Source and Connector Register (pending).
- Versioned projections: source, model_version, run_timestamp, input snapshot — addressed via Projection Artifact Contract (in progress).
- Backtesting harness: replay historical drafts vs. optimizer strategy vs. baseline ADP — deferred to Phase 2 per MVP scope table.
- Live-draft failure plan: websocket dies, sync lags, name mismatches, dual-device drafting — addressed via Live-Draft Degraded Mode Runbook (pending, item 7 in build sequence).

---
*Converted from `Fantasy_Football_Architect_Planning_Ideas.md`, uploaded 2026-08-09.*
