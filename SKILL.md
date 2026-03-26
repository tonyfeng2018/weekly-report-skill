# Weekly Report Skill — 加密周报自动化系统
> 适用模型：任何支持 web_fetch + Python exec + Google Sheets API 的 AI Agent
> 维护者：Gater (Tony) @tongweb3
> 最后更新：2026-03-26 | v1.1

---

## 一、系统概览

### 产出内容
- **内容一**：每周10条热点资讯（含详细分析摘要）
- **内容二**：链上数据分析报告（三张表格 + 原因分析）

### 执行时间（统一）
**每周二 北京时间 15:00（UTC 07:00）**
1. 抓取 DefiLlama 数据 → 写入 Google Sheet
2. 运行数据分析 → 附加到 Google Sheet
3. 抓取资讯来源 → 生成10条候选
4. 推送完整内容给用户

### 数据时间窗口
- 资讯：上周三 00:00 → 本周二 23:59（7天滚动）
- 链上数据：**上上周一 00:00 → 上周日 23:59（完整自然周）**
  - 示例：4/1（周二）执行 → 链上数据覆盖 3/23–3/29

### Google Sheet 配置
- Sheet ID: `1Iaus-JyVbvdD6CENbG66nOp7vl59pyJL-jvtJwHJL1Q`
- Service Account: `gate-weeklu@gate-weekly.iam.gserviceaccount.com`
- Key文件: `/home/node/.openclaw/workspace/memory/gcp-service-account.json`
- Tab命名规则: `YYYY-MM-DD`（数据周的周一日期）

### GitHub仓库
https://github.com/tonyfeng2018/gater-weekly-report-skill

---

## 二、内容一：每周热点资讯10条

### 2.1 数据来源（按优先级）

| 来源 | URL | 方式 | 状态 |
|---|---|---|---|
| ChainFeeds Substack | https://chainfeeds.substack.com/feed | RSS XML | ✅ 最优先，已聚合多平台 |
| PANews 深度 | https://www.panewslab.com/zh/in-depth | web_fetch列表 | ✅ 稳定 |
| Odaily 深度 | https://www.odaily.news/zh-CN/deep | web_fetch列表 | ✅ 稳定 |
| BlockBeats | 单篇URL直接抓 | web_fetch单篇 | ⚠️ 列表页无效，单篇可用 |
| TechFlow | — | — | ❌ 无法抓取（ChainFeeds已覆盖）|
| ChainFeeds.me | — | — | ❌ 需登录（用Substack代替）|

### 2.2 抓取流程

```python
# Step 1: ChainFeeds RSS（最高优先级）
rss_xml = web_fetch("https://chainfeeds.substack.com/feed")
# 解析 XML <item>，提取 title + link + pubDate，过滤本周内文章

# Step 2: PANews 深度列表
panews_html = web_fetch("https://www.panewslab.com/zh/in-depth")
# 从 HTML 提取文章标题和链接

# Step 3: Odaily 深度列表
odaily_html = web_fetch("https://www.odaily.news/zh-CN/deep")
# 从 HTML 提取文章标题和链接

# Step 4: 逐篇抓取候选正文
for url in candidate_urls:
    content = web_fetch(url)
    # 提取核心观点和数据

# Step 5: 按选题标准筛选，输出10条
```

### 2.3 选题标准（严格遵循）

**✅ 优先选（⭐⭐⭐）**
- 机制拆解型：解释"为什么/底层逻辑"，不是"发生了什么"
- 数据支撑的结构性判断：有具体数字+反共识结论
- 行业结构性转变：行业正在发生的根本性变化及含义

**✅ 可选（⭐⭐）**
- 重要机构/人物的深度观点（有实质判断，不是泛泛表态）
- 新赛道演化与前沿判断（有逻辑框架支撑）

**❌ 明确不选**
- 纯新闻播报（"XX宣布XX"）
- 行情预测/技术分析（"BTC将涨到XX"）
- 价值观/精神叙事类文章
- 单项目功能介绍报告
- 名人泛泛表态（无机制深度）
- 速览/项目列举型（"18个项目速览"）

### 主题覆盖偏好（按优先级）

