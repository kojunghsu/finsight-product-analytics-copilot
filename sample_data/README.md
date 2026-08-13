# FinSight upload test data

Upload one CSV at a time. The files are synthetic and contain no real customer records.

`FinSight_Test_Data_Catalog.xlsx` provides the same test matrix in a formatted workbook for presentation or manual review. Upload the CSV files—not the workbook—to the Streamlit app.

| File | Purpose | Expected Ready module |
|---|---|---|
| `00_all_use_cases_alias_mapping.csv` | Full lifecycle plus schema-mapping review; 400 customers with a balanced 200/200 A/B split | All four lifecycle modules and A/B Experiment Evaluation |
| `01_acquisition_onboarding.csv` | Application and onboarding funnel | Acquisition & Onboarding |
| `02_activation_early_use.csv` | Card activation through early engagement | Activation & Early Use |
| `03_engagement_spend.csv` | Usage frequency and spend | Engagement & Spend |
| `04_retention_inactivity.csv` | 30/90-day activity and reactivation | Retention & Inactivity |
| `05_incompatible_transactions.csv` | Unsupported transaction-level file | None; all modules must remain Unavailable |

## Mapping safety check

The full-lifecycle file intentionally uses approved aliases such as `user_id`, `kyc_completed`, and `account_opened`. Review and confirm those suggestions. The incompatible file contains `transaction_id`; it must **not** be suggested as `transactions_30d` because an identifier is not a customer-level transaction count.

## Suggested questions

1. Acquisition: `Where are customers dropping off?`
2. Early use: `What should we measure for onboarding?`
3. Engagement: `How are customers using and spending on the card?`
4. Retention/inactivity: `How do 30-day and 90-day activity compare?`
5. Full lifecycle: `Did the redesigned onboarding flow improve activation?`
6. Incompatible file: `What is our activation rate?` — FinSight must refuse and explain the missing fields.
