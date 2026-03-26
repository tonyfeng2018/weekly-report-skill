#!/usr/bin/env python3
# fetch_defi_data.py — DefiLlama 链上数据抓取
# 执行时间：每周二 北京时间15:00（UTC 07:00）
# 数据窗口：上上周一 至 上周日（完整自然周）
# 输出：/tmp/defi_data.json

# 踩坑1: 总量必须用全局接口，不能各链求和（漏Others）
# 踩坑2: 周变化不能用change_7dover7d（滚动7天，口径不同）
#   案例：Hyperliquid L1 API=-11.77% vs 自然周=+6.59%
# 踩坑3: 链列表动态筛选TVL>$1B，不能硬编码
# 踩坑4: 全链稳定币总量用/stablecoinchains汇总
#   错误：表格各链加总=$303.37B | 正确：$316.27B（差$13B）
# 踩坑5: 必须用parentProtocol合并子协议
#   错误：Spark子协议各自入选 | 正确：合并后SparkLend=+6.9%，不入选

import urllib.request
import json
import datetime

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

def date_to_ts(d):
    return int(datetime.datetime(d.year, d.month, d.day).timestamp())

def get_window():
    """返回上上周一(w1s)到上周日(w1e) 以及 再前一周(w0s-w0e)"""
    today = datetime.date.today()
    last_mon = today - datetime.timedelta(days=today.weekday() + 7)
    w1s = date_to_ts(last_mon)
    return w1s, w1s + 7 * 86400, w1s - 7 * 86400, w1s, last_mon.strftime("%Y-%m-%d")

# ─── 表格一：各链 DEX 周交易量 ────────────────────────────────
def table1():
    w1s, w1e, w0s, w0e, label = get_window()
    print(f"\n[表格一] 数据窗口：{label} 起的7天")
    CHAINS = ["Ethereum", "Solana", "BSC", "Base", "Hyperliquid L1",
              "Arbitrum", "Polygon", "Sui", "Avalanche", "Tron"]
    res = {}
    for c in CHAINS:
        d = fetch(
            f"https://api.llama.fi/overview/dexs/{c.replace(' ','%20')}"
            f"?excludeTotalDataChart=false&excludeTotalDataChartBreakdown=true"
        )
        chart = d.get("totalDataChart", [])
        w1 = sum(v for ts, v in chart if w1s <= ts < w1e)
        w0 = sum(v for ts, v in chart if w0s <= ts < w0e)
        res[c] = {"w1": w1, "w0": w0, "chg": (w1 - w0) / w0 * 100 if w0 else 0}
        print(f"  {c:<20} ${w1/1e6:>8.0f}M {res[c]['chg']:>+7.2f}%")

    # ⚠️ 踩坑1：全链总量用全局接口
    g = fetch(
        "https://api.llama.fi/overview/dexs"
        "?excludeTotalDataChart=false&excludeTotalDataChartBreakdown=true"
    )
    gc = g.get("totalDataChart", [])
    tw1 = sum(v for ts, v in gc if w1s <= ts < w1e)
    tw0 = sum(v for ts, v in gc if w0s <= ts < w0e)
    res["Others"] = {"w1": tw1 - sum(r["w1"] for r in res.values()), "w0": 0, "chg": 0}
    res["Total"] = {"w1": tw1, "w0": tw0, "chg": (tw1 - tw0) / tw0 * 100 if tw0 else 0}
    print(f"  {'Others':<20} ${res['Others']['w1']/1e6:>8.0f}M")
    print(f"  {'Total':<20} ${tw1/1e6:>8.0f}M {res['Total']['chg']:>+7.2f}%")
    return res, label

