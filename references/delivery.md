# 交付：交互看板 + 飞书分享文档（阶段 5 用）

## 一、交互看板（左列表右详情 + 汇总卡片页 + 图表 + 真实截图）

### 1. 模板与构建脚本（布局一致的强制入口）
- **布局模板固定为仓库 `templates/dashboard-template.html`，每周只跑构建脚本注入数据，禁止手改 CSS/JS 壳**，保证每周看板布局一致（2026-10 用户明确要求，历史教训：自研卡片式布局被质疑与上期不一致）。
- 构建命令（用法示例）：
  ```
  python3 scripts/build_dashboard.py <games.json> <输出.html> -t "YYYY-MM-DD" -d <发布目录> [--insights <本周灵感总结片段.html>] [--watchlist <本周观察项片段.html>]
  ```
  - 数据源 `games.json` 结构：`[{id, rank, zh, en, dev, pub, platform, platformLabel, launch, type, rankNow, rankBest, downloads, revenue, rating, intro, monet, score, iaa, dims[13], reasons[13], wishlist, wishlistNote, oneLiner, coreLoop, selling, resources, monetDetail, good[], bad[], tips[], notes[], urls[], icon, shots[]}]`；维度顺序见 `scoring.md`。
  - 构建脚本按发布目录 `assets/` 实存自动清空 `icon`/`shots`：缺素材渲染渐变字块（不发 `<img>` 请求，避免 404 与 consoleErrors），并生成静态预载块（发布链路静态扫描只认 `<img src>`，JS 拼接路径会漏传裂图）。
  - 每周内容注入：`--insights`/`--watchlist` 传 HTML 片段（含 h3 小节），替换模板占位符 `__WEEKLY_INSIGHTS__` / `__WEEKLY_WATCHLIST__`。
  - 图标/截图存放：`assets/<游戏id>_icon.<ext>`、`assets/<游戏id>_shotN.<ext>`。
- 看板功能基线：汇总看板（指标卡 + 4 张 ECharts：综合分排行横条/潜力定位象限散点/平台构成环形/13 维均值横条 + 速览卡片墙（含愿望单热度列） + 灵感总结 + 观察项）+ 游戏图鉴（左列表 + 右详情 hero/画廊/基础信息（含愿望单字段）/13 维条形图/雷达图 + 评分表/深度分析 9 节/来源）。
- 首个规范样例（首期 2026-10 交付物，路径可能随迁移变化）：`E:\doubao\IAA\周榜游戏交互看板\游戏周榜观察看板.html`。

### 2. 手机竖屏适配（必须保留）
- `@media (max-width:640px)` 断点包：`.detail-wrap` 改 `flex-direction:column`；`.list-col` 改 `position:static` + `#game-list` 横向滑动条（`display:flex;overflow-x:auto`，卡片 `min-width:196px`）；`.detail-col`、容器、字号、卡片紧凑化；画廊截图 72% 宽；评分表 11.5px。
- JS：`route()` 在 `window.innerWidth<=640` 且切到详情视图时 `window.scrollTo(0,0)`，避免切游戏停在半截。

### 3. 发布链路（lark-apps，坑已踩平）
- 发布前发布目录**只保留 html + assets**：自检脚本重建的 `_shots\`（中文文件名）会触发服务端 `upload_compiled_artifact` 失败（Succeed 49-53/57、error step=依赖安装），必须移出到过程目录。
- 自检：html skill 的 `scripts/shot.py <html路径>`（仅此一种校验方式），检查 desktop + mobile 全页截图、`consoleErrors`/`horizontalOverflow`/`resourceErrors` 为空；跑完必移走重建的 `_shots`。
- 发布：`lark-cli apps +deploy --dir ./周榜游戏交互看板 --entry-file 周榜游戏观察看板.html --app-id app_xxx`（**复用既有 app_id**，路径只收相对 cwd）；PowerShell 下 stdout 被当 RemoteException 走 stderr，用 `*> 输出文件` 重定向再读；`+release-get --app-id ... --release-id ...` 轮询到 `status=finished` 才拿 `online_url`。
- 应用命名：用 `lark-cli apps +create --name 游戏周榜观察 --app-type html` 建应用再发布；改名需新建应用。

### 4. 素材预载技巧
- `</body>` 前加 hidden `<img src="assets/...">` 预载块，列出全部素材，防发布链路静态扫描漏图导致 JS 动态路径裂图。

## 二、飞书分享文档（lark-doc 工作流）

- 按 lark-doc skill 的创建/更新工作流执行（personal_style.py 读用户风格 → init-draft → 生成 XML → parse 校验 → create → fetch 回查）。
- 文档标题规范：`游戏周榜观察 · YYYY-MM-DD（交互看板分享）`。
- 文档结构（轻量分享入口版，实测可用）：
  1. 目的 + 核心结论（blockquote）
  2. 交互看板入口链接（唯一入口，配一句说明）
  3. Top5 速览表
  4. 4 个讨论问题（抛给同事讨论）
  5. 数据口径表（时间窗口 / 环比待核实 / 下载收入估算 / 评分快照 / 愿望单估算口径 / 打分主观性）
- Windows 已知坑：`+update` 的 `str_replace` 改不了 href（degrade_code=1011）；内联中文 `--content` 报 degrade_code=3001，须把内容写文件用 `--content "@./relative.xml"` 传入（block_replace 单段替换可行）。

## 三、每周收尾清单

- [ ] 三处数据一致：看板 GAMES / 数据源报告 / 飞书文档（并排核对关键数字，含愿望单口径）
- [ ] validate_scores.py 全 PASS（13 维，方案 A）
- [ ] 看板 shot.py 自检通过且 _shots 已移出发布目录
- [ ] 发布轮询到 finished，用 web_fetch 抽查线上标题
- [ ] 文档 URL 与看板 URL 已同步（文档内为最新链接）
- [ ] present_files 交付看板链接 / 文档链接 / 本地报告，最终回复 ≤300 字/8 行