1. DeFi机制与演化（稳定币/借贷/收益来源）
2. 监管政策与金融权力博弈
3. 机构行为与市场结构
4. AI × Crypto 真实结合点（非叙事炒作）
5. 行业人物深度访谈（有实质认知输出）
6. 新赛道方向（预测市场/RWA/永续合约）

### 2.4 输出格式（每条固定格式）

```
**[序号]. [文章标题]**
来源：[可点击超链接]
**核心机制拆解：[副标题，点明核心判断，10字以内]**
- **[要点1标题]**：详细说明，含具体数据
- **[要点2标题]**：详细说明
- **[要点3标题]**：详细说明
- **[结构性结论/反共识判断]**：...
```

（每条约300-500字，重要数据加粗）

### 2.5 已知问题与修复记录

| 问题 | 修复方案 |
|---|---|
| ChainFeeds.me 需登录 | 改用 chainfeeds.substack.com/feed（RSS免登录） |
| TechFlow 无法抓取 | ChainFeeds RSS 已聚合 TechFlow，无需单独抓 |
| BlockBeats 列表只返回1条 | 有具体URL时单篇抓取，否则跳过 |
| 最初只输出5条 | 已改为每周10条，用户自行审核定稿 |

---

## 三、内容二：链上数据抓取

### 3.1 Google Sheet 配置

```python
SHEET_ID = "1Iaus-JyVbvdD6CENbG66nOp7vl59pyJL-jvtJwHJL1Q"
SERVICE_ACCOUNT_KEY = "/home/node/.openclaw/workspace/memory/gcp-service-account.json"
# Service Account Email: gate-weeklu@gate-weekly.iam.gserviceaccount.com

import gspread
from google.oauth2.service_account import Credentials
SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_KEY, scopes=SCOPES)
gc = gspread.authorize(creds)
sh = gc.open_by_key(SHEET_ID)
ws = sh.add_worksheet(title="YYYY-MM-DD", rows=50, cols=10)
```

### 3.2 表格一：各链 DEX 周交易量

固定链列表（10条）：Ethereum, Solana, BSC, Base, Hyperliquid L1, Arbitrum, Polygon, Sui, Avalanche, Tron

```python
import datetime, urllib.request, json

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def date_to_ts(y, m, d):
    return int(datetime.datetime(y, m, d).timestamp())

# 自动计算数据窗口（执行日的上上周一到上周日）
today = datetime.date.today()
last_monday = today - datetime.timedelta(days=today.weekday() + 7)
w1s = date_to_ts(last_monday.year, last_monday.month, last_monday.day)
w1e = w1s + 7 * 86400
w0s = w1s - 7 * 86400
w0e = w1s

chains = ["Ethereum","Solana","BSC","Base","Hyperliquid L1","Arbitrum","Polygon","Sui","Avalanche","Tron"]
results = {}
for chain in chains:
    url = f"https://api.llama.fi/overview/dexs/{chain.replace(' ','%20')}?excludeTotalDataChart=false&excludeTotalDataChartBreakdown=true"
    d = fetch(url)
    chart = d.get("totalDataChart", [])
    w1 = sum(v for ts, v in chart if w1s <= ts < w1e)
    w0 = sum(v for ts, v in chart if w0s <= ts < w0e)
    chg = (w1 - w0) / w0 * 100 if w0 else 0
    results[chain] = {"w1": w1, "w0": w0, "chg": chg}

# ⚠️ 关键：全链总量用全局 totalDataChart，不能各链求和（会漏 Others）
global_d = fetch("https://api.llama.fi/overview/dexs?excludeTotalDataChart=false&excludeTotalDataChartBreakdown=true")
global_chart = global_d.get("totalDataChart", [])
total_w1 = sum(v for ts, v in global_chart if w1s <= ts < w1e)
total_w0 = sum(v for ts, v in global_chart if w0s <= ts < w0e)
named_w1 = sum(r["w1"] for r in results.values())
others_w1 = total_w1 - named_w1
total_chg = (total_w1 - total_w0) / total_w0 * 100 if total_w0 else 0
```

**⚠️ 关键规则：**
- 周变化必须用自然周时间戳汇总，不能用 `change_7dover7d`（滚动7天，口径不同，数值会差异很大）
- Others = 全局Total - 10条链之和

