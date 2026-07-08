# 公众号排版组件库 —— AI 早报

> **设计风格**：科技早报，深色报头 + 青色/蓝色双主色，信息密度高，扫读友好
>
> **适用**：每日 AI 资讯早报，≤10 条精选，国内/国际二分

---

## 设计变量速查表

```
主色·青：       #22D3EE（国内编号、国内色块、日期、数据高亮）
主色·蓝：       #3B82F6（国际编号、国际色块、国际数据高亮）
深色背景：       #0B1220（报头容器、CTA 容器）
深色背景渐变：   linear-gradient(135deg,#0B1220,#1E293B)（CTA 背景）
页面背景：       #FFFFFF
速览背景：       rgba(255,255,255,0.03)

标题色：         #0F172A
正文色：         #1E293B
摘要色：         #475569
来源色：         #64748B
辅助色：         #94A3B8
分割线·栏目：    #E2E8F0
分割线·条目：    #F1F5F9
速览文字：       #CBD5E1
CTA 文字：       #CBD5E1
CTA 品牌：       #475569

正文字号：       13px/15px（不可改）
等宽字体：       'SF Mono',Consolas,monospace（日期/数据）
全局行高：       1.7
最大宽度：       677px
内容区边距：     左右各 24px
```

字体栈：`-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif`

---

## 组件 1 外标题区（公众号平台自动显示）

> 由公众号后台设置，不在 HTML 内生成。此处仅记录结构供参考。

```
位置：页面最顶部，白色背景
结构：
  - 外标题（22px/900/黑色）：AI 早报｜<要点新闻>
  - 作者信息（12px/灰色）：公众号名 · 日期 时间
```

---

## 组件 2 深色容器（报头）

```html
<section style="background:#0B1220;padding:28px 24px 24px;margin-top:16px;">

  <!-- 副标题 -->
  <p style="margin:0 0 16px;font-size:14px;color:#64748B;font-weight:500;letter-spacing:0.5px;">
    <span leaf="">每日精选 AI 资讯，3 分钟扫读完毕</span>
  </p>

  <!-- 日期行 -->
  <section style="display:flex;align-items:center;gap:12px;margin-bottom:20px;">
    <span style="font-family:'SF Mono',Consolas,monospace;font-size:13px;color:#22D3EE;font-weight:700;">
      <span leaf="">2026.07.08</span>
    </span>
    <span style="font-size:12px;color:#64748B;">
      <span leaf="">周三</span>
    </span>
    <span style="flex:1;height:1px;background:linear-gradient(to right,rgba(34,211,238,0.3),transparent);">
      <span leaf=""><br></span>
    </span>
    <section style="display:flex;gap:12px;">
      <span style="font-size:11px;color:#475569;">
        <span leaf="">今日</span><span style="color:#22D3EE;font-weight:700;"><span leaf=""> 8 </span></span><span leaf="">条</span>
      </span>
      <span style="font-size:11px;color:#475569;">
        <span leaf="">国内</span><span style="color:#22D3EE;font-weight:700;"><span leaf=""> 4 </span></span>
      </span>
      <span style="font-size:11px;color:#475569;">
        <span leaf="">国际</span><span style="color:#3B82F6;font-weight:700;"><span leaf=""> 4 </span></span>
      </span>
    </section>
  </section>

  <!-- 内容速览（可选，3-5 条） -->
  <section style="background:rgba(255,255,255,0.03);border-radius:12px;padding:16px 18px;">
    <section style="display:flex;align-items:center;margin-bottom:12px;">
      <span style="font-size:14px;margin-right:6px;"><span leaf="">📋</span></span>
      <span style="font-size:13px;font-weight:800;color:#22D3EE;letter-spacing:1px;">
        <span leaf="">内容速览</span>
      </span>
    </section>
    <p style="margin:0 0 8px;font-size:13px;color:#CBD5E1;line-height:1.8;">
      <span style="color:#22D3EE;font-weight:800;margin-right:6px;"><span leaf="">·</span></span>
      <span leaf="">DeepSeek 被曝自研 AI 芯片，中国大模型厂商走向硬件自主</span>
    </p>
    <p style="margin:0 0 8px;font-size:13px;color:#CBD5E1;line-height:1.8;">
      <span style="color:#22D3EE;font-weight:800;margin-right:6px;"><span leaf="">·</span></span>
      <span leaf="">三星 Q2 利润暴增 1810%，AI 芯片需求持续引爆半导体市场</span>
    </p>
    <p style="margin:0 0 8px;font-size:13px;color:#CBD5E1;line-height:1.8;">
      <span style="color:#22D3EE;font-weight:800;margin-right:6px;"><span leaf="">·</span></span>
      <span leaf="">Anthropic 连发多条动态：Claude Cowork 上线移动端</span>
    </p>
    <p style="margin:0;font-size:13px;color:#CBD5E1;line-height:1.8;">
      <span style="color:#22D3EE;font-weight:800;margin-right:6px;"><span leaf="">·</span></span>
      <span leaf="">腾讯混元 3 正式版发布，搜索能力追平 GPT-5.5</span>
    </p>
  </section>

</section>
```

