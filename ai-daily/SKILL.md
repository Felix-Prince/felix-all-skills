---
name: ai-daily
description: AI 日报排版引擎，将 JSON 数据转换为可直接粘贴到微信公众号编辑器的 HTML。自动分类（国内/国际）、排序、生成内容速览、装配组件。触发场景：(1) 用户提到"AI 早报""日报排版""公众号早报"，(2) 用户给 JSON 数据要排成早报 HTML，(3) 用户说"自动排版"早报内容。
---

# AI 日报排版 Skill

把从不同来源采集的原始 AI 资讯数据，经过格式化、时间窗口过滤、排版三步，转换为可直接复制粘贴进微信公众号编辑器、且粘贴后样式不丢失的 HTML。

核心资产：
- `scripts/format_data.py` — 原始数据 → 标准 JSON（统一 `publishedAt`）
- `scripts/filter_time_window.py` — 24h 时间窗口过滤
- `references/theme-ai-daily.md` — 主题组件库（设计变量 + 各组件完整 HTML + 模板骨架 + 映射规则）
- `references/data-schema.md` — 标准数据结构

**具体 HTML 代码一律从组件库取，不要凭记忆手写**。

## 工作流

### 0. 输入检测与数据校验

用户交付的可能是以下三种之一：

| 格式 | 特征 | 来源 |
|------|------|------|
| `.txt` 原始采集文本 | 含 `数据源 #N:` 标记 | 36氪 / 钛媒体 / Edge Daily / The Verge |
| `.xml` RSS Feed | `<feed>` Atom 格式 | The Verge RSS |
| `.json` 已加工数据 | `{ meta, items[] }` 结构 | 上游处理过的中间产物 |

**数据校验**：确认 `meta.date` 存在（作为参考日期），`items[]` 非空。

字段完整性问题交由 `scripts/format_data.py` 统一处理。

用户说「直接排 / 自动排 / 一键」时进**全自动模式**：跳过结构确认，自动完成后续所有步骤，交付时附决策说明。

---

### 0.5 ⏰ 原始数据格式化

**任何输入数据都必须先经过此步骤**，确保字段归一化。

```bash
# SKILL_ROOT 是 ai-daily/ 目录所在路径
SKILL_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# 示例：原始文本 → 标准 JSON
python3 "$SKILL_ROOT/scripts/format_data.py" <输入路径> --output <标准JSON路径>

# 如输入是 RSS XML
python3 "$SKILL_ROOT/scripts/format_data.py" <input.xml> --output <标准JSON路径>

# 如输入是已加工 JSON（仍走一遍，归一化 publishedAt）
python3 "$SKILL_ROOT/scripts/format_data.py" <input.json> --output <标准JSON路径>
```

**输出格式**（供后续步骤消费）：

```json
{
  "meta": { "date": "2026-07-12", "collection_time": "..." },
  "items": [
    {
      "title": "...",
      "summary": "...",
      "source": "...",
      "sourceUrl": "...",
      "category": "domestic | international",
      "publishedAt": "2026-07-12T09:08:00+08:00",
      "importance": 5
    }
  ]
}
```

每一条都确保含有 `publishedAt`（ISO 8601 字符串），`category` 已分类。

---

### 1. ⏰ 时间窗口过滤

以 `meta.date` 为参考日期、当天 08:00 为参考时间，保留过去 24h 内的条目。

**规则**：
- 窗口 = `[参考日期当天 08:00 - 24h, 参考日期当天 08:00]`
- `publishedAt` 在窗口内 → 保留
- `publishedAt` 在窗口外 → 自动过滤
- 无 `publishedAt` 的条目：
  - 窗口内有效 ≥ 10 条 → 排除
  - 窗口内有效 < 10 条 → 保留兜底

```bash
python3 "$SKILL_ROOT/scripts/filter_time_window.py" <标准JSON路径>

# 可选参数
python3 "$SKILL_ROOT/scripts/filter_time_window.py" <标准JSON路径> --hour 6
```

脚本输出过滤报告，有效条数为 0 时终止。

---

### 2. 数据预处理

读过滤后的 JSON 做以下处理：

1. **分类**：按 `category` 分成 `domestic` 和 `international` 两组
2. **排序**：每组内按 `importance` 降序，相同则按 `publishedAt` 降序
3. **编号**：每组内重新编号 `01/02/03/04…`（两位数字）
4. **统计**：计算 `total`、`domestic`、`international` 条数
5. **选速览**：从所有 items 中选 `importance` 最高的 3-5 条放入 `featured`，国内/国际尽量均衡

---

### 3. 读组件库

Read `references/theme-ai-daily.md`（含深色容器、栏目条、条目、CTA 等组件）。

后续生成完全依据组件库，HTML 一律从中取、不要手写。

---

### 4. 装配 HTML

依组件库的**「完整文章模板骨架」**装配：