### 3.3 表格二：各链 TVL + 稳定币

```python
# 链列表：动态筛选 TVL > $1B（不要硬编码！）
chains_data = fetch("https://api.llama.fi/v2/chains")
big_chains = sorted(
    [c for c in chains_data if c.get("tvl", 0) > 1e9],
    key=lambda x: x["tvl"], reverse=True
)

for chain in big_chains:
    name = chain["name"]
    
    # TVL 7d变化
    hist = fetch(f"https://api.llama.fi/v2/historicalChainTvl/{name.replace(' ','%20')}")
    cur_tvl = hist[-1]["tvl"]
    prev_tvl = hist[-8]["tvl"] if len(hist) >= 8 else hist[0]["tvl"]
    tvl_chg = (cur_tvl - prev_tvl) / prev_tvl * 100
    
    # 稳定币当前值 + 7d变化
    try:
        stbl = fetch(f"https://stablecoins.llama.fi/stablecoincharts/{name.replace(' ','%20')}")
        def get_total(entry):
            return sum(v for v in entry.get("totalCirculatingUSD", {}).values() if isinstance(v, (int, float)))
        cur_s = get_total(stbl[-1])
        prev_s = get_total(stbl[-8]) if len(stbl) >= 8 else get_total(stbl[0])
        stable_chg = (cur_s - prev_s) / prev_s * 100 if prev_s else 0
    except:
        cur_s, stable_chg = None, None  # Bitcoin 等无稳定币数据填 NA

# ⚠️ 关键：全链稳定币总量必须用 /stablecoinchains 所有链求和
# 不能只加表格中的链 → 会漏掉小链，导致偏低约 $13B（如 $303B vs 正确的 $316B）
all_chains_stable = fetch("https://stablecoins.llama.fi/stablecoinchains")
total_stable = sum(
    sum(v for v in c.get("totalCirculatingUSD", {}).values() if isinstance(v, (int, float)))
    for c in all_chains_stable
)

# 全链 DeFi TVL 7d变化
tvl_hist = fetch("https://api.llama.fi/v2/historicalChainTvl")
global_tvl_chg = (tvl_hist[-1]["tvl"] - tvl_hist[-8]["tvl"]) / tvl_hist[-8]["tvl"] * 100

# 全链稳定币 7d变化
all_stable_hist = fetch("https://stablecoins.llama.fi/stablecoincharts/all")
def get_t(e): return sum(v for v in e.get("totalCirculatingUSD",{}).values() if isinstance(v,(int,float)))
global_stable_chg = (get_t(all_stable_hist[-1]) - get_t(all_stable_hist[-8])) / get_t(all_stable_hist[-8]) * 100
```

**⚠️ 关键规则：**
- 链列表动态筛选 TVL > $1B，每周可能有新增或移除的链
- Bitcoin 无稳定币数据，填 NA，不报错退出
- 全链稳定币标题行要同时显示：金额 + 周变化率

### 3.4 表格三：前100协议 7d TVL 涨幅 > 10%

```python
protocols = fetch("https://api.llama.fi/protocols")

# ⚠️ 关键：必须用父协议合并逻辑（否则子协议单独计算会入选，父协议可能不达标）
# 反例：Spark Liquidity Layer +14.65% / Spark Savings +10.80% 各自入选
# 正确：合并为 SparkLend 父协议后 7d 只有 +6.9%，不入选

CEX_CATS = {"CEX", "Exchange", "Centralized Exchange"}
parent_map = {}
for p in protocols:
    if not p.get("tvl") or p["tvl"] <= 0:
        continue
    if p.get("category") in CEX_CATS:
        continue
    key = p.get("parentProtocol") or p.get("slug") or p["name"]
    if key not in parent_map:
        parent_map[key] = {"name": p["name"], "tvl": 0, "tvl_x_chg": 0, "tvl_with_chg": 0}
    if not p.get("parentProtocol"):
        parent_map[key]["name"] = p["name"]  # 父协议用自身名称
    parent_map[key]["tvl"] += p["tvl"]
    chg = p.get("change_7d")
    if chg is not None:
        parent_map[key]["tvl_x_chg"] += p["tvl"] * chg
        parent_map[key]["tvl_with_chg"] += p["tvl"]

# 计算加权平均 7d change
merged = []
for key, info in parent_map.items():
    chg = info["tvl_x_chg"] / info["tvl_with_chg"] if info["tvl_with_chg"] > 0 else None
    merged.append({"name": info["name"], "tvl": info["tvl"], "change_7d": chg})

# 排序取前100，筛选 7d > 10%
top100 = sorted(merged, key=lambda x: x["tvl"], reverse=True)[:100]
winners = [
    (i+1, p["name"], round(p["change_7d"], 2))
    for i, p in enumerate(top100)
    if p.get("change_7d") and p["change_7d"] > 10
]
```