---

## 组件 3 分类栏目条

### 3a. 国内栏目条

```html
<section style="display:flex;align-items:center;margin-bottom:18px;">
  <span style="display:inline-block;width:4px;height:16px;background:#22D3EE;border-radius:2px;margin-right:10px;">
    <span leaf=""><br></span>
  </span>
  <span style="font-size:15px;font-weight:900;color:#0F172A;letter-spacing:1px;">
    <span leaf="">国内 · DOMESTIC</span>
  </span>
  <span style="flex:1;height:1px;background:#E2E8F0;margin-left:12px;">
    <span leaf=""><br></span>
  </span>
  <span style="font-size:11px;color:#94A3B8;margin-left:10px;">
    <span leaf="">4 条</span>
  </span>
</section>
```

### 3b. 国际栏目条

```html
<section style="display:flex;align-items:center;margin-bottom:18px;">
  <span style="display:inline-block;width:4px;height:16px;background:#3B82F6;border-radius:2px;margin-right:10px;">
    <span leaf=""><br></span>
  </span>
  <span style="font-size:15px;font-weight:900;color:#0F172A;letter-spacing:1px;">
    <span leaf="">国际 · GLOBAL</span>
  </span>
  <span style="flex:1;height:1px;background:#E2E8F0;margin-left:12px;">
    <span leaf=""><br></span>
  </span>
  <span style="font-size:11px;color:#94A3B8;margin-left:10px;">
    <span leaf="">4 条</span>
  </span>
</section>
```

---

## 组件 4 资讯条目

### 4a. 国内条目（青色编号）

```html
<section style="padding:14px 0;border-bottom:1px solid #F1F5F9;">
  <section style="display:flex;align-items:flex-start;">
    <span style="flex-shrink:0;font-size:13px;font-weight:800;color:#22D3EE;width:24px;">
      <span leaf="">01</span>
    </span>
    <section style="flex:1;min-width:0;">
      <p style="margin:0 0 5px;font-size:15px;font-weight:700;color:#0F172A;line-height:1.5;">
        <span leaf="">智谱 GLM-5 开源，参数量 130B 推理降本 60%</span>
      </p>
      <p style="margin:0 0 7px;font-size:13px;color:#475569;line-height:1.7;">
        <span leaf="">国产大模型持续追赶，开源协议支持商用，企业可本地化部署。</span>
      </p>
      <span style="font-size:11px;color:#64748B;font-weight:600;">
        <span leaf="">量子位</span>
      </span>
    </section>
  </section>
</section>
```

### 4b. 国际条目（蓝色编号）

```html
<section style="padding:14px 0;border-bottom:1px solid #F1F5F9;">
  <section style="display:flex;align-items:flex-start;">
    <span style="flex-shrink:0;font-size:13px;font-weight:800;color:#3B82F6;width:24px;">
      <span leaf="">01</span>
    </span>
    <section style="flex:1;min-width:0;">
      <p style="margin:0 0 5px;font-size:15px;font-weight:700;color:#0F172A;line-height:1.5;">
        <span leaf="">Anthropic 推出 Claude 企业版，主打数据隔离</span>
      </p>
      <p style="margin:0 0 7px;font-size:13px;color:#475569;line-height:1.7;">
        <span leaf="">企业数据不用于训练，提供 SOC 2 合规审计与 SSO 接入。</span>
      </p>
      <span style="font-size:11px;color:#64748B;font-weight:600;">
        <span leaf="">Anthropic</span>
      </span>
    </section>
  </section>
</section>
```

