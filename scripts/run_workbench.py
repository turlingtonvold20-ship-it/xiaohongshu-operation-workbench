#!/usr/bin/env python3
"""Run the local Xiaohongshu operations workbench from any directory."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


DEFAULT_ROOT = Path("/Users/jony/Documents/小红书运营/xiaohongshu-operation-workbench")
DEFAULT_CODEX_PYTHON = Path(
    "/Users/jony/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"
)
WORKBENCH_COMMANDS = {
    "init",
    "report",
    "competitor",
    "topics",
    "contents",
    "humanize",
    "carousel",
    "publish",
    "calendar",
    "shooting",
    "weekly",
    "all",
}
INPUT_FILES = [
    "01_account_basic.md",
    "02_account_analysis.md",
    "03_competitor_analysis.md",
    "04_content_strategy.md",
    "05_seed_topics.md",
    "06_copywriting_rules.md",
    "07_draft_inputs.md",
    "08_client_notes.md",
]
PATCH_DIR = Path(__file__).resolve().parents[1] / "assets" / "workbench-src"
PATCH_MODULES = [
    "generate_account_report.py",
    "generate_competitor_table.py",
    "generate_topic_library.py",
    "generate_publish_package.py",
]


def resolve_python() -> str:
    configured = os.environ.get("XHS_WORKBENCH_PYTHON")
    if configured:
        return configured
    if DEFAULT_CODEX_PYTHON.exists():
        return str(DEFAULT_CODEX_PYTHON)
    return shutil.which("python3") or sys.executable


def project_root(value: str | None) -> Path:
    configured = value or os.environ.get("XHS_WORKBENCH_ROOT")
    return Path(configured).expanduser().resolve() if configured else DEFAULT_ROOT


def ensure_project(root: Path) -> None:
    run_file = root / "run.py"
    if not run_file.exists():
        raise SystemExit(f"未找到工作台入口：{run_file}")


def pending_patch_modules(root: Path) -> list[str]:
    pending = []
    for filename in PATCH_MODULES:
        source = PATCH_DIR / filename
        target = root / "src" / filename
        if not source.exists():
            raise SystemExit(f"skill 缺少补丁文件：{source}")
        if not target.exists() or source.read_bytes() != target.read_bytes():
            pending.append(filename)
    return pending


def sync_patches(root: Path) -> None:
    ensure_project(root)
    pending = pending_patch_modules(root)
    if not pending:
        print("工作台脚本已是 skill 内的最新版本。")
        return

    backup_dir = root / "src" / "_skill_backup" / datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir.mkdir(parents=True, exist_ok=True)
    for filename in pending:
        source = PATCH_DIR / filename
        target = root / "src" / filename
        if target.exists():
            shutil.copy2(target, backup_dir / filename)
        shutil.copy2(source, target)
        print(f"已同步：{filename}")
    print(f"原脚本备份：{backup_dir}")


def print_status(root: Path) -> None:
    ensure_project(root)
    print(f"工作台：{root}")
    print("\n输入文件：")
    for filename in INPUT_FILES:
        path = root / "input" / filename
        state = "已存在" if path.exists() and path.stat().st_size else "缺失或为空"
        print(f"- {state}：{path}")
    print("\n输出文件：")
    output_dir = root / "output"
    output_files = sorted(path for path in output_dir.glob("*") if path.is_file())
    if not output_files:
        print("- 尚未生成")
    for path in output_files:
        print(f"- {path.name}")
    package_dir = root / "publish_packages"
    packages = [
        path
        for path in package_dir.iterdir()
        if path.is_dir() and path.name != "每条笔记单独一个文件夹"
    ] if package_dir.exists() else []
    print(f"\n独立发布包：{len(packages)} 个")
    pending = pending_patch_modules(root)
    print(f"\nskill 脚本同步状态：{'待同步：' + ', '.join(pending) if pending else '已是最新版本'}")


def print_outputs(root: Path) -> None:
    ensure_project(root)
    for directory in (root / "output", root / "publish_packages"):
        print(f"{directory}:")
        if not directory.exists():
            print("- 目录不存在")
            continue
        for path in sorted(directory.iterdir()):
            print(f"- {path.name}")


def run(root: Path, command: str) -> None:
    ensure_project(root)
    python = resolve_python()
    subprocess.run([python, str(root / "run.py"), command], cwd=root, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="从任意目录运行小红书运营工作台")
    parser.add_argument("--root", help="覆盖默认工作台路径")
    parser.add_argument("command", choices=[*sorted(WORKBENCH_COMMANDS), "status", "outputs", "sync"])
    args = parser.parse_args()
    root = project_root(args.root)

    if args.command == "status":
        print_status(root)
    elif args.command == "outputs":
        print_outputs(root)
    elif args.command == "sync":
        sync_patches(root)
    else:
        run(root, args.command)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
