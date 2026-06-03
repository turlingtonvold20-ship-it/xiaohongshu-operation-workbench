---
name: xiaohongshu-operation-workbench
description: Run the local Xiaohongshu operations content-production workbench from natural-language requests. Use when the user asks to initialize, inspect, or execute the 小红书运营工作台; generate account reports, competitor tables, candidate topic libraries, draft copy, humanized copy, carousel structures, publish packages, 30-day calendars, shooting task lists, or client weekly reports from the provided input files; or run the complete Xiaohongshu content workflow without manually changing directories.
---

# Xiaohongshu Operation Workbench

Use the existing local workbench as a deterministic execution layer. Keep all generated topics, copy, calendars, and publish packages marked as candidates until ChatGPT or a human reviews them.

## Project Location

Default project:

```text
/Users/jony/Documents/小红书运营/xiaohongshu-operation-workbench
```

Use `scripts/run_workbench.py` so commands work from any current directory. Override the project location only when the user provides another workbench path:

```bash
python3 scripts/run_workbench.py --root "/absolute/project/path" all
```

## Workflow

1. Inspect `input/` when the user asks whether the workbench is ready or supplies new source material.
2. Do not overwrite user input files unless the user explicitly asks to update them.
3. Run `status` before execution. If it reports bundled scripts pending synchronization, ask before running `sync`; this command backs up replaced modules under `src/_skill_backup/`.
4. Select the narrowest command that fulfills the request. Use `all` for a complete refresh.
5. Run the wrapper from this skill folder:

```bash
python3 scripts/run_workbench.py all
```

6. Check the command output. For complete runs, report the key files and counts under `output/` and `publish_packages/`.
7. Remind the user that generated materials require ChatGPT or human review before publishing.

## Bundled Compatibility Patches

The skill includes reviewed workbench modules under `assets/workbench-src/`. They add support for:

- seed topics stored as Markdown tables or `### 选题 N` cards;
- competitor research stored as Markdown tables or internal high-performing-note sections;
- richer multi-line account fields and strategy sections in account reports;
- cleanup of previously generated numbered publish-package folders before regeneration.

Synchronize these modules into the selected project only when explicitly requested:

```bash
python3 scripts/run_workbench.py sync
```

## Command Map

| User intent | Command |
| --- | --- |
| 初始化模板和目录 | `init` |
| 查看工作台输入输出状态 | `status` |
| 同步 skill 内置兼容补丁 | `sync` |
| 生成账号报告 | `report` |
| 生成竞品拆解表 | `competitor` |
| 扩展候选选题 | `topics` |
| 批量生成文案初稿 | `contents` |
| 生成基础去人机润色对照库 | `humanize` |
| 生成图文页面结构 | `carousel` |
| 生成发布包和汇总表 | `publish` |
| 生成 30 天排期 | `calendar` |
| 生成拍摄任务 | `shooting` |
| 生成客户周报 | `weekly` |
| 刷新完整流水线 | `all` |
| 列出交付文件 | `outputs` |

## Skill Handoffs

The Python workbench contains conservative local adapters. It does not invoke Codex skills from Python.

- When the user asks for deeper copy editing or final copy review, use `humanizer-zh` on the selected draft after the workbench run.
- When the user asks for finished carousel images, PNG/JPG bundles, or PDF packages, use `xhs-carousel-publisher` on the selected publish package after the workbench run.
- Do not automatically render high-fidelity carousel images for every candidate topic unless the user explicitly requests that batch.

## Guardrails

- Process only files and content supplied by the user.
- Do not crawl Xiaohongshu.
- Do not reverse-engineer interfaces.
- Do not automate login or bypass platform restrictions.
- Do not make final account-positioning, topic-approval, copy-approval, or publishing decisions.
- Do not claim content is publish-ready before human review.
