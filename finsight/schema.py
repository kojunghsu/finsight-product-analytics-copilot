import re
from difflib import SequenceMatcher

ALIASES = {
    "customer_id": ["user_id", "client_id", "account_id"],
    "signed_up": ["registered", "signup_completed", "application_started"],
    "identity_verified": ["kyc_completed", "verified", "identity_check_completed"],
    "card_activated": ["card_activation", "activated", "account_opened"],
    "first_transaction": ["first_purchase", "first_payment", "first_txn"],
    "active_30d": ["engaged_30d", "retained_30d", "active_after_30_days"],
    "device": ["device_type", "platform"],
    "acquisition_channel": ["channel", "acquisition_source", "marketing_source"],
    "customer_segment": ["segment", "user_segment", "customer_type"],
    "experiment_group": ["ab_group", "variant", "test_group"],
    "spend_30d": ["spend_30_days", "thirty_day_spend", "amount_30d"],
}


def normalize_column(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.casefold()).strip("_")


def suggest_mapping(target: str, uploaded_columns: list[str]) -> str | None:
    """Return a conservative initial suggestion; a user must always confirm it."""
    candidates = [target, *ALIASES.get(target, [])]
    normalized = {column: normalize_column(column) for column in uploaded_columns}
    for candidate in candidates:
        for column, value in normalized.items():
            if value == candidate:
                return column

    scored = [
        (max(SequenceMatcher(None, value, candidate).ratio() for candidate in candidates), column)
        for column, value in normalized.items()
    ]
    score, column = max(scored, default=(0.0, None))
    return column if score >= 0.82 else None
