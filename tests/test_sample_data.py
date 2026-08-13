from pathlib import Path

import pandas as pd
import pytest

from finsight.analytics import experiment_analysis
from finsight.schema import suggest_mapping
from finsight.use_cases import KNOWN_FIELDS, assess_compatibility, experiment_compatibility

SAMPLE_DIR = Path(__file__).parents[1] / "sample_data"


def normalize_approved_aliases(df: pd.DataFrame) -> pd.DataFrame:
    mapping = {}
    for target in KNOWN_FIELDS:
        if target not in df.columns:
            source = suggest_mapping(target, list(df.columns))
            if source and source not in mapping.values():
                mapping[target] = source
    return df.rename(columns={source: target for target, source in mapping.items()})


@pytest.mark.parametrize(
    ("filename", "ready_module"),
    [
        ("01_acquisition_onboarding.csv", "acquisition_onboarding"),
        ("02_activation_early_use.csv", "activation_early_use"),
        ("03_engagement_spend.csv", "engagement_spend"),
        ("04_retention_inactivity.csv", "retention_inactivity"),
    ],
)
def test_each_use_case_sample_enables_its_intended_module(filename, ready_module):
    df = pd.read_csv(SAMPLE_DIR / filename)
    statuses = {item["key"]: item["status"] for item in assess_compatibility(df)}
    assert statuses[ready_module] == "Ready"


def test_all_use_cases_alias_sample_maps_to_every_module():
    df = normalize_approved_aliases(pd.read_csv(SAMPLE_DIR / "00_all_use_cases_alias_mapping.csv"))
    assert all(item["status"] == "Ready" for item in assess_compatibility(df))
    assert experiment_compatibility(df)["status"] == "Ready"


def test_all_use_cases_sample_has_balanced_and_coherent_experiment():
    df = normalize_approved_aliases(pd.read_csv(SAMPLE_DIR / "00_all_use_cases_alias_mapping.csv"))
    result = experiment_analysis(df)
    groups = {row["group"]: row for row in result.table}
    assert groups["Control"]["customers"] == 200
    assert groups["Treatment"]["customers"] == 200
    assert result.summary["srm_detected"] is False
    assert result.summary["absolute_lift"] == pytest.approx(0.10)
    assert result.summary["significant"] is True
    assert result.summary["ci_95_low"] > 0
    assert result.summary["decision_status"] == "Candidate for phased rollout"
    assert result.summary["approximate_mde_80"] > 0
    assert len(result.summary["segment_diagnostics"]) == 10


def test_incompatible_sample_stays_unavailable_and_has_no_false_transaction_mapping():
    df = pd.read_csv(SAMPLE_DIR / "05_incompatible_transactions.csv")
    assert suggest_mapping("transactions_30d", list(df.columns)) is None
    assert all(item["status"] == "Unavailable" for item in assess_compatibility(df))
    assert experiment_compatibility(df)["status"] == "Unavailable"
