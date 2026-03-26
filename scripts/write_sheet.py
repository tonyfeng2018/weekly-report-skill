#!/usr/bin/env python3
# write_sheet.py — 将 fetch_defi_data.py 的结果写入 Google Sheet
# 依赖：pip install gspread google-auth

import json
import os
import gspread
from google.oauth2.service_account import Credentials
import time

# ─── 配置 ─────────────────────────────────────────────────────
SHEET_ID = "1Iaus-JyVbvdD6CENbG66nOp7vl59pyJL-jvtJwHJL1Q"
KEY_FILE = os.environ.get(
    "GCP_KEY_PATH",
    "/Users/tonyclaw/.openclaw/workspace/memory/gcp-service-account.json"
)
SCOPES = ["https://spreadsheets.google.com/feeds",
          "https://www.googleapis.com/auth/drive"]
DATA_FILE = "/tmp/defi_data.json"

# ─── 颜色定义 ─────────────────────────────────────────────────
DARK  = {"red": 0.10, "green": 0.10, "blue": 0.18}
MID   = {"red": 0.09, "green": 0.13, "blue": 0.24}
WHITE = {"red": 1.0,  "green": 1.0,  "blue": 1.0}
LGRAY = {"red": 0.88, "green": 0.88, "blue": 0.88}

def fmt(bg, fg, bold=True, size=11):
    return {"backgroundColor": bg,
            "textFormat": {"foregroundColor": fg, "bold": bold, "fontSize": size}}

def connect():
    creds = Credentials.from_service_account_file(KEY_FILE, scopes=SCOPES)
    return gspread.authorize(creds).open_by_key(SHEET_ID)

def write_sheet(data):
    sh = connect()
    label = data["label"]  # YYYY-MM-DD

    # 新建 tab（若已存在则删除重建）
    try:
        ws = sh.worksheet(label)
        sh.del_worksheet(ws)
    except:
        pass
    ws = sh.add_worksheet(title=label, rows=60, cols=10)
    print(f"✅ 已创建 Sheet tab: {label}")

    rows = []

    # ── 表格一 ──────────────────────────────────────────────
    t1 = data["table1"]
    rows.append(["表格一：各链周DEX交易量", "", "", ""])
    rows.append(["链", "本周交易量", "上周交易量", "周变化"])
    for c in ["Solana", "Ethereum", "BSC", "Base", "Hyperliquid L1",
              "Arbitrum", "Polygon", "Sui", "Avalanche", "Tron", "Others", "Total"]:
        if c not in t1:
            continue
        r = t1[c]
        rows.append([
            c,
            f"${r['w1']/1e6:.0f}M" if r['w1'] else "-",
            f"${r['w0']/1e6:.0f}M" if r['w0'] else "-",
            f"{r['chg']:+.2f}%" if r['chg'] else "-"
        ])
    rows.append(["", "", "", ""])  # 空行

    # ── 表格二 ──────────────────────────────────────────────
    t2 = data["table2"]
    s = data["table2_summary"]
    title2 = (f"表格二：各链DeFi TVL+稳定币 "
              f"全链TVL:${s['global_tvl']/1e9:.2f}B({s['global_tvl_chg']:+.2f}%) "
              f"全链稳定币:${s['global_stable']/1e9:.2f}B({s['global_stable_chg']:+.2f}%)")
    rows.append([title2, "", "", "", "", ""])
    rows.append(["链", "DeFi TVL", "TVL周变化", "稳定币", "稳定币周变化", "稳定币占比"])
    for r in t2:
        rows.append([
            r["chain"],
            f"${r['tvl']/1e6:.0f}M",
            f"{r['tvl_chg']:+.2f}%" if r["tvl_chg"] is not None else "N/A",
            f"${r['stable']/1e6:.0f}M" if r["stable"] else "NA",
            f"{r['stable_chg']:+.2f}%" if r["stable_chg"] is not None else "NA",
            f"{r['stable']/s['global_stable']*100:.2f}%" if r["stable"] else "NA"
        ])
    rows.append(["", "", "", "", "", ""])  # 空行

    # ── 表格三 ──────────────────────────────────────────────
    t3 = data["table3"]
    rows.append(["表格三：前100协议7d涨幅>10%（父协议合并后）", "", ""])
    rows.append(["排名", "项目", "7d涨幅"])
    for rank, name, chg in t3:
        rows.append([rank, name, f"+{chg}%"])

    # ── 批量写入 ────────────────────────────────────────────
    ws.update(values=rows, range_name=f"A1:F{len(rows)}")
    print(f"✅ 写入 {len(rows)} 行数据")
    time.sleep(1)

    # ── 格式化 ──────────────────────────────────────────────
    t2r = 3 + 12 + 1  # 表格一数据行 + 空行
    t3r = t2r + 2 + len(t2) + 1  # 表格二数据行 + 空行

    ws.batch_format([
        {"range": "A1:D1", "format": fmt(DARK, WHITE)},
        {"range": "A2:D2", "format": fmt(MID, LGRAY)},
        {"range": f"A{t2r}:F{t2r}", "format": fmt(DARK, WHITE, size=10)},
        {"range": f"A{t2r+1}:F{t2r+1}", "format": fmt(MID, LGRAY)},
        {"range": f"A{t3r}:C{t3r}", "format": fmt(DARK, WHITE)},
        {"range": f"A{t3r+1}:C{t3r+1}", "format": fmt(MID, LGRAY)},
    ])

    # 设置列宽
    sh.batch_update({"requests": [
        {"updateDimensionProperties": {
            "range": {"sheetId": ws.id, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 1},
            "properties": {"pixelSize": 200}, "fields": "pixelSize"
        }},
        {"updateDimensionProperties": {
            "range": {"sheetId": ws.id, "dimension": "COLUMNS", "startIndex": 1, "endIndex": 6},
            "properties": {"pixelSize": 110}, "fields": "pixelSize"
        }},
    ]})
    print(f"✅ Sheet写入完成：https://docs.google.com/spreadsheets/d/{SHEET_ID}")

if __name__ == "__main__":
    with open(DATA_FILE) as f:
        data = json.load(f)
    write_sheet(data)
