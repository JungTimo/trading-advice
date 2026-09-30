# trading-advice
下面这份内容**可以直接贴进你仓库的 `README.md`**。我已经按“项目清单 + 使用方式 + A 股选股建议流水线”组织好，避免闲聊、避免临时口吻。

---

# A 股选股建议：开源项目调研与使用方案

本项目目标：用开源工具搭建一套 **A 股选股 / 信号生成 / 回测验证 / LLM 解读** 系统。  
定位是**研究辅助与策略验证**，不是自动交易，也不构成投资建议。

---

## 1. 调研项目清单

| 项目 | 类型 | 介绍 | 亮点 | 成绩 / 现状 | 链接 |
|---|---|---|---|---|---|
| **AkShare** | 数据层 | 免费金融数据接口库，覆盖 A 股日/周/分钟 K 线、前/后复权、财报、资金流、龙虎榜、北向资金、ETF、基金、宏观数据 | 免费、无需复杂授权；适合做本地数据底座；社区维护活跃 | A 股量化项目最常用的免费数据源之一 | https://github.com/akfamily/akshare |
| **RQAlpha** | 回测框架 | 米筐科技开源的 A 股量化回测框架，事件驱动，支持日线/分钟线 | 原生适配 A 股：T+1、涨跌停、复权、佣金印花税可配置；Mod 机制可扩展数据源和撮合逻辑 | 6k+ stars，A 股回测“开箱即报规则”的成熟方案 | https://github.com/ricequant/rqalpha |
| **Backtrader** | 回测框架 | Python 事件驱动回测引擎，通用但默认按美股假设 | 灵活、生态大；但 **T+1、涨跌停、A 股手数、印花税要自己改** | 海外量化入门项目多；A 股要用必须加规则层 | https://github.com/mementum/backtrader |
| **magic-alt/stock** | A 股量化平台 | 面向 A 股的回测 + 策略准入 + 仿真交易 + Web 控制台 + 实盘网关适配 | A 股日历、T+1、涨跌停、手数、停牌、复权内建；有策略准入门禁、基线注册、牛熊/高波动样本外验证；支持 QMT/XTP/UFT/东财网关适配 | V5.x 活跃维护，适合做“研究 → 仿真 → 实盘预检”平台 | https://github.com/magic-alt/stock |
| **QuantsPlaybook** | 研报复现 | 用 Python 复现国内券商金工研报：RSRS、QRS、HHT、聪明钱因子、筹码分布、扩散指标、行业轮动等 | 每个策略带研报 PDF + notebook + 回测；适合把卖方逻辑变成可验证信号 | 100+ 券商/学院派策略，A 股因子与择时研究宝库 | https://github.com/hugo2046/QuantsPlaybook |
| **daily_stock_analysis** | LLM 投研 | LLM 驱动的股票分析系统，A/港/美/ETF 都支持；拉行情+新闻+资金+技术面，输出买入/观望/卖出、买卖点、风险清单 | AkShare/Tushare/Pytdx/Baostock 多源兜底；GitHub Actions 零成本跑；飞书/企微/邮件推送；有历史建议准确率回测 | 社区热度很高，适合做“人话解读层”，不适合单独当交易决策源 | https://github.com/ZhuLinsen/daily_stock_analysis |

---

## 2. 各项目详细说明

### 2.1 AkShare
- **角色**：数据底座
- **能做什么**
  - 拉 A 股历史行情、实时行情、复权行情
  - 拉北向资金、主力资金、龙虎榜、限售解禁、财报、盈利预测
  - 拉指数、行业、ETF、可转债、宏观数据
- **缺点**
  - 免费接口有频率限制
  - 不同接口字段口径不一致，要做一层清洗
- **在本项目里怎么用**
  - 每天/每周更新股票池
  - 给 RQAlpha / Backtrader / 自写回测提供 OHLCV 与基本面数据
  - 给 daily_stock_analysis 类系统补充行情与资金流

---

### 2.2 RQAlpha
- **角色**：A 股规则正确的回测引擎
- **为什么适合 A 股**
  - T+1：当天买不能当天卖
  - 涨跌停：涨停买不进、跌停卖不出可按框架逻辑处理
  - 复权：前复权/后复权/分红送股处理较完整
  - 费用：佣金、印花税、过户费、滑点可配
