#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""每周看板构建脚本（与 templates/dashboard-template.html 配套）

用法：
  python scripts/build_dashboard.py <games.json> <输出.html> [-t "2026-10-10"] [-d 输出素材目录]

- 读取 validate_scores.py 校验通过的 games.json；
- 将 GAMES 数据注入模板（模板内 __GAMES_DATA__ 占位符），周次写入 __WEEK_LABEL__；
- 生成最终单文件交互看板 HTML，素材按相对路径 assets/ 引用；
- 缺素材的游戏由模板内 onerror 自动回退渐变字块，不会裂图。

每周围绕模板的一致性保证：布局/CSS/JS/ECharts/手机适配全部来自模板，
本周只换数据与素材；「灵感总结」「观察项」两节在生成后按周更新内容。
"""
import argparse
import json
import shutil
import sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("games_json", help="校验通过的 games.json 路径")
    ap.add_argument("output", help="输出 HTML 路径")
    ap.add_argument("-t", "--week-label", default="YYYY-MM-DD", help="标题周次，如 2026-10-10")
    ap.add_argument("-d", "--deploy-dir", help="发布目录（默认=输出文件所在目录）")
    ap.add_argument("--insights", help="本周「灵感总结」内容片段（HTML），替换模板 __WEEKLY_INSIGHTS__")
    ap.add_argument("--watchlist", help="本周「观察项清单」内容片段（HTML），替换模板 __WEEKLY_WATCHLIST__")
    args = ap.parse_args()

    template_path = Path(__file__).resolve().parent.parent / "templates" / "dashboard-template.html"
    if not template_path.exists():
        sys.exit(f"模板不存在：{template_path}")

    with open(args.games_json, encoding="utf-8") as f:
        games = json.load(f)
    if not isinstance(games, list) or not games:
        sys.exit("games.json 为空或格式错误")

    html = template_path.read_text(encoding="utf-8")
    data_json = json.dumps(games, ensure_ascii=False, indent=2)

    # 静态预载块：只列出输出目录 assets/ 中实际存在的素材（发布链路静态扫描
    # 只认 <img src>/CSS url()，JS 拼接路径会导致素材漏传、线上裂图）。
    deploy_dir = Path(args.deploy_dir) if args.deploy_dir else out.parent
    assets_dir = deploy_dir / "assets"
    preload = []
    if assets_dir.exists():
        names = {f.name for f in assets_dir.iterdir() if f.is_file()}
        SUFFIX = ("webp", "jpg", "jpeg", "png")

        def find(prefix):
            for cand in sorted(names):
                if cand.startswith(prefix) and cand.rsplit(".", 1)[-1].lower() in SUFFIX:
                    return cand
            return None

        for g in games:
            # 素材存在性注入：缺素材时清空 icon/shots，模板直接渲染渐变字块，
            # 避免运行时 <img> 404（shot.py 会把这类失败记为 consoleErrors/resourceErrors）。
            # icon 兼容 _icon.* 与 _header.*（header 兜底），预载/清空均按实际文件名。
            icon_f = find(f"{g['id']}_icon.") or find(f"{g['id']}_header.")
            shot_f = find(f"{g['id']}_shot1.")
            if not icon_f:
                g["icon"] = ""
            if not shot_f:
                g["shots"] = []
            if icon_f:
                preload.append(f'<img src="assets/{icon_f}">')
            if shot_f:
                preload.append(f'<img src="assets/{shot_f}">')
    html = (html.replace("__GAMES_DATA__", data_json)
                .replace("__WEEK_LABEL__", args.week_label)
                .replace("__PRELOAD_IMGS__", "\n    ".join(preload) or "<!-- 本周无本地素材 -->"))
    if args.insights:
        html = html.replace("__WEEKLY_INSIGHTS__", Path(args.insights).read_text(encoding="utf-8").strip())
    if args.watchlist:
        html = html.replace("__WEEKLY_WATCHLIST__", Path(args.watchlist).read_text(encoding="utf-8").strip())

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")

    # 素材：输出目录下的 assets/ 由调用方准备；若 games.json 内 icon/shots 是远程 URL
    # 或相对路径，仅提示，不做下载（素材落地规则见 references/sources.md）。
    print(f"OK: {len(games)} 款游戏注入模板 → {out} ({out.stat().st_size} 字节)")
    print("提示：请确认输出目录 assets/ 已就绪；灵感总结/观察项两节按周更新内容。")


if __name__ == "__main__":
    main()
