# Weekly Report Skill

**加密行业周报自动化系统 | Crypto Weekly Newsletter Automation**

---

## 📖 简介 | Overview

本 Skill 由 Gater (Tony) 与 AI Agent 共同打磨，用于每周自动生成两部分内容：

This skill automates a weekly crypto newsletter with two components:

- **内容一 | Part A**：每周10条深度资讯精选（含详细分析摘要）
- **内容二 | Part B**：链上数据分析报告（三张 DefiLlama 表格 + 原因分析）

---

## ⏰ 执行时间 | Schedule

**每周二 北京时间 15:00（UTC 07:00）**

| 任务 | 时间 |
|---|---|
| 链上数据抓取 → 写入 Google Sheet | 周二 15:00 BJ |
| 表格数据分析生成 | 周二 15:00 BJ |
| 资讯候选10条推送给用户 | 周二 15:00 BJ |

---

## 📁 文件结构 | File Structure

```
weekly-report-skill/
├── README.md              # 本文件
├── SKILL.md               # 完整 Skill 说明（给 AI Agent 读取）
├── scripts/
│   ├── fetch_defi_data.py  # 链上数据抓取脚本
│   ├── fetch_news.py       # 资讯抓取脚本
│   └── write_sheet.py      # Google Sheet 写入脚本
└── examples/
    └── 2026-03-26-sample.md  # 示例输出
```

---

## 🚀 快速开始 | Quick Start

### 方式一：直接给 AI Agent 读取 SKILL.md

```
请读取并执行以下 Skill：
https://raw.githubusercontent.com/tonyfeng2018/weekly-report-skill/main/SKILL.md
```

### 方式二：Claude / GPT 等模型手动使用

1. 打开 SKILL.md，复制全部内容作为 System Prompt
2. 确保 Agent 有以下能力：
   - `web_fetch` / `urllib` 抓取网页和 API
   - Python 执行环境（运行数据脚本）
   - Google Sheets API 访问（需 Service Account）
   - 可选：GitHub API（更新 Skill 版本）

### 方式三：OpenClaw Agent 本地使用

本 Skill 已同步至本地路径：
`~/.openclaw/workspace/skills/weekly-report/SKILL.md`

---

## 🔧 依赖配置 | Dependencies

### Google Sheets 访问
- Service Account JSON Key（需用户自行配置）
- Spreadsheet ID：在 SKILL.md 中配置

### Python 依赖
```bash
pip install gspread google-auth
```

### 无需付费 API
- DefiLlama API：免费，无需 Key
- DexScreener API：免费，无需 Key
- 资讯来源（PANews/Odaily/ChainFeeds）：免费抓取

---

## ⚠️ 重要注意事项 | Important Notes

1. **父协议合并**：表格三必须用 `parentProtocol` 合并子协议，否则数据虚高
2. **全链稳定币**：用 `/stablecoinchains` 汇总，不能只加表格中的链（会偏低 ~4%）
3. **周变化计算**：用自然周时间戳汇总，不用 `change_7dover7d`（口径不同）
4. **分析原因**：只用本周内近期事件，不能引用历史合作（时效性要求）
5. **DexScreener 异常检测**：卖单/买单比 > 3 且无官网 → 传销嫌疑代币

---

## 📊 示例输出 | Sample Output

见 `examples/2026-03-26-sample.md`

---

## 🔄 版本历史 | Changelog

| 版本 | 日期 | 更新内容 |
|---|---|---|
| v1.0 | 2026-03-26 | 初始版本，基于 Gater × AI Agent 一天打磨完成 |

---

## 📬 联系 | Contact

- Telegram: @tongweb3
- GitHub: @tonyfeng2018