- **适合场景**
  - 均线 / 双均线 / 动量 / 反转 / 因子选股 / 行业轮动回测
  - 需要“回测结果可信”的策略验证
- **使用方式**
  ```bash
  pip install rqalpha
  rqalpha download-bundle
  rqalpha run -f strategy/ma_crossover.py -s 2020-01-01 -e 2025-12-31 -p 1000000 --plot
  ```
- **注意**
  - 官方 bundle 最省事
  - 用 AkShare/Tushare 时要自己写数据适配 Mod
  - 回测好 ≠ 实盘好

---

### 2.3 Backtrader
- **角色**：高自由度回测引擎
- **A 股坑点**
  - 默认不是 T+1
  - 默认不处理涨跌停
  - 默认不处理 A 股 100 股一手、科创板 200 股、ETF 100 份
  - 默认不扣 A 股卖出印花税 0.1%
- **必须自己加的规则层**
  - `can_trade_today`：今天买入仓位明天才能卖
  - `limit_up/limit_down`：涨停拒绝市价买入，跌停拒绝市价卖出
  - `lot_size`：下单手数取整
  - `commission + stamp_tax + transfer_fee`
  - `no_lookahead`：财务/公告/龙虎榜按披露日之后才可用
- **适合场景**
  - 你已经知道 A 股规则，想自己控制撮合与信号
  - 做多标的批量回测、因子横截面对比
- **不建议**
  - 新手直接拿默认 Backtrader 跑 A 股策略

---

### 2.4 magic-alt/stock
- **角色**：A 股原生量化研究平台
- **核心能力**
  - 回测框架：MACD / EMA / 网格参数搜索 / NAV 组合
  - 策略准入门禁：不是“回测漂亮”就过关
  - 样本外机制：bull / bear / range / high-vol 多市场状态验证
  - 仿真交易与实盘预检
  - FastAPI + Vue 控制台
  - QMT / XTQuant / XTP / 恒生 UFT / 东财 网关适配
- **为什么值得用**
  - 比通用框架更懂 A 股
  - 比单纯 notebook 更接近生产系统
  - 适合做“策略从研究到仿真”的流水线
- **最小运行**
  ```bash
  git clone https://github.com/magic-alt/stock.git
  cd stock
  pip install -r requirements.txt
  python examples/one_click_demo.py --out-dir report/open_source_demo
  python unified_backtest_framework.py run --strategy macd --symbols 600519.SH --start 2023-01-01 --end 2024-12-31 --plot
  ```
- **适合本项目的角色**
  - 主回测 / 仿真 / 策略准入
  - 后续接 QMT 做模拟盘

---

### 2.5 QuantsPlaybook
- **角色**：策略灵感与因子/择时研报复现
- **覆盖内容**
  - 择时：RSRS、QRS、扩散指标、HHT、北向资金、波动率择时
  - 因子：聪明钱、筹码分布、特质波动率、上下影线、动量改进
  - 价值：Piotroski F-Score、现金流模型
  - 组合：行业轮动、指数增强、多任务学习、DE 优化
- **使用方式**
  - 不要直接信研报结论
  - 跑 notebook → 看信号 → 改成日频选股分数 → 送进 RQAlpha / magic-alt 回测
- **示例路径**
  ```text
  QuantsPlaybook/
    C-择时类/RSRS择时指标/py/RSRS.ipynb
    B-因子构建类/聪明钱因子模型/
    A-量化价值类/Piotroski F-Score/
  ```
- **本项目用法**
  - 作为“因子库 / 信号库”
  - 每个研报策略输出一个 0~100 分数或多空信号
  - 再进入组合层

---

### 2.6 daily_stock_analysis
- **角色**：LLM 解读层 / 盘后投研日报
- **能做什么**
  - 输入自选股：600519,300750,000001
  - 拉行情、均线、筹码、资金流、新闻、公告
  - LLM 输出：
    - 核心结论
    - 买入 / 观望 / 卖出
    - 买入价、止损价、目标价
    - 风险点、催化因素、检查清单
  - 推送到企微 / 飞书 / Telegram / 邮件
  - 记录历史建议，做“AI 建议 vs 实际涨跌”回测
- **模型**
  - Gemini / DeepSeek / OpenAI 兼容 / Claude / 通义千问 / Ollama
