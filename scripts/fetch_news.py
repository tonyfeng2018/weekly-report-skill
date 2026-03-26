#!/usr/bin/env python3
# fetch_news.py — 资讯抓取脚本
# 执行时间：每周二 北京时间15:00（UTC 07:00）
# 时间范围：上周三 00:00 至 本周二 23:59
# 输出：/tmp/news_candidates.json

import urllib.request
import xml.etree.ElementTree as ET
import datetime
import json
import re

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", errors="ignore")

def week_range():
    """返回上周三到本周二的时间范围"""
    today = datetime.date.today()
    days_to_tue = (today.weekday() - 1) % 7
    this_tue = today - datetime.timedelta(days=days_to_tue)
    last_wed = this_tue - datetime.timedelta(days=6)
    return last_wed, this_tue

# ─── ChainFeeds Substack RSS（最高优先级）─────────────────────
def chainfeeds(start, end):
    print("\n[ChainFeeds RSS] 抓取中...")
    xml = fetch("https://chainfeeds.substack.com/feed")
    root = ET.fromstring(xml)
    items = []
    for item in root.findall(".//item"):
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        pub = item.findtext("pubDate", "")[:16]
        try:
            dt = datetime.datetime.strptime(pub, "%a, %d %b %Y").date()
        except:
            dt = datetime.date.today()
        if start <= dt <= end:
            items.append({"title": title, "url": link, "source": "ChainFeeds", "date": str(dt)})
            print(f"  ✅ {dt} | {title[:60]}")
    print(f"  共找到 {len(items)} 篇本周文章")
    return items

# ─── PANews 深度文章 ──────────────────────────────────────────
def panews():
    print("\n[PANews 深度] 抓取中...")
    html = fetch("https://www.panewslab.com/zh/in-depth")
    # 提取所有文章路径
    paths = list(set(re.findall(r'href="(/zh/articles/[a-zA-Z0-9\-]+)"', html)))
    items = []
    for p in paths[:20]:  # 最多抓20篇
        url = f"https://www.panewslab.com{p}"
        c = fetch(url)
        m = re.search(r'<title[^>]*>([^<]+)</title>', c)
        title = re.sub(r'\s*[\|｜].*$', '', m.group(1)).strip() if m else p
        if len(title) > 5:
            items.append({"title": title, "url": url, "source": "PANews", "date": ""})
            print(f"  ✅ {title[:60]}")
    print(f"  共 {len(items)} 篇")
    return items

# ─── Odaily 深度文章 ──────────────────────────────────────────
def odaily():
    print("\n[Odaily 深度] 抓取中...")
    html = fetch("https://www.odaily.news/zh-CN/deep")
    paths = list(set(re.findall(r'href="(/zh-CN/post/\d+)"', html)))
    items = []
    for p in paths[:20]:
        url = f"https://www.odaily.news{p}"
        c = fetch(url)
        m = re.search(r'<title[^>]*>([^<]+)</title>', c)
        title = re.sub(r'\s*[\|｜-].*Odaily.*$', '', m.group(1)).strip() if m else p
        if len(title) > 5:
            items.append({"title": title, "url": url, "source": "Odaily", "date": ""})
            print(f"  ✅ {title[:60]}")
    print(f"  共 {len(items)} 篇")
    return items

# ─── 主程序 ────────────────────────────────────────────────────
if __name__ == "__main__":
    start, end = week_range()
    print(f"时间范围：{start} → {end}")

    all_items = chainfeeds(start, end) + panews() + odaily()

    # 去重
    seen, unique = set(), []
    for i in all_items:
        if i["url"] not in seen:
            seen.add(i["url"])
            unique.append(i)

    with open("/tmp/news_candidates.json", "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)

    print(f"\n✅ {len(unique)} 篇候选 → /tmp/news_candidates.json")
    print("将内容交给 AI 筛选10条，格式见 SKILL.md 2.4 节")
