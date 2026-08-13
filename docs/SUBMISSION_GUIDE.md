# FinSight assignment submission guide

## Assignment track

**LLM Business Application**

FinSight is a detailed business application and local prototype, not an LLM technology deep dive or a generic LLM data-scientist pipeline.

## Deliverables in this repository

| Deliverable | Location |
|---|---|
| Runnable local prototype | `app.py` and `finsight/` |
| Business/productization plan | `docs/BUSINESS_PLAN.md` |
| Product requirements and acceptance criteria | `docs/PRODUCT_SPEC.md` |
| System and data-flow architecture | `docs/ARCHITECTURE.md` |
| Setup and usage instructions | `README.md` |
| Automated validation | `tests/` |
| Synthetic upload test pack | `sample_data/` |

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
5. Ask whether the redesigned onboarding flow improved activation.
6. Expand the audit trail to show that the LLM plan and Python result are separate.
7. Upload `sample_data/00_all_use_cases_alias_mapping.csv`, review the approved alias mappings, and show the mapping metadata in the audit trail.
8. If time allows, upload `sample_data/05_incompatible_transactions.csv` to demonstrate safe refusal without false mappings.

The narrative is **Measure → Diagnose → Experiment → Decide**.

## Validation before submission

```bash
python3 -m pytest
python3 -m ruff check .
```

Expected automated result at the time of submission: **17 tests passed**.

## Scope boundaries to state clearly

- The LLM maps business intent and explains results; Python performs all calculations.
- The prototype evaluates four governed credit-card lifecycle use cases and enables only compatible modules.
- Schema suggestions require human confirmation and do not prove business-semantic equivalence.
- Segment comparisons are descriptive.
- A/B interpretation assumes random assignment; SRM is checked against a prespecified 50/50 allocation, while power/MDE is not yet calculated.
- Pricing, market position, and business value are hypotheses, not validated commercial results.
- FinSight prepares decisions but does not approve product, legal, compliance, or rollout actions.

## Files that must not be submitted

- `.env`
- `.venv/`
- locally generated or user-uploaded CSVs under `data/`
- `__pycache__/`
- `.pytest_cache/`
- `.ruff_cache/`

These paths are excluded by `.gitignore`. The synthetic fixtures under `sample_data/` are intentional assignment assets and should be submitted. The repository contains `.env.example` only, with no API key.
