# FinSight

**LLM-powered product analytics copilot for digital-banking onboarding.**

FinSight turns natural-language product questions into four governed workflows: KPI definition, onboarding funnel analysis, customer segmentation, and A/B experiment evaluation. The LLM maps business intent and interprets results; deterministic Python owns every calculation and statistical test.

This is a local prototype for the **LLM Business Application** assignment track—not a generic data-science automation tool and not an autonomous decision maker.

## Demo story

1. “What should we measure for onboarding?”
2. “Where are customers dropping off?”
3. “Which device has the lowest activation?”
4. “Did the redesigned onboarding flow improve activation?”

The synthetic generator intentionally embeds testable patterns: Android and Paid Search start with lower conversion, the treatment improves activation, Android benefits more from the redesign, and 30-day engagement is retained as a guardrail.

## What is included

- Reproducible synthetic dataset generator (30,000 customers by default)
- Schema-aware LLM planner with structured output
- Deterministic KPI, funnel, segmentation, and experiment engines
- Two-proportion A/B test with lift, confidence interval, p-value, guardrail, and SRM check
- Streamlit chat UI with upload, charts, and an auditable plan/result trace
- Offline deterministic demo mode when no API key is present
- Tests plus architecture and productization documentation

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e '.[dev]'
cp .env.example .env
python3 -m streamlit run app.py
```

To enable real LLM planning and interpretation, add `OPENAI_API_KEY` to `.env`. The default model can be changed with `OPENAI_MODEL`. Without a key, the complete UI and analytics engine run in clearly labeled deterministic demo mode.

Generate a CSV explicitly:

```bash
python3 scripts/generate_data.py --rows 30000 --output data/onboarding.csv
```

Run validation:

```bash
python3 -m pytest
python3 -m ruff check .
```

## Data contract

Uploaded CSVs must contain `customer_id`, `device`, `acquisition_channel`, `customer_segment`, `experiment_group`, `spend_30d`, and the sequential binary event columns `signed_up`, `identity_verified`, `card_activated`, `first_transaction`, and `active_30d`. The bundled demo additionally includes optional `signup_date` and `transactions_30d` fields.

If an uploaded file uses different column names, FinSight opens a schema-mapping review. It may preselect conservative alias matches, but a user must confirm every required mapping before Python validates or analyzes the data. FinSight never silently changes KPI definitions.

### Upload and schema-mapping workflow

1. Click **Upload** and select an onboarding CSV.
2. If the file already follows the FinSight data contract, validation runs immediately.
3. If required column names differ, review every suggestion in **Schema Mapping Review**.
4. Correct any mapping whose business meaning is not equivalent to the FinSight target field.
5. Map every required field and ensure that each uploaded column is used only once.
6. Click **Apply confirmed mapping**.
7. Verify **Uploaded CSV active** and the number of confirmed mappings in the sidebar.
8. Ask a demo or free-form product analytics question.
9. Expand **Audit trail** to review the file metadata, confirmed mappings, analysis plan, and deterministic result.

Example:

| Uploaded column | Confirmed FinSight field |
|---|---|
| `user_id` | `customer_id` |
| `kyc_completed` | `identity_verified` |
| `account_opened` | `card_activated` |
| `first_purchase` | `first_transaction` |
| `engaged_30d` | `active_30d` |

Current mapping suggestions use conservative alias rules and string similarity, not unrestricted LLM guessing. Confirmation means that the user accepts the business-semantic equivalence; FinSight validates structure but cannot independently prove that two events have the same business definition.

The audit trail records non-sensitive provenance metadata: source type, file name, file size, row count, confirmed source-to-target mappings, review status, and confirmation time. It does not include uploaded row-level customer data.

## Repository guide

- `app.py` — Streamlit experience
- `finsight/copilot.py` — bounded LLM planning, routing, and interpretation
- `finsight/analytics.py` — deterministic calculations and statistics
- `finsight/synthetic.py` — reproducible synthetic banking data
- `docs/ARCHITECTURE.md` — system contract, boundaries, and production hardening
- `docs/BUSINESS_PLAN.md` — users, value proposition, landscape, pricing, GTM, risks, roadmap
- `docs/PRODUCT_SPEC.md` — workflows, requirements, error states, non-goals, acceptance criteria
- `docs/SUBMISSION_GUIDE.md` — deliverables, demo sequence, validation, and submission safety
- `tests/` — analytical ground-truth and routing tests

## Scope and limitations

FinSight does not perform predictive modeling, causal inference beyond the randomized A/B workflow, arbitrary exploratory analysis, dynamic Power BI generation, or automated rollout. The current data is synthetic, the market and pricing sections are hypotheses, and real banking use would require security, privacy, governance, compliance, and extensive evaluation.

## Portfolio framing

FinSight demonstrates product KPI design, funnel and customer analysis, controlled experimentation, statistical communication, requirements translation, and an auditable LLM-to-analytics architecture. It contains no personal resume or contact information.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Business plan](docs/BUSINESS_PLAN.md)
- [Product specification](docs/PRODUCT_SPEC.md)
- [Assignment submission guide](docs/SUBMISSION_GUIDE.md)

## License

MIT
