# FinSight

**LLM-powered product analytics copilot for the credit-card customer lifecycle.**

FinSight inspects an uploaded customer-level dataset and determines which of four credit-card product use cases it can support: Acquisition & Onboarding, Activation & Early Use, Engagement & Spend, and Retention & Inactivity. A/B experiment evaluation is an additional cross-cutting capability. Conservative rules suggest schema mappings for human confirmation; the LLM routes business intent and interprets results; deterministic Python owns compatibility checks, calculations, and statistical tests.

This is a local prototype for the **LLM Business Application** assignment track—not a generic data-science automation tool and not an autonomous decision maker.

## Demo story

1. “What should we measure for onboarding?”
2. “Where are customers dropping off?”
3. “Which device has the lowest activation?”
4. “Did the redesigned onboarding flow improve activation?”
5. “How are customers using and spending on the card?”
6. “How do 30-day and 90-day activity compare?”

The synthetic generator intentionally embeds testable patterns: Android and Paid Search start with lower conversion, the treatment improves activation, Android benefits more from the redesign, and 30-day engagement is retained as a guardrail.

## What is included

- Reproducible synthetic dataset generator (30,000 customers by default)
- Schema-aware LLM planner with structured output
- Deterministic KPI, funnel, segmentation, and experiment engines
- Deterministic dataset-compatibility routing across four credit-card use cases
- Engagement/spend and retention/inactivity KPI modules
- Governed A/B workflow with experiment data-quality checks, lift, confidence interval, p-value, guardrail, SRM, approximate Power/MDE context, deterministic decision gates, and directional segment consistency
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

FinSight no longer requires every uploaded CSV to contain one universal schema. Each use case has its own minimum data contract:

| Credit-card use case | Minimum confirmed fields |
|---|---|
| Acquisition & Onboarding | `customer_id`, `signed_up`, `identity_verified`, `card_activated` |
| Activation & Early Use | `customer_id`, `card_activated`, `first_transaction`, `active_30d` |
| Engagement & Spend | `customer_id`, `active_30d`, `transactions_30d`, `spend_30d` |
| Retention & Inactivity | `customer_id`, `card_activated`, `active_30d`, `active_90d` |
| A/B Experiment Evaluation | `customer_id`, `experiment_group`, `card_activated`, `active_30d` |

Optional segmentation fields include `device`, `acquisition_channel`, and `customer_segment`. The compatibility panel labels every module Ready, Limited, or Unavailable and explains missing fields.

If an uploaded file uses different column names, FinSight opens a schema-mapping review. It may preselect conservative alias matches, but a user confirms only the mappings that are semantically valid. Unmapped fields are allowed; they simply keep dependent modules from becoming Ready. FinSight never silently changes KPI definitions.

### Upload and schema-mapping workflow

1. Click **Upload** and select an onboarding CSV.
2. If the file already follows the FinSight data contract, validation runs immediately.
3. If recognized field names differ, review the suggestions in **Schema Mapping Review**.
4. Correct any mapping whose business meaning is not equivalent to the FinSight target field.
5. Map the fields whose business meanings are equivalent and ensure each uploaded column is used only once.
6. Click **Apply selected mappings**.
7. Review **Dataset compatibility** to see which product modules are Ready, Limited, or Unavailable.
8. Verify the sidebar status: **Uploaded CSV active** when at least one complete workflow is Ready, or **CSV loaded — no supported analyses** when the file cannot support any governed workflow.
9. Ask a supported demo or free-form product analytics question.
10. Expand **Audit trail** to review the file metadata, confirmed mappings, analysis plan, and deterministic result.

Example:

| Uploaded column | Confirmed FinSight field |
|---|---|
| `user_id` | `customer_id` |
| `kyc_completed` | `identity_verified` |
| `account_opened` | `card_activated` |
| `first_purchase` | `first_transaction` |
| `engaged_30d` | `active_30d` |

Mapping suggestions use an explicit allowlist of exact normalized aliases—not fuzzy string similarity or unrestricted LLM guessing. For example, `transaction_id` is never treated as the customer-level count `transactions_30d`. Confirmation means the user accepts the business-semantic equivalence; FinSight validates structure but cannot independently prove that two events have the same business definition.

The audit trail records non-sensitive provenance metadata: source type, file name, file size, row count, confirmed source-to-target mappings, review status, and confirmation time. It does not include uploaded row-level customer data.

## Repository guide

- `app.py` — Streamlit experience
- `finsight/copilot.py` — bounded LLM planning, routing, and interpretation
- `finsight/analytics.py` — deterministic calculations and statistics
- `finsight/synthetic.py` — reproducible synthetic banking data
- `finsight/use_cases.py` — use-case data contracts and deterministic compatibility checks
- `sample_data/` — six synthetic upload fixtures covering every use case, full compatibility, and rejection
- `docs/ARCHITECTURE.md` — system contract, boundaries, and production hardening
- `docs/BUSINESS_PLAN.md` — users, value proposition, landscape, pricing, GTM, risks, roadmap
- `docs/PRODUCT_SPEC.md` — workflows, requirements, error states, non-goals, acceptance criteria
- `docs/SUBMISSION_GUIDE.md` — deliverables, demo sequence, validation, and submission safety
- `docs/presentation/` — PDF presentation for the assignment/demo
- `tests/` — analytical ground-truth and routing tests

## Upload test pack

The repository includes one synthetic CSV for each lifecycle use case, one fully compatible alias-mapping CSV, and one deliberately incompatible transaction-level CSV. See [`sample_data/README.md`](sample_data/README.md) for expected statuses and questions. These fixtures are safe to submit because they are fabricated and contain no real customer records.

## Scope and limitations

FinSight does not accept arbitrary banking datasets. It supports the four documented customer-level credit-card use cases and refuses analyses whose required fields are unavailable. It does not perform predictive modeling, causal inference beyond the randomized A/B workflow, arbitrary exploratory analysis, dynamic Power BI generation, or automated rollout. The current data is synthetic, the market and pricing sections are hypotheses, and real banking use would require security, privacy, governance, compliance, and extensive evaluation.

## Portfolio framing

FinSight demonstrates product KPI design, funnel and customer analysis, controlled experimentation, statistical communication, requirements translation, and an auditable LLM-to-analytics architecture. It contains no personal resume or contact information.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Business plan](docs/BUSINESS_PLAN.md)
- [Product specification](docs/PRODUCT_SPEC.md)
- [Assignment submission guide](docs/SUBMISSION_GUIDE.md)
- [Product overview slides (PDF)](docs/presentation/FinSight_Product_Overview.pdf)

## License

MIT
