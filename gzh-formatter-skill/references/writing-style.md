# 写作规范与 HTML 输出模板

## 写作核心规则

1. **纯事实，不点评** — 每条资讯只陈述"发生了什么"，不写"这意味着什么""这说明了什么"
2. **每条 1-2 句** — 保持简讯体，信息密度优先
3. **英文内容双语处理** — 标题保留原文，正文先放中文翻译再放英文原文
4. **来源标注** — 正文用 `📎 信息来源：[N]`，文末统一罗列

---

## 7 天主题色配置

所有主题均适配白底（微信公众平台兼容）。

### 周一 · 极简科技 Tech Minimal
```json
{
  "name": "极简科技",
  "h1_color": "#1a1a1a",
  "h2_color": "#2563EB",
  "h3_color": "#1e293b",
  "body_color": "#334155",
  "sec_color": "#94a3b8",
  "line_color": "#e2e8f0",
  "summary_bg": "#f0f4ff",
  "emoji": "🔹",
  "vibe": "干净 · 专业 · 冷静"
}
```

### 周二 · 暖心橙 Warm Orange
```json
{
  "name": "暖心橙",
  "h1_color": "#1a1a1a",
  "h2_color": "#EA580C",
  "h3_color": "#431407",
  "body_color": "#3f3f46",
  "sec_color": "#a1a1aa",
  "line_color": "#fed7aa",
  "summary_bg": "#fff7ed",
  "emoji": "🟠",
  "vibe": "亲切 · 有温度 · 早晨感"
}
```

### 周三 · 薰衣草 Lavender
```json
{
  "name": "薰衣草",
  "h1_color": "#1a1a1a",
  "h2_color": "#7C3AED",
  "h3_color": "#2e1065",
  "body_color": "#3f3f46",
  "sec_color": "#a1a1aa",
  "line_color": "#ddd6fe",
  "summary_bg": "#f5f3ff",
  "emoji": "💜",
  "vibe": "优雅 · 清新 · 柔和"
}
```

### 周四 · 极光绿 Aurora Green
```json
{
  "name": "极光绿",
  "h1_color": "#1a1a1a",
  "h2_color": "#059669",
  "h3_color": "#064e3b",
  "body_color": "#374151",
  "sec_color": "#9ca3af",
  "line_color": "#a7f3d0",
  "summary_bg": "#ecfdf5",
  "emoji": "🟢",
  "vibe": "活力 · 生长感 · 科技自然"
}
```

### 周五 · 中国红 China Red
```json
{
  "name": "中国红",
  "h1_color": "#1a1a1a",
  "h2_color": "#DC2626",
  "h3_color": "#450a0a",
  "body_color": "#3f3f46",
  "sec_color": "#a1a1aa",
  "line_color": "#fecaca",
  "summary_bg": "#fef2f2",
  "emoji": "🔴",
  "vibe": "热烈 · 有张力 · 视觉冲击"
}
```

### 周六 · 莫兰迪 Morandi
```json
{
  "name": "莫兰迪",
  "h1_color": "#1a1a1a",
  "h2_color": "#9D6B7E",
  "h3_color": "#4a3f44",
  "body_color": "#57534e",
  "sec_color": "#a8a29e",
  "line_color": "#e6d5d0",
  "summary_bg": "#faf5f6",
  "emoji": "💗",
  "vibe": "高级 · 安静 · 文艺感"
}
```

### 周日 · 深海蓝 Deep Sea Blue
```json
{
  "name": "深海蓝",
  "h1_color": "#1a1a1a",
  "h2_color": "#1E40AF",
  "h3_color": "#1e3a5f",
  "body_color": "#334155",
  "sec_color": "#94a3b8",
  "line_color": "#dbeafe",
  "summary_bg": "#eff6ff",
  "emoji": "🔵",
  "vibe": "稳重 · 高端 · 专业深度"
}
```

---

## 内容速览写作规范

内容速览是读者打开文章后看到的**第一段内容**，目的不是展示具体新闻，而是让读者 3 秒内知道"今天有哪些看点"。

### 规则

| 规则 | 说明 |
|------|------|
| **条数** | 3-4 条 |
| **长度** | 每条 15-25 字，高度凝练 |
| **语法** | 名词性短语或短句，**不写完整句子** |
| **内容** | 按主题归纳，不是按顺序列前 N 条 |
| **角度** | 覆盖当天最核心的 3-4 个话题，尽量跨信源、跨板块 |
| **时效感** | 使用"发布"/"宣布"/"爆出"/"公布"等即时动词 |

### 示例

