# FinSight MVP product specification

## Product statement

FinSight helps digital-banking product teams translate natural-language onboarding questions into reviewable KPI, funnel, segmentation, and A/B experiment analyses.

## Design principles

1. **LLM for ambiguity; Python for numerical truth.**
2. **Bounded workflows before open-ended automation.**
3. **Expose the plan and result, not only the narrative.**
4. **Describe uncertainty and preserve human decision authority.**
5. **Reject unsupported scope instead of inventing an analysis.**

## Primary user journey

1. The user opens the local Streamlit application.
2. FinSight loads reproducible synthetic data or validates an uploaded CSV.
3. The user asks a product question in ordinary business language.
4. The LLM returns a structured, allowlisted analysis plan.
5. Python executes the selected calculation.
6. The LLM interprets the immutable result.
7. The UI shows the explanation, table, chart, routing rationale, and audit trail.
8. A human decides whether more analysis or organizational review is required.

## Functional requirements

### Data input

- Generate 5K–50K synthetic customers with a fixed seed.
- Accept a CSV upload and switch the active data source.
- When column names differ, show conservative mapping suggestions and require user confirmation.
- Validate required columns before showing KPIs or accepting questions.
- Show a clear error without a traceback when the contract is invalid.
- Never commit API keys or uploaded data to the repository.

### LLM planner

- Return structured output matching the `AnalysisPlan` contract.
- Select only KPI, funnel, segmentation, or experiment workflows.
- Use only approved metrics, dimensions, and filters.
- For experiments, compare the complete Control and Treatment groups.
- Do not calculate numbers or invent fields.

### Deterministic analytics

- KPI: define and calculate onboarding metrics.
- Funnel: calculate stage counts, overall conversion, step conversion, and drop-off.
- Segmentation: compare activation across device, acquisition channel, or customer segment.
- Experiment: calculate group rates, absolute and relative lift, 95% confidence interval, two-sided p-value, and a 30-day engagement guardrail.

### LLM interpreter

- Lead with the result and cite only supplied numbers.
- Distinguish descriptive analysis from experimental evidence.
- Use human-readable business labels.
- State relevant assumptions and limitations.
- Recommend one bounded next step using only available fields.
- Never authorize a full rollout when experiment-integrity checks are incomplete.

### User interface

- Display active data source and core KPIs.
- Provide four demo questions plus free-form chat input.
- Show business-readable tables and charts.
- Expose the plan and deterministic result in an audit trail.
- Label offline demo mode separately from OpenAI LLM mode.

## Error and boundary states

| State | Expected behavior |
|---|---|
| No upload | Use reproducible synthetic data |
| Missing API key | Run clearly labeled deterministic demo mode |
| Invalid CSV | List missing required fields and stop analysis |
| Different column names | Require a human-reviewed schema mapping before analysis |
| Empty filter result | Explain that no rows match |
| Missing Control or Treatment | Explain that both groups are required |
| Unsupported metric or dimension | Reject it with the allowed values |
| Unsupported business question | Explain the four supported workflows; do not force an unrelated analysis |
| OpenAI API error | Show a concise failure without exposing the API key |

## Non-goals

- Generic exploratory or predictive data-science automation
- Arbitrary code, SQL, or chart generation by the LLM
- Dynamic Power BI report generation
- Production banking-data storage
- Autonomous causal claims, compliance decisions, or rollout approval

## MVP acceptance criteria

- All deterministic unit tests pass.
- The four demo questions route correctly.
- Synthetic ground-truth patterns are recovered.
- A valid uploaded CSV changes KPI and analysis results.
- An invalid CSV produces a friendly contract error.
- LLM explanations match the audit-trail numbers.
- The interpreter does not reference unavailable fields.
- Experiment recommendations remain conditional on integrity and human checks.

## Known limitations

- Sample-ratio mismatch and power/MDE are not yet tested.
- Segment effects are not yet calculated inside the experiment workflow.
- Event-order validity is assumed by the synthetic generator.
- The current UI keeps one displayed response rather than persistent conversation history.
- Market, pricing, and value hypotheses have not been validated with customers.