- **最小部署**
  ```bash
  git clone https://github.com/ZhuLinsen/daily_stock_analysis.git
  cd daily_stock_analysis
  cp .env.example .env
  # 配置 STOCK_LIST、LLM KEY、推送 webhook
  docker compose up -d webui
  ```
- **重要边界**
  - LLM 输出是“解释与摘要”，不是交易依据
  - 真正买卖信号必须由回测引擎产生
  - 可用来：把量化信号翻成人话、做复盘、做风控提醒

---

## 3. 推荐架构：用这些项目搭 A 股选股建议系统

```text
┌────────────────────────┐
│ AkShare / Tushare      │  数据层
│ 行情 / 财务 / 资金流    │
└──────────┬─────────────┘
           │
┌──────────▼─────────────┐
│ QuantsPlaybook         │  因子 / 择时 / 研报复现
│ RSRS / 聪明钱 / 动量    │  输出原始分数
└──────────┬─────────────┘
           │
┌──────────▼─────────────┐
│ RQAlpha / magic-alt    │  回测 & 规则层
│ T+1 / 涨跌停 / 费用     │  输出可交易信号
└──────────┬─────────────┘
           │
┌──────────▼─────────────┐
│ 组合层                  │
│ 打分排序 / 仓位 / 风控   │  输出股票池 + 建议
└──────────┬─────────────┘
           │
┌──────────▼─────────────┐
│ daily_stock_analysis   │  LLM 解读 / 盘后日报
│ 人话解释 / 风险清单      │  推送到企微/飞书
└────────────────────────┘
```

---

## 4. 用这些项目完成 A 股选股建议的步骤

### Step 1：建股票池
用 AkShare：
- 全 A 股
- 剔除 ST / 退市 / 上市 < 250 个交易日
- 剔除日均成交额过低股票
- 按行业/板块分组

输出：
```text
universe.csv
code, name, board, industry, list_date
```

---

### Step 2：做因子与择时信号
从 QuantsPlaybook 里挑 3~5 个 A 股验证过的信号：

1. RSRS 市场择时：决定仓位 0 / 50% / 100%
2. 聪明钱因子：个股资金结构
3. 20 日动量改进：避免除权后假动量
4. 北向/主力资金过滤：连续流出扣分
5. 波动率/换手率过滤：妖股降权

每个因子归一化成 0~100 分。

---

### Step 3：回测信号，别信肉眼
用 RQAlpha 或 magic-alt/stock：

- 回测周期拆开：
  - 2018–2019 熊市
  - 2020–2021 结构性行情
  - 2022 熊市
  - 2023–2025 震荡
  - 2026 样本外
- 必须记录：
  - 年化收益
  - 最大回撤
  - 夏普
  - 胜率
  - 换手率
  - 涨停买不进次数
  - 跌停卖不出次数
  - 单边佣金+印花税后的净收益

---

### Step 4：生成“选股建议”
最终建议不是 LLM 说买，而是：

```text
买入候选：
  600519.SH  总分 82  动量 90  资金 75  估值 60  涨停可买性 OK
  300750.SZ  总分 74  动量 80  资金 70  估值 55  高波动预警

观望：
  000725.SZ  动量好但资金流出，等回踩确认

回避：
  XXX.ST     停牌/ST/异常波动/流动性差
```

建议分级：
- 强买入
- 回调买入
- 持有观察
- 减仓
- 回避

---

### Step 5：用 LLM 做人类可读报告
把回测结果喂给 daily_stock_analysis：

```text
以下股票通过 A 股回测信号：
600519 总分 82，RSRS 看多，聪明钱因子正向，20 日改进动量靠前
请生成盘后投研摘要：
- 为什么入选
- 关键风险
- 买入/观望/卖出
- 止损与目标价框架
- 不构成投资建议
```

LLM 只做：
- 总结
- 解释
- 风险提示
- 推送

不做：
- 最终下单
- 保证收益
- 替代回测

---

## 5. A 股回测防作弊清单

回测 A 股必须检查：

