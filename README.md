# ApexOS: Fantasy GM

League-aware fantasy football draft and full-season decision platform built on versioned data, projections, optimization, and explainable recommendations.

## Current Stage

Architecture and MVP definition.

## Product Rule

The application does not use LLM narrative as the source of fantasy recommendations. Recommendations must be traceable to league rules, roster state, valid inputs, versioned projections, deterministic decision logic, and explicit user controls.

## Repository Authority

- `docs/architecture/`: approved product and system architecture
- `docs/contracts/`: versioned data, rules, projection, and recommendation contracts
- `docs/reviews/`: independent release-gate findings
- `configs/`: versioned configuration, never secrets
- `src/`: application and decision-engine code
- `tests/`: automated verification

No production application code is authorized until the League Rules Contract and Draft Recommendation Contract are approved.
