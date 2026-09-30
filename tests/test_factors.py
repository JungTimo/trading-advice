import pandas as pd
import numpy as np
from strategy.factor_score import FactorScorer


def test_normalize():
    s = pd.Series([1, 2, 3, 4, 5])
    result = FactorScorer.normalize(s)
    assert result.min() >= 0
    assert result.max() <= 100


def test_score_output():
    scorer = FactorScorer()
    # 构造假数据
    dates = pd.date_range("2023-01-01", periods=30)
    codes = ["000001", "600519"]
    data = {
        "daily": pd.DataFrame({
            "code": np.repeat(codes, 30),
            "date": dates.tolist() * 2,
            "close": np.random.randn(60).cumsum() + 100
        }),
        "money_flow": pd.DataFrame({
            "code": np.repeat(codes, 30),
            "date": dates.tolist() * 2,
            "main_net_inflow": np.random.randn(60) * 1e6,
            "northbound_net": np.random.randn(60) * 1e6,
            "turnover": np.random.rand(60) * 1e8
        }),
        "rsrs_signal": 0.7
    }
    result = scorer.score(data)
    assert "score" in result.columns
    assert len(result) == 2