**末条无分割线**：最后一项去掉 `border-bottom:1px solid #F1F5F9`。

---

## 组件 5 CTA 容器

```html
<section style="padding:24px 24px 32px;">
  <section style="background:linear-gradient(135deg,#0B1220,#1E293B);border-radius:14px;padding:22px 20px;text-align:center;">
    <p style="margin:0 0 16px;font-size:14px;color:#CBD5E1;line-height:1.7;">
      <span leaf="">觉得有用，欢迎点赞、评论、转发</span>
    </p>
    <p style="margin:16px 0 0;font-size:10px;color:#475569;letter-spacing:1.5px;">
      <span leaf="">AI DAILY · AI 早报</span>
    </p>
  </section>
</section>
```

---

## 完整文章模板骨架

```html
<section style="max-width:677px;margin:0 auto;background:#ffffff;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif;color:#1E293B;line-height:1.7;letter-spacing:0.3px;">

  <!-- 1. 深色容器（组件 2）：副标题 + 日期行 + 内容速览 -->

  <!-- 2. 国内板块 -->
  <section style="padding:28px 24px 8px;">
    <!-- 3a. 国内栏目条 -->
    <!-- 4a. 国内条目 × N（编号 01/02/03/04） -->
  </section>

  <!-- 3. 国际板块 -->
  <section style="padding:20px 24px 8px;">
    <!-- 3b. 国际栏目条 -->
    <!-- 4b. 国际条目 × M（编号 01/02/03/04） -->
  </section>

  <!-- 4. CTA 容器（组件 5） -->

</section>
```

**骨架顺序铁律**：深色容器 → 国内板块 → 国际板块 → CTA

---

## 文章类型 → 组件组合配方

| 文章类型 | 核心组件组合 | 点缀组件 |
|---------|-------------|---------|
| 每日 AI 早报 | 组件 2（深色容器）+ 3a/3b（栏目条）+ 4a/4b（条目）+ 5（CTA） | 无（早报结构固定） |

所有类型共用固定结构：组件 2 + 国内板块 + 国际板块 + 组件 5。

---

## Markdown → AI 早报排版 映射规则

| Markdown/JSON 元素 | 对应组件 | 说明 |
|-------------------|---------|------|
| `items[].category = "domestic"` | 组件 3a + 4a | 国内条目，青色编号 |
| `items[].category = "international"` | 组件 3b + 4b | 国际条目，蓝色编号 |
| `items[].title` | 条目 4a/4b 标题 | 15px/700/黑色 |
| `items[].summary` | 条目 4a/4b 摘要 | 13px/#475569 |
| `items[].source` | 条目 4a/4b 来源 | 11px/600/#64748B |
| `featured[]` | 组件 2 内容速览 | 3-5 条精选 |
| `date` + `weekday` | 组件 2 日期行 | 等宽字体青色 |
| `total/domestic/international` | 组件 2 数据徽章 | 数字加粗着色 |

---

## 公众号平台限制须知

- ❌ 不支持 `<style>`/`<script>`、CSS class/id、`position:fixed/absolute`、`float`、`@media`/`@keyframes`、`display:grid`
- ✅ 支持内联 `style`、`display:flex`（有限）、`linear-gradient`、`border-radius`、`box-shadow`、`<section>/<p>/<span>/<strong>/<img>`
- ✅ 所有文字节点用 `<span leaf="">` 包裹
- ✅ 装饰性空元素内放 `<span leaf=""><br></span>` 占位

---

## WeChat 兼容铁律

- 所有"装饰性空元素"（色块竖条、渐变分割线）**必须在内部放 `<span leaf=""><br></span>` 占位**，否则微信会剥掉样式
- **不要把 `font-size` 打在 `<strong>` 上**，也不要在同一个 `<p>` 里混多个不同 `font-size`
- 结构化区域没有内容时**整块删掉**，不留空 section
