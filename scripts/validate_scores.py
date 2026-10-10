#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""每周榜单调研 · 综合分校验脚本（v13 · 含「愿望单热度」维度，方案 A 权重）

按既定加权公式重算每款游戏的综合分与 IAA 潜力分，并（可选）与输入中的
预期值比对，防止人工打分或写入看板时出错。维度顺序必须与看板 GAMES 数组
及 references/scoring.md 一致：

  DIM_NAMES = [玩法创新性, 核心循环完整度, 美术可复刻性, 技术门槛,
               内容量成本, IAA 改造潜力, IAP 付费友好度, 上手门槛,
               题材市场热度, 竞争烈度, 小团队可借鉴度, 上架合规风险,
               愿望单热度]

公式（方案 A，2026-10-10 确认）：
  综合分 = 玩法创新性×0.18 + 美术可复刻性×0.15 + 技术门槛×0.10
         + (IAA 改造潜力 + IAP 付费友好度)/2 ×0.15
         + 小团队可借鉴度×0.18 + 愿望单热度×0.12
         + 其余 6 维均值×0.12
  IAA 潜力分 = 第 6 维（IAA 改造潜力）

用法：
  python validate_scores.py games.json [--tolerance 0.02]
  games.json: [{"id":"rr","dims":[7,8,8,8,6,9,7,9,8,6,9,10,8],"score":7.97,"iaa":9}, ...]
  --score/--iaa 省略时不比对，仅重算输出。
"""
import json
import sys

WEIGHTS = [0.18, None, 0.15, 0.10, None, 0.075, 0.075, None, None, None, 0.18, None, 0.12]
# WEIGHTS 中 0.075 两项即 IAA/IAP 均值×0.15 的拆分；None 项进入"其余 6 维均值"（权重 0.12）。
IAA_IDX = 5          # 第 6 维：IAA 改造潜力
OTHER_IDX = [1, 4, 7, 8, 9, 11]  # 核心循环完整度、内容量成本、上手门槛、题材热度、竞争烈度、合规
OTHER_W = 0.12       # 其余 6 维均值权重（方案 A）


def compute(dims):
    assert len(dims) == 13, f"dims 必须为 13 项，实际 {len(dims)}"
    for v in dims:
        assert isinstance(v, (int, float)) and 1 <= v <= 10, f"维度分必须在 1-10：{dims}"
    fixed = sum(dims[i] * w for i, w in enumerate(WEIGHTS) if w is not None)
    other = sum(dims[i] for i in OTHER_IDX) / len(OTHER_IDX) * OTHER_W
    return round(fixed + other, 2), dims[IAA_IDX]


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    tol = 0.02
    if "--tolerance" in sys.argv:
        tol = float(sys.argv[sys.argv.index("--tolerance") + 1])
    with open(sys.argv[1], encoding="utf-8") as f:
        games = json.load(f)
    print(f"{'id':<6}{'重算综合':>8}{'预期综合':>9}{'重算IAA':>9}{'预期IAA':>9}  结论")
    fail = 0
    for g in games:
        score, iaa = compute(g["dims"])
        ok = True
        if "score" in g and abs(score - g["score"]) > tol:
            ok = False
        if "iaa" in g and iaa != g["iaa"]:
            ok = False
        exp_s = f"{g.get('score', '-'):>8}" if "score" in g else "       -"
        exp_i = f"{g.get('iaa', '-'):>8}" if "iaa" in g else "       -"
        tag = "PASS" if ok else "FAIL"
        if not ok:
            fail += 1
        print(f"{g['id']:<6}{score:>9.2f}{exp_s}{iaa:>9}{exp_i}  {tag}")
    print(f"\n共 {len(games)} 款，通过 {len(games) - fail}，失败 {fail}")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
