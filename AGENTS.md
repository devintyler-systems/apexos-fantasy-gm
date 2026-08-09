# ApexOS: Fantasy GM Repository Rules

## Source of Truth
GitHub is canonical for code, schemas, versioned contracts, tests, decision records, and release reviews.

## Non-Negotiables
- Never commit secrets, raw credentials, API keys, tokens, or private league exports.
- Do not overwrite projection or recommendation artifacts in place.
- Every recommendation must retain an as-of timestamp, input snapshot ID, and version identifiers.
- Do not use future information in historical or live decision artifacts.
- Treat platform integrations as read-only until explicitly approved.
- Schema changes require migration notes and tests.
- Model or optimizer changes require a documented baseline comparison and evaluation plan.

## Current Build Gate
Do not begin application implementation until these artifacts exist:
1. League Rules Contract
2. Product Charter
3. Data Source and Connector Register
4. Canonical Data Model
5. Draft Recommendation Contract
6. MVP Acceptance Gates
