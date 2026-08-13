import pytest

from finsight.analytics import experiment_analysis, funnel_analysis, segment_analysis
from finsight.synthetic import generate_onboarding_data


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


def test_missing_columns_fail_clearly(data):
    with pytest.raises(ValueError, match="Missing required columns"):
        funnel_analysis(data.drop(columns=["card_activated"]))
