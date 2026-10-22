# 交付：交互看板 + 分享文档（阶段 5 用）

## 一、交互看板（左列表右详情 + 汇总卡片页 + 图表 + 真实截图）

### 1. 模板与构建脚本（布局一致的强制入口）

- **布局模板固定为仓库 `templates/dashboard-template.html`，每周只跑构建脚本注入数据，禁止手改 CSS/JS 壳**，保证每周看板布局一致（历史教训：自研卡片式布局被质疑与上期不一致）。
- 构建命令（用法示例）：
  ```
  python scripts/build_dashboard.py <games.json> <输出.html> -t "YYYY-MM-DD" -d <发布目录> [--insights <本周灵感总结片段.html>] [--watchlist <本周观察项片段.html>]
  ```
  - 数据源 `games.json` 结构：`[{id, rank, zh, en, dev, pub, platform, platformLabel, launch, type, rankNow, rankBest, downloads, revenue, rating, intro, monet, score, iaa, dims[13], reasons[13], wishlist, wishlistNote, oneLiner, coreLoop, selling, resources, monetDetail, good[], bad[], tips[], notes[], urls[], icon, shots[]}]`；维度顺序见 `references/scoring.md`。
  - 构建脚本按发布目录 `assets/` 实存自动清空 `icon`/`shots`：缺素材渲染渐变字块（不发 `<img>` 请求，避免 404 与控制台报错），并生成静态预载块（静态扫描只认 `<img src>`，JS 拼接路径会漏传裂图）。
  - 每周内容注入：`--insights`/`--watchlist` 传 HTML 片段（含 h3 小节），替换模板占位符 `__WEEKLY_INSIGHTS__` / `__WEEKLY_WATCHLIST__`。
  - 图标/截图存放：`assets/<游戏id>_icon.<ext>`、`assets/<游戏id>_shotN.<ext>`。
- 看板功能基线：汇总看板（指标卡 + 4 张 ECharts：综合分排行横条/潜力定位象限散点/平台构成环形/13 维均值横条 + 速览卡片墙（含愿望单热度列） + 灵感总结 + 观察项）+ 游戏图鉴（左列表 + 右详情 hero/画廊/基础信息（含愿望单字段）/13 维条形图/雷达图 + 评分表/深度分析 8 节/来源）。

### 2. 手机竖屏适配（必须保留）

- `@media (max-width:640px)` 断点包：`.detail-wrap` 改 `flex-direction:column`；`.list-col` 改 `position:static` + `#game-list` 横向滑动条（`display:flex;overflow-x:auto`，卡片 `min-width:196px`）；`.detail-col`、容器、字号、卡片紧凑化；画廊截图 72% 宽；评分表 11.5px。
- JS：`route()` 在 `window.innerWidth<=640` 且切到详情视图时 `window.scrollTo(0,0)`，避免切游戏停在半截。

### 3. 自检与交付（通用，不依赖特定宿主）

- **自检**（三选一或组合，任选环境可用的方式）：
  1. 无头浏览器截图：用环境中可用的无头浏览器（Playwright / Puppeteer / 等价工具）打开 HTML，分别以 desktop 与 ≤640px 视口截图，核对布局与内容；
  2. 浏览器打开核对：直接打开 HTML，检查控制台报错（consoleErrors）、资源 404（resourceErrors）、横向溢出（horizontalOverflow）是否为空；
  3. 静态检查：确认全部素材以 `<img src="assets/...">` 静态引用且文件实际存在；`__GAMES_DATA__` / `__WEEK_LABEL__` / `__PRELOAD_IMGS__` 必须全部替换为实际内容；`__WEEKLY_INSIGHTS__` / `__WEEKLY_WATCHLIST__` 仅在未提供对应 `--insights`/`--watchlist` 参数时保留（属正常），交付前确认已注入或确认可接受。
- **交付形态**：看板为自包含单文件 HTML + `assets/` 目录（相对路径引用）。交付本地文件路径，或上传任意静态托管（GitHub Pages / Netlify / 内部文件服务等）后给线上链接；托管时发布目录只保留 HTML + assets。
- **素材预载**：`</body>` 前保留模板生成的 hidden `<img src="assets/...">` 预载块，防止动态路径漏图。

## 二、分享文档（可选，载体自选）

- 生成轻量分享入口（看板链接 + Top5 速览 + 讨论问题 + 数据口径声明），载体可用 Markdown / HTML / 环境提供的文档工具。
- 建议命名：`游戏周榜观察 · YYYY-MM-DD（交互看板分享）`。
- 建议结构：
  1. 目的 + 核心结论（blockquote）
  2. 交互看板入口链接（唯一入口，配一句说明）
  3. Top5 速览表
  4. 3-4 个讨论问题（抛给团队讨论）
  5. 数据口径表（时间窗口 / 环比待核实 / 下载收入估算 / 评分快照 / 愿望单估算口径 / 打分主观性）

## 三、每周收尾清单

- [ ] 三处数据一致：看板 GAMES / 数据源报告 / 分享文档（并排核对关键数字，含愿望单口径）
- [ ] validate_scores.py 全 PASS（13 维，方案 A）
- [ ] 看板自检通过：无控制台报错 / 无资源 404 / 手机竖屏布局正常
- [ ] 素材全部静态引用且文件就绪（缺失项已回退字块并确认可接受）
- [ ] 看板文件/链接与分享文档已同步交付（文档内为最新链接）