**⚠️ 关键规则：**
- 必须用 parentProtocol 字段合并，否则数据与网站不一致
- API change_7d 是滚动7天，网站显示是日历周，以 API 为准（用户已确认）
- CEX 必须排除

---

## 四、链上数据分析框架

数据写入 Sheet 后，按以下框架逐表分析，每个判断必须附来源链接且为本周内近期事件。

### 4.1 表格一分析框架（DEX交易量）

**Step 1：整体行情一句话总结**（本周 vs 上周变化 + 主要驱动/拖累方向）

**Step 2：增长链（> +4%）逐链分析，最多3条**

```
链增长 → 哪个协议占比最高且增长最多
 → 该协议日交易量走势（什么时间点放量）
 → 主要交易什么代币对（用 DexScreener API 查）
 → 该代币为何这周交易量高（找近期事件/公告）
 → 附链接
```

**Step 3：下降链（< -4%）逐链分析，最多3条**（同上反向逻辑）

**⚠️ 异常代币识别（传销/刷量判断标准）：**
- 卖单笔数 / 买单笔数 > 3 且无官网无社交媒体 → 传销嫌疑
- FDV / 市值比 > 5 → 代币结构异常
- 标注："不具有机含量，Quickswap/链交易量虚高"
- 案例：LGNS (Longinus) —— 24h卖单718,762次 vs 买单183,315次，FDV $9.58B vs 市值 $1.02B

**DexScreener API（查代币详情，无需登录）：**
```
https://api.dexscreener.com/latest/dex/search?q={代币名或合约地址}
```
注意：dexscreener.com 主页403，必须用 api.dexscreener.com

### 4.2 表格二分析框架（TVL + 稳定币）

**Step 1：整体总结**
- 全链 TVL + 稳定币变化幅度
- 是否有新增或消失的链（TVL > $1B 门槛变化）

**Step 2：TVL 增长链（> +4%）分析**

```
哪条链增长 → 哪个协议 TVL 最高且增长最多
 → 打开 defillama.com/protocol/tvl/{slug} 查 Token Breakdown
 → 哪条链的哪个代币余额增长了
 → 找该代币/协议本周内的事件（官方博客/公告）
 → 附链接（必须是本周内）
```

**Step 3：稳定币变化分析（单独列出异动链）**

**⚠️ 特殊案例记录：**
- Bitcoin TVL 剧烈波动 → 全部来自 Babylon Protocol，需说明 BTC 价格影响
- 全链稳定币标题 = /stablecoinchains 汇总，不是表格各行加总

### 4.3 表格三分析框架（前100协议涨幅榜）

**Step 1：整体总结**（几个项目入选 + 赛道分布 + 本周主题判断）

**Step 2：逐项目分析（按赛道分组）**

每个项目固定三步：
1. **链/代币**：TVL 在哪条链？增长的是哪个代币？
   → 看 defillama.com/protocol/tvl/{slug} 的 Token Breakdown 图
   → 关注突然的单日跳升（可能是单笔大额，非有机增长）
2. **时间点**：什么时候开始增长？多少天？
   → 看 TVL 历史折线图
3. **原因**：本周内（7天以内）的事件
   → 查顺序：官方博客 > Medium > DefiLlama Hallmarks > Twitter
   → 必须附链接，无法确认则标注"待确认，建议人工查 @xxx Twitter"