```markdown
📋 内容速览
  · AI 教父 LeCun 炮轰 xAI 为"失败品"，警示行业泡沫风险
  · 亚马逊自研芯片挑战英伟达，内部调查 AI 数据中心扩张争议
  · Anthropic 连发两条动态：Claude Design 大更新 + 机器人操控突破
  · 美国政策层面：Sanders 提 7 万亿 AI 公有化计划，Bezos 称 AI 将创造劳动力短缺
```

### 与标题的分工

```
公众号外标题（吸引打开）→ AI 早报｜LeCun 炮轰 xAI 为"失败品"
文章内速览（快速浏览）  → 今日 4 个看点：AI 泡沫 / 芯片竞争 / Anthropic / 政策
```

---

## HTML 输出模板

```html
<!-- 顶部封面图占位 -->
<div style="margin-bottom: 16px; text-align: center;">
  <img src="https://your-image-url.com/640.jpeg" alt="封面图" style="width: 100%; max-width: 640px; border-radius: 8px;">
  <p style="font-size: 12px; color: #ccc; margin-top: 4px;">📷 请上传至微信后替换此图片链接</p>
</div>

<!-- 日期 -->
<p style="font-size: 13px; color: {sec_color}; margin: 0 0 12px 0;">
  {YYYY 年 M 月 D 日（周X）}
</p>

<!-- 内容速览 -->
<div style="background: {summary_bg}; border-radius: 8px; padding: 14px 18px; margin-bottom: 16px;">
  <p style="font-size: 14px; font-weight: 600; color: {h2_color}; margin: 0 0 8px 0; letter-spacing: 0.5px;">
    📋 内容速览
  </p>
  <p style="font-size: 13px; color: {body_color}; line-height: 2; margin: 0;">
    · {第 1 条凝练概括}<br>
    · {第 2 条凝练概括}<br>
    · {第 3 条凝练概括}<br>
    · {第 4 条凝练概括}
  </p>
</div>

<hr style="border: none; border-top: 1px solid {line_color}; margin: 16px 0;">

<!-- 国内板块 -->
<h2 style="font-size: 17px; font-weight: bold; color: {h2_color}; padding-left: 10px; margin: 20px 0 14px 0;">
  🇨🇳 国内动态
</h2>

<div style="margin-bottom: 16px;">
  <h3 style="font-size: 15px; font-weight: 600; color: {h3_color}; margin: 0 0 4px 0;">
    {N}. {标题}
  </h3>
  <p style="font-size: 14px; color: {body_color}; line-height: 1.8; margin: 0 0 4px 0;">
    {正文简讯 1-2 句}
  </p>
  <p style="font-size: 12px; color: {sec_color}; margin: 0 0 14px 0;">
    📎 信息来源：[{N}]
  </p>
</div>

<!-- 英文内容示例 -->
<div style="margin-bottom: 16px;">
  <h3 style="font-size: 15px; font-weight: 600; color: {h3_color}; margin: 0 0 4px 0;">
    {N}. {English Original Title}
  </h3>
  <p style="font-size: 14px; color: {body_color}; line-height: 1.8; margin: 0 0 4px 0;">
    {中文翻译}
  </p>
  <p style="font-size: 14px; color: {body_color}; line-height: 1.8; margin: 0 0 4px 0;">
    {English original text}
  </p>
  <p style="font-size: 12px; color: {sec_color}; margin: 0 0 14px 0;">
    📎 信息来源：[{N}]
  </p>
</div>

<!-- 国际板块 -->
<h2 style="font-size: 17px; font-weight: bold; color: {h2_color}; padding-left: 10px; margin: 20px 0 14px 0;">
  🌏 国际动态
</h2>

<!-- ... 同国内结构 ... -->

<hr style="border: none; border-top: 1px solid {line_color}; margin: 16px 0;">

<!-- 信息来源 -->
<p style="font-size: 13px; color: {sec_color}; line-height: 2;">
  <strong style="color: {sec_color};">📎 信息来源</strong><br>
  [1] {标题} — <a href="{url}" style="color: {h2_color}; text-decoration: none;">{来源名}</a><br>
  [2] {标题} — <a href="{url}" style="color: {h2_color}; text-decoration: none;">{来源名}</a><br>
</p>

<hr style="border: none; border-top: 1px solid {line_color}; margin: 16px 0;">

<!-- 底部声明 -->
<p style="font-size: 13px; color: {sec_color}; text-align: center; font-style: italic; margin-top: 20px;">
  感谢阅读！本资讯由 AI 自动搜集整理，内容仅供参考。
</p>
```

> 所有 `{变量}` 在生成时替换为实际值。`{h1_color}` 等从当天主题色配置中注入。
