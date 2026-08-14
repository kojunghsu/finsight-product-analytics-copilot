# FinSight demo and evaluation guide

## Product positioning

FinSight is a focused LLM business application and local product prototype, not a generic data-scientist automation pipeline.

## Recommended review order

1. Read [`BUSINESS_PLAN.md`](BUSINESS_PLAN.md) for the product strategy and commercial rationale.
2. Review the [`FinSight product overview PDF`](presentation/FinSight_Product_Overview.pdf) for the concise presentation narrative.
3. Follow the local setup below and run the prototype as implementation evidence.
4. Consult [`PRODUCT_SPEC.md`](PRODUCT_SPEC.md) and [`ARCHITECTURE.md`](ARCHITECTURE.md) for detailed product and system decisions.

The prototype, tests, sample data, and technical documentation provide implementation evidence for the business/productization plan.

## Product materials in this repository

| Deliverable | Location |
|---|---|
| **Business/productization plan** | **`docs/BUSINESS_PLAN.md`** |
| Runnable local prototype | `app.py` and `finsight/` |
| Product requirements and acceptance criteria | `docs/PRODUCT_SPEC.md` |
| System and data-flow architecture | `docs/ARCHITECTURE.md` |
| Setup and usage instructions | `README.md` |
| Automated validation | `tests/` |
| Synthetic upload test pack | `sample_data/` |
| Presentation PDF | `docs/presentation/FinSight_Product_Overview.pdf` |

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e '.[dev]'
cp .env.example .env
python3 -m streamlit run app.py
```

Add an OpenAI API key to the local `.env` file to enable LLM planning and interpretation. Never submit or commit the populated `.env` file.

## Suggested five-minute demonstration

1. Show the synthetic-data KPIs and explain that no real customer records are bundled.
2. Ask, “What should we measure for onboarding?”
3. Ask, “Where are customers dropping off?”
4. Ask which device or acquisition channel has the lowest activation.
5. Ask whether the redesigned onboarding flow improved activation, then show lift, confidence interval, p-value, guardrail, SRM, MDE, and the human-reviewed decision gate.
6. Briefly show the engagement/spend and 30-day-versus-90-day retention questions so all four lifecycle use cases are visible.
7. Expand the audit trail to show that the LLM plan and Python result are separate.
8. Upload `sample_data/00_all_use_cases_alias_mapping.csv`, review the approved alias mappings, and show the mapping metadata in the audit trail.
9. If time allows, upload `sample_data/05_incompatible_transactions.csv` to demonstrate safe refusal without false mappings or fabricated KPIs.

The narrative is **Measure → Diagnose → Experiment → Decide**.

## Validation

```bash
python3 -m pytest
python3 -m ruff check .
```

Current expected automated result: **25 tests passed**.

## Scope boundaries to state clearly

- The LLM maps business intent and explains results; Python performs all calculations.
- The prototype evaluates four governed credit-card lifecycle use cases and enables only compatible modules.
- Schema suggestions require human confirmation and do not prove business-semantic equivalence.
- Segment comparisons are descriptive.
- A/B interpretation assumes random assignment; SRM is checked against a prespecified 50/50 allocation. FinSight reports an approximate 80%-power MDE as a planning diagnostic, but it does not replace prospective power analysis.
- Pricing, market position, and business value are hypotheses, not validated commercial results.
- FinSight prepares decisions but does not approve product, legal, compliance, or rollout actions.

## Files that must not be committed

- `.env`
- `.venv/`
- locally generated or user-uploaded CSVs under `data/`
- `__pycache__/`
- `.pytest_cache/`
- `.ruff_cache/`

These paths are excluded by `.gitignore`. The synthetic fixtures under `sample_data/` are intentional product-demo assets and remain in the repository. The repository contains `.env.example` only, with no API key.