- [ ] T+1：当日买入不能当日卖出
- [ ] 涨跌停：涨停买不进，跌停卖不出
- [ ] 复权口径统一：因子用后复权，成交用实际可成交价
- [ ] 100 股一手，科创板 200 股，ETF 100 份
- [ ] 买入佣金、卖出佣金、最低 5 元
- [ ] 卖出印花税 0.1%
- [ ] 过户费
- [ ] 停牌期间不能成交
- [ ] 财务/公告/龙虎榜无未来函数
- [ ] 样本外区间不参与参数选择
- [ ] 换手率过高时交易成本会吃掉 alpha

---

## 6. 项目分工一句话总结

- **AkShare**：给我 A 股数据
- **QuantsPlaybook**：给我因子和研报灵感
- **RQAlpha**：用 A 股规则回测
- **magic-alt/stock**：做 A 股原生平台 / 仿真 / 策略准入
- **Backtrader**：只在你愿意自己写 A 股规则时用
- **daily_stock_analysis**：把信号变成人话，做盘后报告

---

## 7. 最小落地路线

### 阶段 1：能跑
1. AkShare 拉全 A 日线
2. 写 3 个因子
3. RQAlpha 回测双均线 + 动量
4. 输出每天前 20 名股票

### 阶段 2：能信
1. 加 T+1 / 涨跌停 / 费用
2. 分牛熊样本外
3. 用 magic-alt/stock 做策略准入
4. 记录夏普 / 回撤 / 换手

### 阶段 3：能看
1. 接 daily_stock_analysis
2. 每天收盘生成 A 股选股日报
3. 推飞书 / 企微
4. 每月统计“系统建议 vs 实际收益”

### 阶段 4：能仿真
1. 接 QMT / XTQuant 模拟盘
2. 只发信号，不自动下单
3. 人工确认后才交易

---

## 8. 免责声明

本项目用于：
- 量化学习
- 策略研究
- 回测验证
- 投研信息整理

不构成：
- 投资建议
- 收益承诺
- 自动交易系统
- 实盘操作依据

A 股回测结果通常优于实盘；任何买卖应由使用者自行承担风险。

---

如果你愿意，下一步我可以帮你把上面内容再拆成：

1. `docs/architecture.md`
2. `strategy/factor_score.py`
3. `backtest/rqalpha_config.yaml`
4. `llm/report_prompt.md`
5. `data/update_universe.py`

也就是直接变成可运行仓库结构。

结论先说：

> **GitHub 上“看代码/ Fork 代码”可以，但“跑起来”基本都要下载到本地（或自己的机器 / 容器 / GitHub Actions）里跑。**  
> GitHub 页面本身不是 Python 运行环境，不能直接帮你跑 AkShare / RQAlpha / Backtrader / magic-alt/stock。

只有 `daily_stock_analysis` 这种项目**天然支持 GitHub Actions 定时跑**；  
RQAlpha / Backtrader / magic-alt/stock / QuantsPlaybook **都是本地研究/回测工具**。

---

## 一、你这套仓库里，各自该怎么跑

### 1️⃣ AkShare
**必须本地 / 容器里跑**
```bash
pip install akshare
python data/update_universe.py
```
GitHub 网页点开没用，它只是代码。

✅ 可以写 GitHub Actions 定时跑“拉数据”  
❌ 不能“在 GitHub 网页里直接分析 A 股”

---

### 2️⃣ RQAlpha
**本地运行（强烈推荐）**

```bash
pip install rqalpha
rqalpha download-bundle
rqalpha run -f backtest/strategy_ma.py -s 2020-01-01 -e 2025-12-31 -p 1000000
```

RQAlpha 官方就要求：
- Python 环境
- 下载 bundle / 接数据源
- 命令行跑 

✅ 本地  
✅ 服务器  
✅ Docker  
❌ GitHub 网页直接跑

> 你也可以写 GitHub Actions 跑 RQAlpha，但那也是“Actions  runner 里跑”，不是 GitHub 网页跑。

---

### 3️⃣ Backtrader
**纯本地 Python 脚本**

```bash
pip install backtrader
python backtest/run_backtrader.py
```

没有 bundle，没有服务端，就是一个 Python 框架。

---

### 4️⃣ magic-alt/stock
**本地 / 服务器 / Docker**

它不是“点一下就跑”的轻量脚本，而是：
- FastAPI
- Vue 前端
- 回测引擎
- 仿真/实盘网关适配

正确方式：
```bash
git clone https://github.com/magic-alt/stock
pip install -r requirements.txt
python examples/one_click_demo.py
```

