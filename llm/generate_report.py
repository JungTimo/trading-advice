"""
生成 LLM 投研日报
"""
import openai
import yaml
from pathlib import Path
from loguru import logger


def load_prompt(template_path="llm/report_prompt.md", **kwargs):
    template = Path(template_path).read_text(encoding="utf-8")
    return template.format(**kwargs)


def generate(stock_list: str, model="deepseek-chat"):
    """
    stock_list: 格式化后的股票信号文本
    """
    prompt = load_prompt(stock_list=stock_list)

    client = openai.OpenAI(
        base_url="https://api.deepseek.com/v1",
        api_key="your-key-here"   # 从环境变量读
    )

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是 A 股量化研究员"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    report = resp.choices[0].message.content
    logger.info("报告生成完成")

    # 保存
    out = Path("llm/reports")
    out.mkdir(exist_ok=True)
    out_file = out / f"report_{pd.Timestamp.now().strftime('%Y%m%d')}.md"
    out_file.write_text(report, encoding="utf-8")

    return report


if __name__ == "__main__":
    import pandas as pd
    # 示例
    sample = """
    600519.SH 贵州茅台  score=82  signal=strong_buy
    因子: 动量90 资金75 RSRS 0.8
    """
    report = generate(sample)
    print(report)
