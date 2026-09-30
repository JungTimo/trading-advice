"""
RQAlpha 回测入口
用法: python run_rqalpha.py --strategy ma_cross --start 2020-01-01 --end 2025-12-31
"""
import subprocess
import sys
import yaml
from pathlib import Path


def load_config():
    with open("config/backtest.yaml") as f:
        return yaml.safe_load(f)


def run(strategy_file: str, start: str = None, end: str = None):
    cfg = load_config()
    start = start or cfg["start_date"]
    end = end or cfg["end_date"]

    cmd = [
        sys.executable, "-m", "rqalpha", "run",
        "-f", strategy_file,
        "-s", start,
        "-e", end,
        "-p", str(cfg["initial_cash"]),
        "--plot",
        "--output-dir", "backtest/results"
    ]

    # A股规则
    rules = cfg["rules"]
    if rules["t_plus_one"]:
        cmd.append("--t-plus-one")
    if rules["limit_up_down"]:
        cmd.append("--limit-up-down")

    logger.info(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--strategy", required=True)
    parser.add_argument("--start")
    parser.add_argument("--end")
    args = parser.parse_args()

    run(args.strategy, args.start, args.end)