**按赛道分组输出参考：**
- Restaking 赛道（Babylon, Mellow, EigenLayer等）
- RWA 赛道（Centrifuge, Anemoy, Ondo等）
- 借贷赛道（Dolomite, Aave, Morpho等）
- Yield 策略赛道（CIAN, Pendle等）
- DEX/流动性赛道

**⚠️ 单日 TVL 跳升判断规则：**
- 单日增幅 > 总 TVL 的 20% → 高度疑似单笔大额存款
- 案例：Dolomite 3/25 单日 $285M → $411M（+44%），驱动代币为 WLFI（特朗普家族DeFi代币）

---

## 五、已知限制与解决方案

| 限制 | 解决方案 |
|---|---|
| 无 Brave Search API Key | 直接访问官方博客/Medium；用 ChainFeeds RSS 获取事件线索 |
| DexScreener 主页 403 | 用 api.dexscreener.com/latest/dex/search?q=xxx API |
| Twitter/X 无法抓取 | 标注"待确认，建议人工查 @xxx" |
| DefiLlama 协议页 403 | 用 /protocol/{slug} API 端点替代 |
| Odaily/PANews 搜索页无内容 | 直接访问深度文章列表页，不用搜索 |
| 全链稳定币总量偏低 | 用 /stablecoinchains 汇总（不加表格各行） |
| API change_7d vs 网站不同 | API 是滚动7天，用 API 为准，备注说明 |
| 子协议被拆分导致重复入选 | 用 parentProtocol 合并 |
| write/exec 工具 bug（OpenClaw特有） | 用 Python 脚本通过 heredoc 写入，或 GitHub 托管 |

---

## 六、Google Sheet 格式规范

```python
# 标题行（深色）
header_fmt = {
    "backgroundColor": {"red": 0.1, "green": 0.1, "blue": 0.18},
    "textFormat": {"foregroundColor": {"red":1,"green":1,"blue":1}, "bold": True, "fontSize": 11}
}
# 表头行（次深色）
subheader_fmt = {
    "backgroundColor": {"red": 0.09, "green": 0.13, "blue": 0.24},
    "textFormat": {"foregroundColor": {"red":0.88,"green":0.88,"blue":0.88}, "bold": True, "fontSize": 10}
}
# 列宽
col_widths = {"A": 200, "B": 110, "C": 110, "D": 110, "E": 110, "F": 110}
```

---

## 七、运行方式

```bash
# Step 1: 抓链上数据
python3 scripts/fetch_defi_data.py

# Step 2: 写入Google Sheet
python3 scripts/write_sheet.py

# Step 3: 抓资讯候选
python3 scripts/fetch_news.py
# 输出 → /tmp/news_candidates.json
# 把内容交给 AI 筛选10条

# 依赖安装
pip install gspread google-auth
```

---

## 八、参考案例（2026-03-26 实际执行结果）

### 表格一（3/16-3/22）

- **Total**: $47.91B（-0.72%）
- **增长：Tron +43%**（SUNSwap V3 占95%，稳定币兑换需求）
- **增长：Polygon +14%**（Polymarket 57% + LGNS传销刷量）
- **增长：Hyperliquid L1 +6.59%**（Project X 激励活动）
- **下降：Sui -33%**（Meme热度退潮，全链DEX -45-52%）
- **下降：Avalanche -9%**（Pharaoh/Blackhole LP撤出 $4.5M）
- **下降：Ethereum -7%**（ETH Restaking协议集体收缩）

### 表格二（截至3/26）

- **全链DeFi TVL**: $96.62B（-0.18%）
- **全链稳定币**: $316.27B（+0.02%）
- **异动：Bitcoin +53%**（Babylon Protocol + Ledger集成事件）

### 表格三（6项入选）

| 排名 | 项目 | 赛道 | 7d涨幅 |
|---|---|---|---|
| #16 | Babylon Protocol | Restaking | +85.66% |
| #41 | Centrifuge Protocol | RWA | +11.81% |
| #54 | Anemoy Capital | RWA | +20.31% |
| #86 | Dolomite | 借贷 | +40.53% |
| #88 | CIAN Yield Layer | Yield策略 | +13.48% |
| #89 | Mellow Core | LRT/Restaking | +17.21% |
