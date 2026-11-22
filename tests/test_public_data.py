"""Additional public-release checks; no customer-level source is required."""
from pathlib import Path
import json
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
O = ROOT / "outputs"

def load(name):
    return pd.read_csv(O / name)

def metadata(name):
    return json.loads((O / name).read_text(encoding="utf-8"))

def test_aggregate_revenue_contracts():
    m = metadata("metrics.json")
    m2 = metadata("merchandise_metrics.json")
    assert sum(load("monthly.csv").revenue_gbp) == pytest.approx(m["positive_sales_gbp"],abs=.01)
    assert sum(load("merchandise_abc_summary.csv").positive_sales_gbp) == pytest.approx(m2["merchandise_candidate_gbp"],abs=.01)
    assert sum(load("classification_bridge.csv").positive_sales_gbp) == pytest.approx(m["positive_sales_gbp"],abs=.01)

def test_abc_codes_and_revenue_consistency():
    abc = load("merchandise_candidate_abc.csv")
    group = abc.groupby("abc").agg(product_codes=("product_id", "size"),sales=("revenue_gbp", "sum"))
    summary = load("merchandise_abc_summary.csv").set_index("abc")
    assert len(abc) == 4875
    assert not abc.product_id.astype(str).duplicated().any()
    for k, row in summary.iterrows():
        assert int(group.loc[k, "product_codes"]) == int(row.product_codes)
        assert group.loc[k, "sales"] == pytest.approx(row.positive_sales_gbp, abs=.01)

def test_customer_denominators_are_separate():
    core = metadata("metrics.json")
    repeat = load("merchandise_repeat_summary.csv").iloc[0]
    assert core["identified_customers_with_positive_sale"] == 5878
    assert int(repeat.identified_customers) == 5852
    assert int(repeat.repeat_customers) == 4234
    assert sum(load("rfm_segment_summary.csv").customers) == 5878

def test_affinity_screen_matches_thresholds():
    v = metadata("temporal_validation_metrics.json")
    aff = load("basket_temporal_validation.csv")
    passing = aff.loc[aff.meets_holdout_screen.astype(str).str.lower() == "true"]
    assert len(passing) == v["holdout_screen_pairs"] == 2662
    assert ((passing.train_co_baskets >= 30) & (passing.test_co_baskets >= 20) &
            (passing.train_lift >= 1.5) & (passing.test_lift >= 1.5)).all()
    assert len(load("validated_affinity_shortlist.csv")) == 100

def test_public_distribution_omits_transactions_and_customer_ids():
    forbidden = ["data/source_lines.csv", "outputs/fact_transaction.csv.gz",
                 "outputs/classified_lines.csv.gz", "outputs/customers_rfm.csv",
                 "outputs/customer_action_center.csv", "outputs/product_action_center.csv"]
    for relative in forbidden:
        assert not (ROOT / relative).exists(), relative
