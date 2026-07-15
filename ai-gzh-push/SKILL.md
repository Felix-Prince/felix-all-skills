---
name: ai-gzh-push
description: 把 ai-daily 排版好的文章推进微信公众号草稿箱。零模型的薄传输层——只搬运不思考，读文章清单 JSON → 校验 HTML → 换 access_token → draft/add → 停。安全边界：只实现草稿箱接口，永不实现群发接口，草稿箱是终点。触发场景：(1) Hermes 每日 workflow 编排（采集→排版→推送）的最后一环，(2) 用户说"推到公众号草稿箱""推草稿""发布早报"，(3) ai-daily 排完版后要进草稿箱。
---

# ai-gzh-push —— 公众号草稿箱推送

整个公众号创作 workflow 的第三环，也是最后一环：

```
ai-source (GH Actions, 零模型, 2h 定时) → data/latest-24h.json
   ↓ Hermes 每日编排
ai-daily skill (用模型排版) → 文章清单 JSON + 合规 HTML
   ↓ Hermes 调本 skill
ai-gzh-push (零模型, 确定性脚本) → 公众号草稿箱【终点】
```

本 skill 是**薄传输层**：不排版、不调模型、不思考。它只做一件事——把 ai-daily 产出的现成 HTML 安全地塞进公众号草稿箱。

## 输入契约

ai-daily 排版完成后，须产出一个**文章清单 JSON** 交给本 skill：

```json
{
  "title": "AI 早报｜<要点新闻>",
  "digest": "≤120 字摘要，用于列表页展示",
  "content_html_path": "xxx_排版_AI 早报.html",
  "cover": {
    "thumb_media_id": "可选，覆盖默认封面"
  },
  "author": "可选",
  "content_source_url": "可选，阅读原文链接",
  "need_open_comment": 0,
  "only_fans_can_comment": 0
}
```

**必填**：`title`、`content_html_path`。其余可空（`digest` 不填则公众号用正文前 54 字兜底；`cover.thumb_media_id` 不填则用配置默认封面）。

## 前置配置（一次性）

1. 复制 `config.example.json` → `config.local.json`
2. 填入真实值：
   - `appid` / `appsecret`：公众号后台「设置与开发 → 基本配置」
   - `thumb_media_id`：封面图素材 id（先调素材上传接口或后台手动上传一张缩略图拿到）
3. 公众号后台「IP 白名单」加入运行机器的出口 IP（IP 漂移导致失败时，脚本会报出当前 IP 供人工添加）

`config.local.json` 已在 `.gitignore`，**绝不进 git**。

## 运行

```bash
# 校验 + 推送
python push_draft.py <article.json>

# 只校验（HTML 大小 + 合规），不推送
python push_draft.py <article.json> --dry
```

成功输出：
```
✅ 已进入草稿箱（草稿 media_id: xxx）
   → 登录公众号后台「内容与互动 → 图文消息 → 草稿箱」预览后人工发布。
```

## 流程

```
读 article.json
  → 校验 HTML 存在 + 大小未超限（默认 1900KB 阈值）
  → 跑 ../ai-daily/scripts/validate_gzh_html.py 兜底合规校验
  → 取 access_token（本地 token_cache.json 缓存，过期前 5 分钟刷新）
  → draft/add（content=HTML 文件内容, thumb_media_id=封面）
  → 返回 media_id，停
失败 → 按 errcode 翻译成人话，非零退出
```

## 错误处理（关键）

| errcode | 含义 | 脚本行为 |
|---------|------|---------|
| 40164 | IP 不在白名单 | **解析并报出当前出口 IP** + 加白名单指引，人工加完后重跑 |
| 40001 | token 失效 | 自动刷新 token 重试一次，仍失败才报错 |
| 40007/41006 | 封面 media_id 问题 | 报错，提示重新上传缩略图 |
| 45009 | 频率超限 | 提示稍后重试 |
| 其他 | — | 原样抛出 errmsg + 通用指引 |

**IP 失败的人肉回路**：推送因 40164 失败 → 脚本报出当前 IP → 人工去后台加白名单 → 原命令重跑一次即可（脚本无状态幂等，无需清状态）。

## 安全边界（硬规则）

- **只实现 `draft/add`，代码里根本不写群发接口（`freepublish`）**——物理上发不出去，不是靠自觉
- 草稿箱是终点，是否群发由人工在公众号后台预览后决定
- 失败不污染草稿箱（draft/add 是整体提交，失败即不入库）

## 与 Hermes 编排

本 skill 在 Hermes 每日 workflow 中作为最后一环。Hermes 编排逻辑：

```
读 ai-source 的 data/latest-24h.json
  → 调 ai-daily skill 排版，产出 article.json + HTML
  → 调本 skill: python push_draft.py article.json
  → 进草稿箱，人工预览后发布
```

三环里只有 ai-daily 烧模型 token；ai-source 和 ai-gzh-push 都是零模型确定性流程。

## Gotchas

- **token 互踢**：access_token 多端获取会互相失效。本 skill 用本地 `token_cache.json` 做单一来源；若你在别处（如公众号后台调试工具）也获取了 token，本地缓存可能失效——脚本遇到 40001 会自动重刷一次兜底
- **重跑会重复进草稿**：同一篇 article.json 推两次会生成两条草稿（draft/add 不去重）。重跑前可手动删旧草稿
- **HTML 大小**：公众号正文有上限，脚本默认 1900KB 报警，超了直接拦下不推
- **封面图**：必须是 thumb 类型的永久素材 media_id，不能用图片 URL，也不能用普通 image 类型
