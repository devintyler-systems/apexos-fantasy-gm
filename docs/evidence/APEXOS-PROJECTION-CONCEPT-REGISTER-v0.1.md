# ApexOS Projection Concept Register v0.1

## Scope

Read-only visual extraction from two supplied screenshots:

- `ApexOS_Projections.png` — ApexOS SPAMML 2026 Fantrax Draft Board.
- `FantraxProjections.png` — Fantrax projection-list view.

This register records visible concepts and observed relationships only. It does not assert live synchronization, provider methodology, scoring-event decomposition, or a definitive meaning for labels not explained in the screenshots.

## Concept register

| ID | Concept | Visible source | Observed representation | ApexOS treatment / note |
|---|---|---|---|---|
| PCR-01 | Projection source mode | ApexOS | Persistent `DEGRADED SOURCE MODE` banner | User-provided local snapshot; manual live-state entry required; provider FPts is not event-decomposable. |
| PCR-02 | Player identity | Both | Player name; Fantrax also renders position and team under the name | ApexOS table uses `Player` and a normalized `Pool`; raw source identity is preserved in its input snapshot. |
| PCR-03 | Raw position | Fantrax | `QB` is shown before the team abbreviation | ApexOS exposes a normalized pool. Screenshot demonstrates `QB → QB`; other normalization is not visually demonstrated here. |
| PCR-04 | Provider overall rank | Fantrax | `Rk` column, 1–15 for the visible rows | ApexOS displays `RkOv`; visible ordering aligns for the shown quarterbacks. Rank is displayed alongside, not substituted for marginal value. |
| PCR-05 | Provider projected points | Fantrax | `FPTs` column | ApexOS displays `FPts` and treats it as the provider-computed SPAMML projection. It explicitly does not claim raw event-component decomposition. |
| PCR-06 | Provider projected points per game | Fantrax | `FP/G` column | Visible in Fantrax but not shown as a decision-component column in the ApexOS table. |
| PCR-07 | ADP / market context | Both | `ADP` column | ApexOS displays ADP but labels it market context rather than a decision component. Visible values differ slightly between screenshots (for example Josh Allen: 18.3 vs 18.8), so it must not be treated as a stable identity key or projection source. |
| PCR-08 | Bye week | Fantrax | `Bye` column | Visible provider context; not shown in the ApexOS board table in this screenshot. |
| PCR-09 | Opponent / schedule context | Fantrax | `Opp` column with opponent, parenthetical rank, and game time | Not shown as an ApexOS decision component in the screenshot. Semantics should remain provider-context only unless separately contracted. |
| PCR-10 | Player availability/status | Fantrax | `Std` column, visible value `FA` | Provider UI context. ApexOS instead requires explicit local/manual availability state. No equivalence between Fantrax `FA` and ApexOS manual availability is asserted. |
| PCR-11 | Fantrax percentage columns | Fantrax | `%D`, `Ros`, and `+/-` columns | Labels are visible but their provider definitions are not in the screenshot; register them as unresolved provider metadata, not decision inputs. |
| PCR-12 | UI affordances | Fantrax | Star and people icons beside each player | Visible interaction affordances; no ApexOS calculation meaning is inferred. |
| PCR-13 | Draft context | ApexOS | Current manual overall pick 4; next planned Professor FleX pick 29 | Planned schedule is used for decision context; manual state is required for live draft events. |
| PCR-14 | Recommendation | ApexOS | `recommendation: Josh Allen (QB)` | A distinct decision-layer output, separate from provider rank and raw FPts. |
| PCR-15 | Normalized position pool | ApexOS | `Pool` column, visible `QB` | Roster/decision grouping. It is distinct from raw provider position presentation. |
| PCR-16 | Replacement anchor score | ApexOS | `Anchor score` column; visible QB anchor 169.2 | Provider FPts at the canonical pool replacement anchor; it is displayed separately from marginal replacement value. |
| PCR-17 | Marginal replacement value | ApexOS | `Marginal replacement value` column; Josh Allen 72 | Visible relationship: 241.2 FPts minus 169.2 anchor equals 72. This is a marginal delta, not the raw anchor score. |
| PCR-18 | Scarcity component | ApexOS | `Scarcity component` column; visible QB value 0.05555555555555555 | Explicit normalized/weighted decision component. |
| PCR-19 | Roster-fit component | ApexOS | `Roster-fit component` column; visible QB value 1 | Explicit decision component for an open eligible QB slot. |
| PCR-20 | Specialist suppression | ApexOS | `Suppression penalty` column and K/D_O explanatory text | K is suppressed before round 6 unless its documented wait-cost exception passes; D/O is suppressed before the final round unless its documented marginal-advantage exception passes. |
| PCR-21 | Reconciled recommendation value | ApexOS | `Reconciled value` column; Josh Allen 123.45555555555553 | Decision-layer score, visibly separate from FPts, rank, and ADP. |
| PCR-22 | Manual availability | ApexOS | Local/manual availability label and select control | In-memory local state only; not validated live-platform state; discarded on reload. |
| PCR-23 | Offline/provenance limitation | ApexOS | Artifact metadata says no network, API, storage, current provider sync, or automatic draft action | Board is a local offline artifact, not a provider platform session. |

## Observed field mappings

| Fantrax visible field | ApexOS visible field | Relationship observed |
|---|---|---|
| Name | Player | Same visible player identities for the shown QB rows. |
| Rk | RkOv | Same visible rank sequence for the shown QB rows. |
| FPTs | FPts | Same visible point values for the shown QB rows. |
| ADP | ADP | Both display ADP; values are not byte-identical across screenshots and are display/context only in ApexOS. |
| QB–team text | Pool | ApexOS reduces the visible raw QB position to the QB decision pool. |
| — | Anchor score | ApexOS decision-layer field; not visible in Fantrax source view. |
| — | Marginal replacement value | ApexOS derived field: `max(0, FPts − anchor score)`. |
| — | Scarcity / roster fit / suppression / reconciled value | ApexOS decision-layer fields; not visible as Fantrax source fields. |

## Example: Josh Allen

| Field | Fantrax screenshot | ApexOS screenshot |
|---|---:|---:|
| Player | Josh Allen | Josh Allen |
| Position / pool | QB–BUF | QB |
| Rank | 1 | 1 |
| Provider points | 241.2 | 241.2 |
| ADP | 18.3 | 18.8 |
| Replacement anchor score | — | 169.2 |
| Marginal replacement value | — | 72 |
| Scarcity component | — | 0.05555555555555555 |
| Roster-fit component | — | 1 |
| Suppression penalty | — | 0 |
| Reconciled value | — | 123.45555555555553 |

## Explicit non-claims and open items

- The screenshots do not establish how Fantrax calculates FPts, FP/G, `%D`, `Ros`, or `+/-`.
- The screenshots do not expose raw touchdown, yardage, reception, or other scoring-event components.
- Fantrax opponent/status/percentage columns are not evidence that ApexOS uses them in marginal-value math.
- Visible ADP differences confirm it should be treated as context, not as a stable calculation input.
- The screenshots do not establish live draft state, provider freshness, or platform-side availability.

