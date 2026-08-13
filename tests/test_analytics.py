import pytest

from finsight.analytics import (
    _sample_ratio_mismatch,
    engagement_analysis,
    experiment_analysis,
    funnel_analysis,
    retention_analysis,
    segment_analysis,
)
from finsight.audit import build_data_context
from finsight.schema import suggest_mapping
from finsight.synthetic import generate_onboarding_data
from finsight.use_cases import assess_compatibility, experiment_compatibility


@pytest.fixture(scope="module")
def data():
    return generate_onboarding_data(30_000, seed=42)


def test_funnel_is_monotonic(data):
    counts = [row["customers"] for row in funnel_analysis(data).table]
    assert counts == sorted(counts, reverse=True)


def test_android_has_lower_activation_than_ios(data):
    rows = {row["device"]: row["rate"] for row in segment_analysis(data, dimension="device").table}
    assert rows["Android"] < rows["iOS"]


def test_treatment_improves_activation(data):
    result = experiment_analysis(data)
    assert result.summary["absolute_lift"] > 0.025
    assert result.summary["p_value"] < 0.05
    assert result.summary["srm_detected"] is False


def test_sample_ratio_mismatch_flags_large_allocation_error():
    result = _sample_ratio_mismatch(control_n=700, treatment_n=300)
    assert result["srm_detected"] is True
    assert result["srm_p_value"] < 0.01


def test_missing_columns_fail_clearly(data):
    incomplete = data.drop(
        columns=["identity_verified", "card_activated", "first_transaction", "active_30d"]
    )
    with pytest.raises(ValueError, match="Missing required columns"):
        experiment_analysis(incomplete)


def test_partial_dataset_enables_only_compatible_use_cases(data):
    partial = data[["customer_id", "card_activated", "active_30d", "transactions_30d", "spend_30d"]]
    statuses = {item["key"]: item["status"] for item in assess_compatibility(partial)}
    assert statuses["engagement_spend"] == "Ready"
    assert statuses["acquisition_onboarding"] != "Ready"
    assert statuses["retention_inactivity"] != "Ready"
    assert experiment_compatibility(partial)["status"] == "Unavailable"


def test_engagement_and_retention_modules_run_on_synthetic_data(data):
    engagement = engagement_analysis(data)
    retention = retention_analysis(data)
    assert engagement.summary["active_customers"] > 0
    assert retention.summary["retention_rate_30d"] > retention.summary["retention_rate_90d"]


def test_schema_mapping_suggests_known_aliases_only():
    columns = ["user_id", "kyc_completed", "first_purchase", "unrelated_notes"]
    assert suggest_mapping("customer_id", columns) == "user_id"
    assert suggest_mapping("identity_verified", columns) == "kyc_completed"
    assert suggest_mapping("first_transaction", columns) == "first_purchase"
    assert suggest_mapping("spend_30d", columns) is None


def test_mapping_metadata_is_auditable_without_row_data():
    context = build_data_context(
        source_type="uploaded_csv",
        file_name="example.csv",
        file_size_bytes=1234,
        rows=5000,
        mapping={"customer_id": "user_id", "identity_verified": "kyc_completed"},
        confirmed_at_utc="2026-08-13T01:00:00+00:00",
    )
    assert context["mapping_review_status"] == "user_confirmed"
    assert context["rows"] == 5000
    assert {item["source_column"] for item in context["schema_mapping"]} == {
        "user_id",
        "kyc_completed",
    }
    assert "data" not in context