# ─── 表格二：各链 TVL + 稳定币 ────────────────────────────────
def table2():
    print("\n[表格二] 各链 TVL + 稳定币")
    # ⚠️ 踩坑3：动态筛选
    chains = fetch("https://api.llama.fi/v2/chains")
    big = sorted([c for c in chains if c.get("tvl", 0) > 1e9],
                 key=lambda x: x["tvl"], reverse=True)
    print(f"  共 {len(big)} 条链 TVL > $1B")
    res = []
    for c in big:
        n = c["name"]
        hist = fetch(f"https://api.llama.fi/v2/historicalChainTvl/{n.replace(' ','%20')}")
        tvl_chg = (hist[-1]["tvl"] - hist[-8]["tvl"]) / hist[-8]["tvl"] * 100 if len(hist) >= 8 else None
        try:
            s = fetch(f"https://stablecoins.llama.fi/stablecoincharts/{n.replace(' ','%20')}")
            def gt(e):
                return sum(v for v in e.get("totalCirculatingUSD", {}).values() if isinstance(v, (int, float)))
            cur_s = gt(s[-1])
            prev_s = gt(s[-8]) if len(s) >= 8 else gt(s[0])
            sc = (cur_s - prev_s) / prev_s * 100 if prev_s else 0
        except:
            cur_s = sc = None
        res.append({"chain": n, "tvl": c["tvl"], "tvl_chg": tvl_chg,
                    "stable": cur_s, "stable_chg": sc})
        tvl_str = f"${c['tvl']/1e9:.2f}B"
        chg_str = f"{tvl_chg:+.2f}%" if tvl_chg is not None else "N/A"
        s_str = f"${cur_s/1e9:.2f}B" if cur_s else "NA"
        print(f"  {n:<20} {tvl_str} {chg_str} | 稳定币 {s_str}")

    # ⚠️ 踩坑4：全链稳定币总量
    all_s = fetch("https://stablecoins.llama.fi/stablecoinchains")
    total_s = sum(
        sum(v for v in c.get("totalCirculatingUSD", {}).values() if isinstance(v, (int, float)))
        for c in all_s
    )
    tvl_h = fetch("https://api.llama.fi/v2/historicalChainTvl")
    g_tvl_chg = (tvl_h[-1]["tvl"] - tvl_h[-8]["tvl"]) / tvl_h[-8]["tvl"] * 100
    sh = fetch("https://stablecoins.llama.fi/stablecoincharts/all")
    def gt2(e):
        return sum(v for v in e.get("totalCirculatingUSD", {}).values() if isinstance(v, (int, float)))
    g_sc = (gt2(sh[-1]) - gt2(sh[-8])) / gt2(sh[-8]) * 100
    summary = {
        "global_tvl": tvl_h[-1]["tvl"],
        "global_tvl_chg": g_tvl_chg,
        "global_stable": total_s,
        "global_stable_chg": g_sc
    }
    print(f"\n  全链 DeFi TVL: ${summary['global_tvl']/1e9:.2f}B ({summary['global_tvl_chg']:+.2f}%)")
    print(f"  全链稳定币:    ${summary['global_stable']/1e9:.2f}B ({summary['global_stable_chg']:+.2f}%)")
    return res, summary

# ─── 表格三：前100协议 7d 涨幅 > 10% ──────────────────────────
def table3():
    print("\n[表格三] 前100协议 7d 涨幅 > 10%（父协议合并后）")
    # ⚠️ 踩坑5：parentProtocol 合并
    protocols = fetch("https://api.llama.fi/protocols")
    CEX = {"CEX", "Exchange", "Centralized Exchange"}
    pm = {}
    for p in protocols:
        if not p.get("tvl") or p["tvl"] <= 0:
            continue
        if p.get("category") in CEX:
            continue
        key = p.get("parentProtocol") or p.get("slug") or p["name"]
        if key not in pm:
            pm[key] = {"name": p["name"], "tvl": 0, "txc": 0, "twc": 0}
        if not p.get("parentProtocol"):
            pm[key]["name"] = p["name"]  # 父协议用自身名称
        pm[key]["tvl"] += p["tvl"]
        chg = p.get("change_7d")
        if chg is not None:
            pm[key]["txc"] += p["tvl"] * chg
            pm[key]["twc"] += p["tvl"]

    merged = [
        {"name": v["name"], "tvl": v["tvl"],
         "chg": v["txc"] / v["twc"] if v["twc"] > 0 else None}
        for v in pm.values()
    ]
    top100 = sorted(merged, key=lambda x: x["tvl"], reverse=True)[:100]
    winners = [
        (i + 1, p["name"], round(p["chg"], 2))
        for i, p in enumerate(top100)
        if p.get("chg") and p["chg"] > 10
    ]
    print(f"  共 {len(winners)} 个项目入选:")
    for rank, name, chg in winners:
        print(f"  #{rank:<3} {name:<30} {chg:>+7.2f}%")
    return winners

# ─── 主程序 ────────────────────────────────────────────────────
if __name__ == "__main__":
    t1, label = table1()
    t2, t2s = table2()
    t3 = table3()
    out = {
        "label": label,
        "table1": t1,
        "table2": t2,
        "table2_summary": t2s,
        "table3": t3
    }
    with open("/tmp/defi_data.json", "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 数据保存 → /tmp/defi_data.json")