⚠️ 新手别一上来跑全套平台，先跑 example / 单策略。

---

### 5️⃣ QuantsPlaybook
**本地 Jupyter / notebook 研究用**

```bash
git clone https://github.com/hugo2046/QuantsPlaybook
jupyter lab
```
打开：
```
C-择时类/RSRS择时指标/RSRS.ipynb
```

它不是回测平台，是**研报复现笔记本**。

---

### 6️⃣ daily_stock_analysis
**这个最特殊：GitHub Actions 也能跑**

两种方式都行：

#### ✅ 方式 A：GitHub Actions 零成本
1. Fork 仓库
2. Settings → Secrets 里配：
   - `STOCK_LIST=600519,300750,000001`
   - `DEEPSEEK_API_KEY=xxx`
   - `WECHAT_WEBHOOK_URL=xxx`
3. Actions → 启用工作流
4. 每个交易日 18:00 自动跑，推企微/飞书

✅ 不用自己服务器  
✅ 适合“每天出 AI 报告”

---

#### ✅ 方式 B：本地跑
```bash
git clone https://github.com/ZhuLinsen/daily_stock_analysis
pip install -r requirements.txt
cp .env.example .env
python main.py
```

---

## 二、你这个「a-share-picker」仓库应该怎么做

### ✅ 推荐架构（现实可落地）

```text
AkShare / Tushare        → 本地定时拉数据
QuantsPlaybook           → 本地 notebook 研究因子
factor_score.py          → 本地算分
RQAlpha / Backtrader     → 本地回测
magic-alt/stock          → 本地/服务器做仿真
daily_stock_analysis     → GitHub Actions 出 AI 日报（可选）
```

### ✅ 新手正确顺序

**第 1 步：本地跑通**
```bash
git clone 你的仓库
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python data/update_universe.py
python strategy/factor_score.py
python backtest/run_rqalpha.py --strategy backtest/strategy_ma.py
```

**第 2 步：把 daily_stock_analysis 单独 Fork 去 GitHub Actions 跑**
> 别把 RQAlpha 塞进 GitHub Actions 当主系统，没必要。

**第 3 步：本地出股票池 → 丢给 LLM 项目生成人话报告**

---

## 三、一句话对照表

| 项目 | GitHub 网页 | 本地 Python | GitHub Actions | Docker |
|---|---|---|---|---|
| AkShare | ❌ | ✅ | ✅（拉数据） | ✅ |
| RQAlpha | ❌ | ✅✅ | ✅（高级） | ✅ |
| Backtrader | ❌ | ✅✅ | ✅ | ✅ |
| magic-alt/stock | ❌ | ✅ | ⚠️ 复杂 | ✅✅ |
| QuantsPlaybook | ❌ | ✅（notebook） | ⚠️ | ⚠️ |
| daily_stock_analysis | ❌ | ✅ | ✅✅ 零成本 | ✅✅ |

---

## 四、你可以直接写进 README 的这段话

```markdown
## 运行方式说明

本项目不是“在 GitHub 网页直接运行”的应用。
GitHub 用于：托管代码、版本管理、Issues、Actions 定时任务。

实际运行需要 Python 环境：

- 数据层（AkShare / Tushare）：本地或 GitHub Actions 定时执行
- 因子层（QuantsPlaybook / factor_score）：本地 Jupyter / Python
- 回测层（RQAlpha / Backtrader / magic-alt）：本地或服务器
- LLM 报告层（daily_stock_analysis）：可本地运行，也可用 GitHub Actions 零成本定时推送

最小上手：
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python data/update_universe.py
python strategy/factor_score.py
python backtest/run_rqalpha.py --strategy backtest/strategy_ma.py
```

AI 日报可单独 Fork daily_stock_analysis，
配置 STOCK_LIST / LLM_KEY / Webhook 后用 GitHub Actions 自动运行。
```

---

如果你愿意，下一步我可以帮你：
1. 写一个 **GitHub Actions 工作流**：收盘后拉数据 + 跑因子 + 出 CSV
2. 把 `daily_stock_analysis` 接进你自己的 `factor_score.py` 输出
3. 给你一个 **本地一键脚本 `run_pipeline.py`**：更新数据 → 算分 → 回测 → 出报告

你要哪个？
