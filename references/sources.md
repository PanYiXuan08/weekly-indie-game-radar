# 数据源与榜单定位（阶段 1 用）

## 三平台榜单入口与判定

| 平台 | 榜单 | 入口/工具 |
|---|---|---|
| Google Play（美区为主） | 热门免费榜前 50 / 畅销榜前 100 / 新品榜 | `https://play.google.com/store/apps/collection/topselling_free`（+ `topgrossing` / 新品集合）；商店页加 `&hl=en_US` |
| Google Play · 7 日热度 | Movers / New Releases | querygame（搜索「querygame google play movers」）——「7 日热度 +N%」排行，用于判定新进榜 |
| App Store | 美区 + 中区：免费榜前 50 / 付费榜前 30 / 畅销榜前 100 / New Apps | `https://apps.apple.com/us/charts/iphone`（+ `/top-paid` `/top-grossing` `/new-apps`；中区把 `us` 换 `cn`） |
| Steam | 新品热销前 40 / 热门新品 / 好评上升 | `https://store.steampowered.com/search/?filter=popularnew` 等；用商店页或 appdetails API |

判定「新进榜」的三种证据（无上周快照时环比一律标「待核实」，禁止编造）：
1. 平台「新品/New」标记（GP new 标记、iOS New Apps、Steam 本周新发售）；
2. 7 日热度显著上升（querygame Movers 榜上有名，如 +200% 以上）；
3. 上架日期落在本周窗口内（以上架日期为硬证据，早于窗口即排除，如 3 个月以上老游戏）。

## 官方 API 核验（关键数字必须抽查）

- **Steam 评论（好评率/评论数）**：`https://store.steampowered.com/appreviews/<appid>?json=1&language=schinese&purchase_type=all`
  - 返回 `query_summary.total_positive / total_reviews`，好评率 = positive/reviews，可精确到小数点后一位。
- **Steam 应用信息（上架日期/价格/开发商）**：`https://store.steampowered.com/api/appdetails?appids=<appid>&l=schinese`
  - 用 web_fetch 可达；浏览器内 `bu.http_get` 对 Steam 易超时，改 web_fetch。
- **iOS（上架日期/评分/评论数）**：`https://itunes.apple.com/lookup?id=<苹果AppID>`
  - 注意 iTunes `search` 接口受 robots 限制，用 `lookup`；返回 `releaseDate / averageUserRating / userRatingCount`。
- **Google Play（评分/评论数）**：商店页解析（页面含评分与评论数；AppBrain 可查安装量区间）。

## 商店页素材抓取定位（可复用，实测有效）

- **GP 包名 → 详情页**：`https://play.google.com/store/apps/details?id=<package>&hl=en_US`。
- GP 页内截图 img 类名：`T75of B5GQxf`；图标类名：`T75of Q3MhI` / `nm4vBd`。
- GP 图片 URL 处理：按 `=` 截断后拼 `=w800-h450-rw`（截图）/ `=w512-h512-rw`（图标），存 webp。
- **Steam 截图直链**：`shared.akamai.steamstatic.com` 域，header 图 460x215（`header.jpg`）、截图 1920x1080（`ss_*.jpg`）；可浏览器下载。
- 素材落地规则：图标 + 每款 1-4 张截图（尽量含一张竖版 9:16 手机截图，看板画廊用 `object-fit:contain` 防裁切）；命名 `<游戏id>_icon.<ext>`、`<游戏id>_shotN.<ext>`。

## 已知可复用包名/AppID（2026-10 首期实测）

- GP：`com.nebula.rotaterings` / `com.agavegames.wordtiles` / `com.noodlecake.flickshotrogues` / `findy.search.hidden.object` / `com.cscmobi.livestream.idle.clicker` / `com.flow.smashparty` / `com.Bureau81.OPERATOR`
- Steam：4019220（针影裁梦）/ 1478500（大走）/ 4001890（渔力全开）

## 口碑关键词抓取

- 商店页评论（好评/差评各若干条）实际抓取后提炼 5-8 条好评关键词 + 3-5 条差评关键词；禁止凭印象编造。
- 排除刷榜痕迹：评论集中发布、内容雷同、评分与评论数不匹配的产品。
