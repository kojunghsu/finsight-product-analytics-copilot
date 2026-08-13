import re

ALIASES = {
    "customer_id": ["user_id", "client_id", "account_id"],
    "signed_up": ["registered", "signup_completed", "application_started"],
    "identity_verified": ["kyc_completed", "verified", "identity_check_completed"],
    "card_activated": ["card_activation", "activated", "account_opened"],
    "first_transaction": ["first_purchase", "first_payment", "first_txn"],
    "active_30d": ["engaged_30d", "active_at_30_days", "active_after_30_days"],
    "active_90d": ["engaged_90d", "active_at_90_days", "active_after_90_days"],
    "reactivated_90d": ["reactivated", "winback_90d", "resumed_usage_90d"],
    "device": ["device_type", "platform"],
    "acquisition_channel": ["channel", "acquisition_source", "marketing_source"],
    "customer_segment": ["segment", "user_segment", "customer_type"],
    "experiment_group": ["ab_group", "variant", "test_group"],
    "spend_30d": ["spend_30_days", "thirty_day_spend", "amount_30d"],
    "transactions_30d": ["transaction_count_30d", "txns_30d", "purchases_30d"],
}


def normalize_column(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.casefold()).strip("_")


def suggest_mapping(target: str, uploaded_columns: list[str]) -> str | None:
    """Return only an explicitly allowlisted alias; a user must always confirm it."""
    candidates = [target, *ALIASES.get(target, [])]
    normalized = {column: normalize_column(column) for column in uploaded_columns}
    for candidate in candidates:
        for column, value in normalized.items():
            if value == candidate:
                return column
    return None


def suggested_mappings(
    uploaded_columns: list[str], known_fields: tuple[str, ...]
) -> dict[str, str]:
    """Return only useful alias suggestions for fields absent from the upload."""
    canonical = set(known_fields)
    candidates = [column for column in uploaded_columns if column not in canonical]
    suggestions = {}
    for target in sorted(canonical - set(uploaded_columns)):
        if source := suggest_mapping(target, candidates):
            suggestions[target] = source
    return suggestions
