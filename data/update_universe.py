"""
更新 A 股股票池
输出: data/cache/universe.parquet
"""
import akshare as ak
import pandas as pd
from loguru import logger
from pathlib import Path

def load_config():
    import yaml
    with open("config/universe.yaml") as f:
        return yaml.safe_load(f)

def update_universe():
    cfg = load_config()
    logger.info("拉取 A 股股票列表...")

    # AkShare 获取全 A 列表
    df = ak.stock_info_a_code_name()

    # 拉取详细信息
    spot = ak.stock_zh_a_spot_em()
    spot = spot[["代码", "名称", "上市时间", "所属行业", "板块"]]

    df = df.merge(spot, left_on="code", right_on="代码", how="left")

    # 过滤
    if cfg["filters"]["exclude_st"]:
        df = df[~df["名称"].str.contains("ST", na=False)]

    if cfg["filters"]["exclude_delisted"]:
        df = df[~df["名称"].str.contains("退", na=False)]

    if cfg["filters"]["min_list_days"]:
        min_days = cfg["filters"]["min_list_days"]
        df["上市时间"] = pd.to_datetime(df["上市时间"])
        df = df[df["上市时间"] <= pd.Timestamp.now() - pd.Timedelta(days=min_days)]

    # 行业过滤
    if cfg["industry_whitelist"]:
        df = df[df["所属行业"].isin(cfg["industry_whitelist"])]

    # 板块过滤
    if cfg["boards"]:
        df = df[df["板块"].isin(cfg["boards"])]

    # 保存
    Path("data/cache").mkdir(parents=True, exist_ok=True)
    df.to_parquet("data/cache/universe.parquet", index=False)
    logger.info(f"股票池更新完成: {len(df)} 只")

    return df

if __name__ == "__main__":
    update_universe()
