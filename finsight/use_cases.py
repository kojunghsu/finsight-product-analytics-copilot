from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class UseCaseSpec:
    key: str
    name: str
    business_question: str
    required_fields: tuple[str, ...]
    optional_fields: tuple[str, ...] = ()


USE_CASES = (
    UseCaseSpec(
        key="acquisition_onboarding",
        name="Acquisition & Onboarding",
        business_question="Where do applicants leave the onboarding journey?",
        required_fields=(
            "customer_id",
            "signed_up",
            "identity_verified",
            "card_activated",
        ),
        optional_fields=("acquisition_channel", "device", "customer_segment"),
    ),
    UseCaseSpec(
        key="activation_early_use",
        name="Activation & Early Use",
        business_question="Do activated cardholders complete a first transaction and remain active?",
        required_fields=(
            "customer_id",
            "card_activated",
            "first_transaction",
            "active_30d",
        ),
        optional_fields=("signup_date", "device", "customer_segment"),
    ),
    UseCaseSpec(
        key="engagement_spend",
        name="Engagement & Spend",
        business_question="How actively are customers using the card and how much do they spend?",
        required_fields=(
            "customer_id",
            "active_30d",
            "transactions_30d",
            "spend_30d",
        ),
        optional_fields=("device", "acquisition_channel", "customer_segment"),
    ),
    UseCaseSpec(
        key="retention_inactivity",
        name="Retention & Inactivity",
        business_question="Are activated cardholders retained at 30 and 90 days?",
        required_fields=(
            "customer_id",
            "card_activated",
            "active_30d",
            "active_90d",
        ),
        optional_fields=("reactivated_90d", "customer_segment", "device"),
    ),
)

EXPERIMENT_FIELDS = (
    "customer_id",
    "experiment_group",
    "card_activated",
    "active_30d",
)

KNOWN_FIELDS = tuple(
    sorted(
        {field for spec in USE_CASES for field in (*spec.required_fields, *spec.optional_fields)}
        | set(EXPERIMENT_FIELDS)
    )
)


def assess_compatibility(df: pd.DataFrame) -> list[dict]:
    """Return deterministic use-case eligibility from confirmed canonical fields."""
    columns = set(df.columns)
    assessments = []
    for spec in USE_CASES:
        found = [field for field in spec.required_fields if field in columns]
        missing = [field for field in spec.required_fields if field not in columns]
        optional_found = [field for field in spec.optional_fields if field in columns]
        if not missing:
            status = "Ready"
        elif "customer_id" in columns and len(found) >= max(2, len(spec.required_fields) // 2):
            status = "Limited"
        else:
            status = "Unavailable"
        assessments.append(
            {
                "key": spec.key,
                "use_case": spec.name,
                "status": status,
                "business_question": spec.business_question,
                "required_found": found,
                "missing_required": missing,
                "optional_found": optional_found,
            }
        )
    return assessments


def experiment_compatibility(df: pd.DataFrame) -> dict:
    columns = set(df.columns)
    missing = [field for field in EXPERIMENT_FIELDS if field not in columns]
    return {
        "capability": "A/B Experiment Evaluation",
        "status": "Ready" if not missing else "Unavailable",
        "missing_required": missing,
    }


def ready_use_cases(df: pd.DataFrame) -> set[str]:
    return {
        assessment["key"]
        for assessment in assess_compatibility(df)
        if assessment["status"] == "Ready"
    }
