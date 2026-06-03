from __future__ import annotations

import re

from .utils import COMPETITOR_HEADERS, INPUT_DIR, OUTPUT_DIR, markdown_table_rows, read_text, write_workbook


def _labeled_fields(block: str) -> dict[str, str]:
    fields: dict[str, list[str]] = {}
    current = ""
    for line in block.splitlines():
        match = re.match(r"^([^：]+)：\s*(.*)$", line.strip())
        if match:
            current = match.group(1).strip()
            fields[current] = [match.group(2).strip()] if match.group(2).strip() else []
        elif current and line.strip():
            fields[current].append(line.strip())
    return {key: "\n".join(values).strip() for key, values in fields.items()}


def _source_rows(text: str) -> list[dict[str, str]]:
    rows = markdown_table_rows(text)
    if rows:
        return rows

    internal = text.split("## 当前账号内部高表现内容拆解", 1)
    if len(internal) < 2:
        return []
    body = internal[1].split("\n## ", 1)[0]
    matches = list(re.finditer(r"^###\s+\d+\.\s+《(.+?)》\s*$", body, flags=re.MULTILINE))
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        fields = _labeled_fields(body[match.end():end])
        rows.append(
            {
                "竞品账号": "本账号高表现内容",
                "账号链接": "",
                "行业": "品牌策略 / 品牌设计",
                "账号定位": fields.get("内容类型", ""),
                "爆款内容": match.group(1),
                "标题结构": fields.get("标题结构", ""),
                "封面特点": fields.get("封面特点", ""),
                "评论区需求": fields.get("评论区需求", ""),
                "可借鉴点": fields.get("可借鉴逻辑", ""),
                "不建议模仿点": fields.get("不建议直接模仿的地方", ""),
                "备注": "外部竞品账号待补充；当前为账号内部高表现内容拆解",
            }
        )
    return rows


def generate() -> None:
    source_rows = _source_rows(read_text(INPUT_DIR / "03_competitor_analysis.md"))
    rows = []
    for index, source in enumerate(source_rows, 1):
        rows.append(
            {
                "序号": index,
                "竞品账号": source.get("竞品账号", ""),
                "账号链接": source.get("账号链接", ""),
                "行业": source.get("行业", ""),
                "账号定位": source.get("账号定位", ""),
                "爆款内容": source.get("爆款内容", ""),
                "标题结构": source.get("标题结构", ""),
                "封面特点": source.get("封面特点", ""),
                "用户需求": source.get("用户需求", source.get("评论区需求", "")),
                "可借鉴点": source.get("可借鉴点", source.get("可借鉴方向", "")),
                "不建议模仿点": source.get("不建议模仿点", ""),
                "备注": source.get("备注", ""),
            }
        )
    write_workbook(OUTPUT_DIR / "competitor_analysis.xlsx", "竞品拆解", COMPETITOR_HEADERS, rows)


if __name__ == "__main__":
    generate()
