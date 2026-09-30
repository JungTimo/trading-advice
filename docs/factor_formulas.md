# 因子公式

## 1. 改进动量
momentum_20 = close[t-5] / close[t-25] - 1
跳过最近5天避免除权假信号

## 2. 聪明钱因子
smart_money = Σ(大单净流入) / Σ(成交额)  over 10 days
## 3. RSRS
RSRS = slope of (high, low) regression over 18 days
阈值 → 看多
## 4. 资金流
capital_flow = (northbound_net * 0.4 + main_net * 0.6) / turnover
## 5. 波动率过滤
vol_20 = std(returns, 20)
score = -vol_20 (低波动高分)
