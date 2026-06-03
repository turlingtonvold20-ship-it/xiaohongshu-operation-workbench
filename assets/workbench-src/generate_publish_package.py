from __future__ import annotations

import re
import shutil

from .utils import (
    OUTPUT_DIR,
    PUBLISH_DIR,
    PUBLISH_HEADERS,
    build_carousel_with_adapter,
    materialize_publish_package,
    read_workbook_rows,
    write_workbook,
)


def _clear_previous_packages() -> None:
    for path in PUBLISH_DIR.iterdir():
        if path.is_dir() and re.match(r"^\d{3}_", path.name):
            shutil.rmtree(path)


def build_publish_rows() -> list[dict[str, object]]:
    humanized = read_workbook_rows(OUTPUT_DIR / "humanized_content_library.xlsx")
    rows = []
    for source in humanized:
        pages = build_carousel_with_adapter(source)
        package_path = materialize_publish_package(source, pages)
        page_summary = "\n".join(
            f"第 {page['页码']} 页｜{page['页面任务']}：{page['页面文案']}" for page in pages
        )
        rows.append(
            {
                "序号": source.get("序号", ""),
                "账号名称": source.get("账号名称", ""),
                "内容栏目": source.get("内容栏目", ""),
                "选题标题": source.get("选题标题", ""),
                "发布标题": source.get("润色后标题", ""),
                "封面文案": source.get("润色后封面文案", ""),
                "图文页数": len(pages),
                "每页内容摘要": page_summary,
                "正文文案": source.get("润色后正文", ""),
                "标签": source.get("标签建议", ""),
                "评论区引导语": source.get("润色后评论区引导语", ""),
                "发布状态": "待审核",
                "发布包路径": package_path,
                "备注": "候选发布包；视觉图片可继续交给 xhs-carousel-publisher skill 生成",
            }
        )
    return rows


def generate() -> None:
    _clear_previous_packages()
    write_workbook(
        OUTPUT_DIR / "xhs_publish_package.xlsx",
        "发布包汇总",
        PUBLISH_HEADERS,
        build_publish_rows(),
        validations={"发布状态": ["待审核", "待发布", "已发布", "暂不发布"]},
    )


if __name__ == "__main__":
    generate()
