"""
因子打分核心模块
每个因子输出 0~100 分
"""
import pandas as pd
import numpy as np
from loguru import logger


def normalize(series: pd.Series, method="rank") -> pd.Series:
    """归一化到 0~100"""
    if method == "rank":
        return series.rank(pct=True) * 100
    elif method == "minmax":
        lo, hi = series.min(), series.max()
        if hi - lo == 0:
            return pd.Series(50, index=series.index)
        return (series - lo) / (hi - lo) * 100
    else:
        raise ValueError(f"unknown method: {method}")


class FactorScorer:
    def __init__(self, config_path="config/factors.yaml"):
        import yaml
        with open(config_path) as f:
            self.cfg = yaml.safe_load(f)

    def score(self, data: dict) -> pd.DataFrame:
        """
        data 包含:
          - daily: 日线 OHLCV
          - money_flow: 资金流
          - rsrs_signal: RSRS 信号
        """
        weights = self.cfg["weights"]

        # 各因子打分
        scores = {}

        # 1. 改进动量
        scores["momentum"] = self._momentum_score(data["daily"])

        # 2. 聪明钱
        scores["smart_money"] = self._smart_money_score(data["money_flow"])

        # 3. RSRS 择时（市场级，决定仓位权重）
        scores["rsrs"] = self._rsrs_score(data.get("rsrs_signal", 0.5))

        # 4. 资金流
        scores["capital_flow"] = self._capital_flow_score(data["money_flow"])

        # 5. 波动率过滤（负向 → 低波动高分）
        scores["volatility"] = self._volatility_score(data["daily"])

        # 加权合成
        composite = pd.Series(0, index=scores["momentum"].index)
        for name, weight in weights.items():
            if name in scores:
                composite += scores[name] * weight

        result = pd.DataFrame({
            "code": composite.index,
            "score": composite.values,
            **{f"{k}_score": v.values for k, v in scores.items()}
        })

        # 分级
        thresholds = self.cfg["thresholds"]
        result["signal"] = pd.cut(
            result["score"],
            bins=[0, thresholds["reduce"], thresholds["watch"],
                  thresholds["buy"], thresholds["strong_buy"], 100],
            labels=["reduce", "watch", "buy", "strong_buy"]
        )

        return result.sort_values("score", ascending=False)

    def _momentum_score(self, daily: pd.DataFrame) -> pd.Series:
        """20日改进动量，跳过最近5天"""
        skip = self.cfg["momentum"]["skip_recent"]
        returns = daily.groupby("code")["close"].pct_change(
            self.cfg["momentum"]["lookback"]
        )
        # 跳过最近N天
        returns = returns.groupby("code").shift(skip)
        return normalize(returns, method="rank")

    def _smart_money_score(self, money_flow) -> pd.Series:
        """聪明钱因子：大单净流入占比"""
        # 简化版：用主力净流入/成交额
        ratio = money_flow["main_net_inflow"] / money_flow["turnover"]
        return normalize(ratio, method="rank")

    def _rsrs_score(self, signal: float) -> pd.Series:
        """RSRS 信号映射到 0~100"""
        # signal: 0~1，0=空仓，1=满仓
        return pd.Series(signal * 100, index=pd.Index([], name="code"))

    def _capital_flow_score(self, money_flow) -> pd.Series:
        """北向+主力连续流入"""
        score = (
            money_flow["northbound_net"] * 0.4 +
            money_flow["main_net_inflow"] * 0.6
        ) / money_flow["turnover"]
        return normalize(score, method="rank")

    def _volatility_score(self, daily: pd.DataFrame) -> pd.Series:
        """低波动 → 高分"""
        vol = daily.groupby("code")["close"].pct_change().rolling(20).std()
        # 反转：波动低分高
        return normalize(-vol, method="rank")
