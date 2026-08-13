from typing import Any


def build_data_context(
    *,
    source_type: str,
    rows: int,
    file_name: str | None = None,
    file_size_bytes: int | None = None,
    mapping: dict[str, str] | None = None,
    confirmed_at_utc: str | None = None,
) -> dict[str, Any]:
    """Build non-sensitive provenance metadata for the visible audit trail."""
    confirmed_mapping = mapping or {}
    return {
        "source_type": source_type,
        "file_name": file_name,
        "file_size_bytes": file_size_bytes,
        "rows": rows,
        "schema_mapping": [
            {"source_column": source, "target_field": target}
            for target, source in sorted(confirmed_mapping.items())
        ],
        "mapping_review_status": "user_confirmed" if confirmed_mapping else "not_required",
        "mapping_confirmed_at_utc": confirmed_at_utc,
    }
