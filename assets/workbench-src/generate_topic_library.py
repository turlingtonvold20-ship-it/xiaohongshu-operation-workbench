from __future__ import annotations

from collections import defaultdict
import re

from .utils import (
    INPUT_DIR,
    OUTPUT_DIR,
    TOPIC_HEADERS,
    account_name,
    markdown_table_rows,
    read_text,
    write_workbook,
)


TITLE_PATTERNS = [
    "{痛点}，先别急着做表面动作",
    "遇到{痛点}，可以先检查这 5 件事",
    "{栏目}里最容易被忽略的一个问题",
    "关于{主题}，客户最常问的 4 个问题",
    "为什么只处理表面动作，解决不了{痛点}",
    "{主题}：落到执行到底要拆成哪几步",
    "如果正在遇到{痛点}，先把这张清单过一遍",
    "做{栏目}时，别急着套模板",
    "{痛点}，通常不是单一环节的问题",
    "怎么判断{栏目}该从哪里开始调整",
]
FORMATS = ["攻略清单", "避坑说明", "对比分析", "图文", "案例拆解", "口播", "攻略清单"]


def _short(value: str, limit: int = 20) -> str:
    value = str(value or "").strip()
    return value if len(value) <= limit else value[:limit].rstrip("，。！？ ") + "…"


def _seed_topic_rows(text: str) -> list[dict[str, str]]:
    rows = markdown_table_rows(text)
    if rows:
        return rows

    # Newer research files use editable topic cards instead of a Markdown table.
    card_rows: list[dict[str, str]] = []
    for block in re.split(r"(?=^###\s+选题\s+\d+\s*$)", text, flags=re.MULTILINE):
        if not re.match(r"^###\s+选题\s+\d+\s*$", block.splitlines()[0].strip()):
            continue
        row: dict[str, str] = {}
        for line in block.splitlines()[1:]:
            match = re.match(r"^([^：:]+)[：:]\s*(.+?)\s*$", line.strip())
            if match:
                row[match.group(1).strip()] = match.group(2).strip()
        if row.get("选题标题"):
            card_rows.append(row)
    return card_rows


def generate() -> None:
    strategy = read_text(INPUT_DIR / "04_content_strategy.md")
    seeds = _seed_topic_rows(read_text(INPUT_DIR / "05_seed_topics.md"))
    if not seeds:
        raise ValueError("input/05_seed_topics.md 中没有可用的选题表格或选题卡片")

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for seed in seeds:
        grouped[seed.get("内容栏目", "待补充栏目")].append(seed)

    rows = []
    sequence = 1
    for column, column_seeds in grouped.items():
        # 每个栏目至少扩展 10 条。多条种子会轮流作为来源，避免脱离已审核方向。
        for offset in range(max(10, len(column_seeds) * 10)):
            seed = column_seeds[offset % len(column_seeds)]
            pattern = TITLE_PATTERNS[offset % len(TITLE_PATTERNS)]
            pain = _short(seed.get("用户痛点", "用户问题"), 16)
            seed_title = _short(seed.get("选题标题", column), 18)
            title = pattern.format(痛点=pain, 栏目=column, 主题=seed_title)
            rows.append(
                {
                    "序号": sequence,
                    "账号名称": account_name(),
                    "内容栏目": column,
                    "选题标题": title,
                    "用户痛点": seed.get("用户痛点", ""),
                    "内容角度": seed.get("内容角度", ""),
                    "封面文案": title[:18],
                    "内容形式": FORMATS[offset % len(FORMATS)],
                    "转化动作": seed.get("转化动作", ""),
                    "参考来源": f"种子选题扩展：{seed.get('选题标题', '')}",
                    "优先级": "A优先发布" if offset < 3 else "B备选" if offset < 8 else "C暂不发布",
                    "状态": "待生成",
                    "备注": "候选稿，需 ChatGPT 或人工审核；已读取内容策略" if strategy else "候选稿，需补充内容策略",
                }
            )
            sequence += 1
    write_workbook(
        OUTPUT_DIR / "topic_library.xlsx",
        "候选选题库",
        TOPIC_HEADERS,
        rows,
        validations={
            "内容形式": ["图文", "视频", "口播", "案例拆解", "攻略清单", "避坑说明", "对比分析"],
            "优先级": ["A优先发布", "B备选", "C暂不发布"],
            "状态": ["待生成", "待审核", "暂不发布"],
        },
    )


if __name__ == "__main__":
    generate()