```
1. 深色容器（组件 2）：副标题 + 日期行 + 内容速览
2. 国内板块：栏目条（3a）+ 条目（4a）× N
3. 国际板块：栏目条（3b）+ 条目（4b）× M
4. CTA 容器（组件 5）
```

**装配规则**：
- 日期行：用 `date` + `weekday` + 统计数据填充
- 内容速览：用 `featured[]` 的 `title` 填充（3-5 条）
- 条目：`title` → 条目标题，`summary` → 摘要，`source` → 来源媒体
- 编号：用预处理后的两位数字（`01/02/03…`）
- 颜色：国内条目用青色 `#22D3EE`，国际条目用蓝色 `#3B82F6`
- 末条无分割线：每个板块最后一项去掉 `border-bottom`

---

### 5. 校验合规（强制）

把生成的 HTML 写入目标文件后，**必须运行校验脚本**，ERROR 清零才算完成：

```bash
<SKILL_ROOT>/scripts/validate_gzh_html.py <生成的.html 的实际路径>
```

它确定性地检查平台禁用项和 `<span leaf>` 包裹。报 ERROR 就回到第 4 步修；**半角标点 WARNING 同样要修复到 0 再交付**。

---

### 6. 输出

**产物格式：纯 `<section>…</section>` 正文片段，从全局容器开始，不要包 `<!DOCTYPE>`/`<html>`/`<head>`/`<body>`**——公众号编辑器只接受正文片段。

1. **干净正文文件**：HTML 保存到当前工作目录，文件名 `{原文件名}_排版_AI 早报 (ai-daily).html`
2. **带「复制」按钮的预览页**：
   ```bash
   <SKILL_ROOT>/scripts/wrap_preview.py <上面的干净正文.html>
   ```
   产出 `{...}_预览.html`——浏览器打开后右上角有「复制到公众号」按钮
3. 告知用户：**打开 `{...}_预览.html` → 点右上角「复制」→ 公众号编辑器粘贴**；并给出干净正文文件路径作为兜底。附校验脚本结论。

## 生成时的智能处理（必须做）

1. **外标题建议**：从 `items[]` 中选 `importance` 最高的 `title`，生成外标题建议 `AI 早报｜<要点新闻>`，在交付时告知用户（用于公众号后台填写）
2. **内容速览**：自动选 3-5 条 `importance` 最高的放入深色容器的速览区，国内/国际尽量均衡
3. **中文全角标点**：正文标点一律用全角（，。！？：；""''（）—— …），不要用半角。**生成 HTML 时就直接写弯引号""''**。例外：代码块、行内代码、英文专名/URL 内部保持原样
4. **来源标注**：直接用 `source` 字段值，不加「信息来源：」前缀（简洁）

## 视觉层级（3 层递进）

| 层级 | 作用 | 频率 | 手段 |
|------|------|------|------|
| **锚点层** | 最强锚点：编号、栏目色块 | 每条目 | 青色/蓝色编号 + 色块竖条 |
| **标记层** | 栏目条 | 2 处 | 国内/国际栏目条 |
| **容器层** | 深色报头、CTA | 2 处 | 深色背景容器 |

**克制原则**：
- 青色 `#22D3EE` 只用于国内编号、国内色块、日期、数据高亮
- 蓝色 `#3B82F6` 只用于国际编号、国际色块、国际数据高亮
- 深色 `#0B1220` 只用于报头和 CTA 容器
- 大面积白底 + 灰阶文字，彩色只做编号和色块点缀

## 平台红线（核心，完整检查交给校验脚本）

- **禁止**：`<style>`/`<script>`/`<div>`、`class`/`id` 属性、`position:fixed/absolute/sticky`、`float`、`@media`/`@keyframes`、`display:grid`、CSS 变量、外部字体/CSS
- **必须**：样式全部内联 `style`；所有文字节点用 `<span leaf="">文字</span>` 包裹（否则粘贴后样式丢失）；装饰性空元素内放 `<span leaf=""><br></span>` 占位
- **可用**：`display:flex`（有限）、`linear-gradient`、`border-radius`、`box-shadow`、`<section>/<p>/<span>/<strong>/<img>`

## Gotchas（真实排版踩过的坑）

- **漏 `<span leaf>` 包裹**是最常见致命错——粘贴到公众号后样式整片丢失。靠第 5 步校验脚本兜底，别跳过
- **装饰元素占位**：色块竖条、渐变分割线等空元素必须放 `<span leaf=""><br></span>`，否则微信剥掉样式
- **末条分割线**：每个板块最后一项去掉 `border-bottom`，不然多一条线
- **编号从 01 开始**：两位数字，不要跳号，不要从 1 开始
- **国内国际颜色别混**：国内青色 `#22D3EE`，国际蓝色 `#3B82F6`
- **速览条数 3-5**：不要太多（失去精选感），不要太少（失去目录感）
- **外标题不重复**：正文里不出现外标题（公众号平台自动显示在顶部）
- **标点别混半角**：正文出现半角逗号句号、英文直引号 `"` `'` 都要改成全角
