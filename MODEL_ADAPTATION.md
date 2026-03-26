# 其他 AI 模型适配说明

> 本说明帮助在不同 AI 能力的模型上执行本系统。

---

## 工具能力分层

### Tier 1：工具完整型（如 OpenClaw + Claude）
**能力**：web_fetch + Python exec + Google Sheets API
**方式**：直接运行三个脚本，全自动完成

### Tier 2：有代码执行但无网络（如 ChatGPT Code Interpreter）
**限制**：无法直接抓取网页和 API
**解决方案**：
1. 在本地运行 `fetch_defi_data.py`，生成 `/tmp/defi_data.json`
2. 把 defi_data.json 内容上传给 AI
3. AI 读取数据，生成分析报告
4. 本地运行 `write_sheet.py` 写入 Google Sheet

### Tier 3：纯对话型（GPT API / Claude API / Gemini，无工具）
**限制**：无 web_fetch、无 Python 执行、无 Google Sheet 访问
**解决方案（手动数据输入流程）**：

#### 链上数据手动流程
1. 打开以下网址，截图或复制数据：
   - 表格一：https://defillama.com/dexs/chains
   - 表格二：https://defillama.com/chains
   - 表格三：https://defillama.com → 协议列表筛选 7d 涨幅
2. 把数据粘贴给 AI
3. 告诉 AI："按执行 Prompt 的要求分析这些数据"
4. AI 生成分析报告，手动复制到 Google Sheet

#### 资讯手动流程
1. 打开以下来源，复制本周文章标题 + 链接：
   - https://chainfeeds.substack.com（最新一期）
   - https://www.panewslab.com/zh/in-depth
   - https://www.odaily.news/zh-CN/deep
2. 把标题列表粘贴给 AI
3. AI 根据选题标准筛选 10 条
4. 逐篇打开文章，让 AI 生成详细摘要

---

## 给纯对话 AI 的关键注意事项

必须告诉 AI 以下规则，否则它会出错：

1. **"表格三数据需要按 parentProtocol 合并子协议，Spark 等子协议不能单独计算"**
2. **"全链稳定币总量要用 defillama 所有链的总和，不是表格中各链加总"**
3. **"周变化要用我提供的自然周数据，不要用 API 里的 change_7dover7d 字段"**
4. **"分析原因只能用本周内（7天内）的事件，不能引用几个月前的历史合作"**
5. **"卖单/买单比超过3倍且无官网的代币，标注传销嫌疑"**

---

## 模型推荐

| 推荐 | 模型 | 说明 |
|---|---|---|
| **最佳** | OpenClaw + Claude Sonnet | 全自动，即本系统 |
| 备选1 | GPT-4o + Code Interpreter | 需手动提供数据 |
| 备选2 | Claude.ai（纯对话） | 需手动提供数据 + 完整 Prompt |
| 备选3 | Gemini Advanced | 同上 |

---

## 给其他 AI 的快速启动方式

直接发以下内容给任何 AI 模型：

> "请读取以下 Skill 文档，按照其中的说明执行加密周报任务：
> https://raw.githubusercontent.com/tonyfeng2018/gater-weekly-report-skill/main/README.md
>
> 我会提供本周的数据，请按照文档中的选题标准、分析框架和输出格式执行。"

---

## Whisper 语音转录配置（OpenClaw 专用）

本系统的语音输入功能依赖 OpenAI Whisper。

### 安装
```bash
brew install openai-whisper
```

### 使用方法
1. 在 OpenClaw 对话中发送语音消息（.ogg / .m4a / .mp3 格式）
2. AI 自动转录为文字
3. 转录内容用于资讯筛选、备忘记录等

### 注意
- Whisper 模型首次运行时会自动下载（约 1.5GB）
- 推荐使用 turbo 模型（速度快，精度足够）
- Telegram 语音消息会先自动转码为 .ogg 格式再处理
