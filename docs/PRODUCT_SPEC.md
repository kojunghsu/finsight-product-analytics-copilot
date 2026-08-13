# FinSight MVP product specification

## Product statement

FinSight helps credit-card product teams determine which lifecycle questions an uploaded customer-level dataset can answer, then translates natural-language questions into reviewable deterministic analyses.

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
- Compare confirmed fields with each use-case contract before enabling its analysis.
- Show a clear error without a traceback when the contract is invalid.
- Never commit API keys or uploaded data to the repository.

### Schema-mapping metadata contract

After a user confirms renamed fields, the audit trail must expose non-sensitive provenance metadata:

| Field | Purpose |
|---|---|
| `source_type` | Distinguish synthetic data from an uploaded CSV |
| `file_name` | Identify the uploaded file used for the analysis |
| `file_size_bytes` | Support basic provenance checks |
| `rows` | Record the analyzed row count |
| `schema_mapping` | List each confirmed source column and FinSight target field |
| `mapping_review_status` | Distinguish `user_confirmed` from `not_required` |
| `mapping_confirmed_at_utc` | Record when the mapping was accepted in the session |

The metadata must not contain API keys or uploaded row-level records. Mapping is session-scoped in the MVP and is not persisted to a database.

### LLM planner

- Return structured output matching the `AnalysisPlan` contract.
- Select only KPI, funnel, segmentation, engagement/spend, retention/inactivity, or experiment workflows.
- Use only approved metrics, dimensions, and filters.
- For experiments, compare the complete Control and Treatment groups.
- Do not calculate numbers or invent fields.

### Deterministic analytics

- KPI: define and calculate onboarding metrics.
- Funnel: calculate stage counts, overall conversion, step conversion, and drop-off.
- Segmentation: compare activation across device, acquisition channel, or customer segment.
- Experiment: calculate group rates, absolute and relative lift, 95% confidence interval, two-sided p-value, a 30-day engagement guardrail, and sample-ratio mismatch (SRM).
- Engagement & Spend: calculate 30-day active rate, transaction frequency, and average spend.
- Retention & Inactivity: calculate separate 30-day and 90-day activity-window rates among activated cardholders, plus reactivation when available. These are not presented as a monotonic survival-retention curve.

### Dataset compatibility

The UI must show four credit-card use cases—Acquisition & Onboarding, Activation & Early Use, Engagement & Spend, and Retention & Inactivity—plus the cross-cutting experiment capability. Each receives one deterministic status:

- **Ready:** all required canonical fields are present after confirmed mapping.
- **Limited:** some relevant fields are present, but at least one required field is missing.
- **Unavailable:** the dataset does not meet the minimum contract.

Only Ready modules may run their complete analysis. FinSight must explain missing fields instead of forcing an unrelated workflow.

### LLM interpreter

- Lead with the result and cite only supplied numbers.
- Distinguish descriptive analysis from experimental evidence.
- Use human-readable business labels.
- State relevant assumptions and limitations.
- Recommend one bounded next step using only available fields.
- Never authorize a full rollout when experiment-integrity checks are incomplete.

### User interface

- Display active data source and core KPIs.
- Provide lifecycle demo questions plus free-form chat input.
- Show business-readable tables and charts.
- Expose the plan and deterministic result in an audit trail.
- Label offline demo mode separately from OpenAI LLM mode.

## Error and boundary states

| State | Expected behavior |
|---|---|
| No upload | Use reproducible synthetic data |
| Missing API key | Run clearly labeled deterministic demo mode |
| Empty or unreadable CSV | Explain the file error and stop analysis |
| Partially compatible CSV | Show module-level status and allow supported analyses to continue |
| Different column names | Require a human-reviewed schema mapping before analysis |
| Similar but unapproved column name | Do not suggest a mapping; leave it unmapped for human review |
| Empty filter result | Explain that no rows match |
| Missing Control or Treatment | Explain that both groups are required |
| Unsupported metric or dimension | Reject it with the allowed values |
| Unsupported business question | Explain the supported lifecycle use cases; do not force an unrelated analysis |
| OpenAI API error | Show a concise failure without exposing the API key |

## Non-goals

- Generic exploratory or predictive data-science automation
- Arbitrary code, SQL, or chart generation by the LLM
- Dynamic Power BI report generation
- Production banking-data storage
- Autonomous causal claims, compliance decisions, or rollout approval

## MVP acceptance criteria

- All deterministic unit tests pass.
- Lifecycle demo questions route correctly.
- A partial dataset enables only use cases whose minimum contracts are satisfied.
- Every CSV in `sample_data/` produces its documented compatibility status.
- `transaction_id` is never mapped to `transactions_30d`.
- Synthetic ground-truth patterns are recovered.
- A valid uploaded CSV changes KPI and analysis results.
- An invalid CSV produces a friendly contract error.
- LLM explanations match the audit-trail numbers.
- The interpreter does not reference unavailable fields.
- Experiment recommendations remain conditional on integrity and human checks.

## Known limitations

- Power/MDE is not yet calculated.
- SRM assumes a prespecified 50/50 allocation and uses a 1% alert threshold.
- Segment effects are not yet calculated inside the experiment workflow.
- Event-order validity is assumed by the synthetic generator.
- The 30-day and 90-day activity fields are independent measurement windows; reactivation can make the later activity rate higher.
- The current UI keeps one displayed response rather than persistent conversation history.
- Market, pricing, and value hypotheses have not been validated with customers.
