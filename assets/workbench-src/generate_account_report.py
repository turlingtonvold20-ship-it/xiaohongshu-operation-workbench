from __future__ import annotations

import re

from .generate_competitor_table import _source_rows
from .utils import (
    INPUT_DIR,
    OUTPUT_DIR,
    account_name,
    bullet_fields,
    markdown_table_rows,
    read_text,
    section,
    write_text,
    write_workbook,
)


def _h2_section(text: str, name: str, default: str = "待补充") -> str:
    match = re.search(
        rf"^##\s+{re.escape(name)}\s*$\n(.*?)(?=^##\s+|\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    return match.group(1).strip() if match and match.group(1).strip() else default


def _basic_fields(text: str) -> dict[str, str]:
    keys = {
        "账号名称", "账号链接", "说明", "行业类型", "账号简介", "粉丝数", "获赞与收藏",
        "笔记数量", "账号阶段", "账号主要内容", "账号目标用户", "备注",
    }
    fields: dict[str, list[str]] = {}
    current = ""
    for line in _h2_section(text, "账号基础信息", "").splitlines():
        match = re.match(r"^([^：]+)：\s*(.*)$", line.strip())
        if match and match.group(1).strip() in keys:
            current = match.group(1).strip()
            fields[current] = [match.group(2).strip()] if match.group(2).strip() else []
        elif current and line.strip() and line.strip() != "---":
            fields[current].append(line.strip())
    return {key: "\n".join(values).strip() for key, values in fields.items()}


def generate() -> None:
    basic_text = read_text(INPUT_DIR / "01_account_basic.md")
    analysis_text = read_text(INPUT_DIR / "02_account_analysis.md")
    competitor_text = read_text(INPUT_DIR / "03_competitor_analysis.md")
    strategy_text = read_text(INPUT_DIR / "04_content_strategy.md")
    basic = _basic_fields(basic_text)
    competitors = _source_rows(competitor_text)

    competitor_lines = [
        f"- {row.get('竞品账号', '待补充')}：{row.get('可借鉴方向', row.get('可借鉴点', '待补充'))}"
        for row in competitors
    ] or ["- 待补充"]
    basic_lines = [f"- {key}：{value}" for key, value in basic.items()] or ["- 待补充"]
    report = f"""# {account_name()}账号运营报告

> 本报告仅整理已提供的账号资料和 ChatGPT 分析，不新增运营判断。发布与执行前请人工复核。

## 账号基础信息

{chr(10).join(basic_lines)}

## 账号定位

{_h2_section(analysis_text, "账号定位分析", _h2_section(strategy_text, "账号内容定位"))}

## 目标用户

{_h2_section(strategy_text, "目标用户")}

## 内容栏目

{_h2_section(strategy_text, "内容栏目设计")}

## 竞品参考

{chr(10).join(competitor_lines)}

## 当前问题

{section(analysis_text, "内容问题")}

## 优化方向

{section(analysis_text, "优化建议")}

## 执行建议

{section(analysis_text, "执行建议")}
"""
    write_text(OUTPUT_DIR / "account_report.md", report)

    rows = [
        {"模块": "账号基础信息", "内容": "\n".join(basic_lines)},
        {"模块": "账号定位", "内容": _h2_section(analysis_text, "账号定位分析", _h2_section(strategy_text, "账号内容定位"))},
        {"模块": "目标用户", "内容": _h2_section(strategy_text, "目标用户")},
        {"模块": "内容栏目", "内容": _h2_section(strategy_text, "内容栏目设计")},
        {"模块": "竞品参考", "内容": "\n".join(competitor_lines)},
        {"模块": "当前问题", "内容": section(analysis_text, "内容问题")},
        {"模块": "优化方向", "内容": section(analysis_text, "优化建议")},
        {"模块": "执行建议", "内容": section(analysis_text, "执行建议")},
    ]
    write_workbook(OUTPUT_DIR / "account_report.xlsx", "账号报告", ["模块", "内容"], rows)


if __name__ == "__main__":
    generate()
