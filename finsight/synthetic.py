from pathlib import Path

import numpy as np
import pandas as pd


def generate_onboarding_data(n: int = 30_000, seed: int = 42) -> pd.DataFrame:
    """Create reproducible, non-random business patterns for prototype evaluation."""
    rng = np.random.default_rng(seed)
    device = rng.choice(["iOS", "Android", "Web"], n, p=[0.38, 0.42, 0.20])
    channel = rng.choice(["Organic", "Referral", "Paid Search"], n, p=[0.44, 0.25, 0.31])
    segment = rng.choice(["Young Professional", "Family", "Student"], n, p=[0.45, 0.35, 0.20])
    group = rng.choice(["Control", "Treatment"], n)
    signup_date = pd.Timestamp("2026-01-01") + pd.to_timedelta(rng.integers(0, 120, n), unit="D")

    verification_p = (
        0.86
        - 0.07 * (device == "Android")
        - 0.05 * (channel == "Paid Search")
        + 0.02 * (group == "Treatment")
    )
    verified = rng.random(n) < verification_p
    activation_p = (
        0.76
        - 0.08 * (device == "Android")
        - 0.05 * (channel == "Paid Search")
        + 0.035 * (group == "Treatment")
        + 0.025 * ((group == "Treatment") & (device == "Android"))
    )
    activated = verified & (rng.random(n) < activation_p)
    transacted = activated & (rng.random(n) < (0.84 + 0.015 * (group == "Treatment")))
    engaged = transacted & (rng.random(n) < (0.72 + 0.01 * (segment == "Young Professional")))
    retained_90d = engaged & (rng.random(n) < (0.78 + 0.03 * (segment == "Young Professional")))
    reactivated_90d = transacted & ~engaged & (rng.random(n) < 0.18)
    active_90d = retained_90d | reactivated_90d
    transactions = np.where(engaged, rng.poisson(5.2, n) + 1, 0)
    spend = np.where(engaged, rng.gamma(2.2, 58, n), 0).round(2)

    return pd.DataFrame(
        {
            "customer_id": [f"C{i:06d}" for i in range(1, n + 1)],
            "signup_date": signup_date,
            "device": device,
            "acquisition_channel": channel,
            "customer_segment": segment,
            "experiment_group": group,
            "signed_up": 1,
            "identity_verified": verified.astype(int),
            "card_activated": activated.astype(int),
            "first_transaction": transacted.astype(int),
            "active_30d": engaged.astype(int),
            "active_90d": active_90d.astype(int),
            "reactivated_90d": reactivated_90d.astype(int),
            "transactions_30d": transactions,
            "spend_30d": spend,
        }
    )


def save_dataset(path: str | Path = "data/onboarding.csv", n: int = 30_000, seed: int = 42) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    generate_onboarding_data(n=n, seed=seed).to_csv(output, index=False)
    return output
