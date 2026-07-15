# ai-gzh-push

把 ai-daily 排版好的文章推进微信公众号草稿箱。

**零模型、薄传输层**——不排版、不思考，只搬运。是整个公众号每日创作 workflow 的第三环（也是最后一环）：

```
ai-source (采集) → ai-daily (排版) → ai-gzh-push (推送) → 公众号草稿箱【停】
```

## 特性

- **只推到草稿箱**，永不群发。代码里没有群发接口，物理上发不出去，是否发布由人工在后台决定
- **IP 失败可人肉恢复**：因 IP 白名单失败时，脚本报出当前出口 IP + 加白名单指引，人工加完原命令重跑即可
- **access_token 自动缓存与刷新**：本地 `token_cache.json` 单一来源，过期前 5 分钟自动刷新，40001 时再自动兜底重刷一次
- **HTML 大小 + 合规校验**：推送前跑 ai-daily 的校验脚本兜底，不合规直接拦下
- **错误人话化**：常见 errcode（40164/40007/45009/40001 等）都翻译成中文 + 操作指引

## 文件说明

| 文件 | 作用 |
|------|------|
| `push_draft.py` | 主脚本（Python 标准库，零依赖） |
| `config.example.json` | 配置模板（进 git） |
| `config.local.json` | **本地配置**，含 AppID/AppSecret 等敏感信息（**不进 git**） |
| `token_cache.json` | access_token 缓存（自动生成，**不进 git**） |
| `SKILL.md` | Hermes 编排用，描述 skill 的契约与调用方式 |

## 配置（一次性）

1. 复制配置模板：
   ```bash
   cp config.example.json config.local.json
   ```
2. 编辑 `config.local.json`，填入真实值：
   ```json
   {
     "appid": "wxxxxxxxxxxxxx",
     "appsecret": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
     "thumb_media_id": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
     ...
   }
   ```
   - `appid` / `appsecret`：公众号后台「设置与开发 → 基本配置」
   - `thumb_media_id`：封面图素材 id。需要先在公众号后台上传一张封面缩略图（建议 900×500，≤2MB），通过素材管理接口或后台工具拿到 `thumb` 类型的永久素材 `media_id`
3. **IP 白名单**：公众号后台「基本配置 → IP白名单」，加入运行脚本机器的出口 IP。如脚本因 IP 失败会报出当前 IP，按需添加即可

## 运行

```bash
# 推送
python push_draft.py <article.json>

# 只校验（HTML 大小 + 合规），不推送
python push_draft.py <article.json> --dry
```

`<article.json>` 由 ai-daily skill 排版后产出，包含 `title`、`digest`、`content_html_path` 等字段，详见 [SKILL.md](SKILL.md)。

## 失败 → 重试

脚本是无状态幂等的。常见失败场景的处理：

| 失败 | 脚本输出 | 你要做的 |
|------|---------|---------|
| IP 不在白名单 | 报出当前 IP + 加白名单指引 | 去后台加 IP，**原命令重跑** |
| access_token 失效 | 自动刷新重试，仍失败才报错 | 检查 AppID/AppSecret 是否正确 |
| 封面 media_id 无效 | 报错 + 提示重新上传 | 重新上传封面图，拿新 media_id 更新配置 |
| HTML 过大 / 不合规 | 拦截在推送前 | 精简条目或修复 HTML |

## 安全边界

- 脚本只实现 `POST /cgi-bin/draft/add`（进草稿箱），**不实现** `POST /cgi-bin/freepublish/submit`（群发）
- 草稿箱是终点，是否群发由人工在公众号后台预览后决定
- `config.local.json` 在 `.gitignore` 里，AppID/AppSecret 不进 git

## 与 Hermes 工作流

本 skill 在 Hermes 每日工作流中作为最后一环：

```
读 ai-source 的 data/latest-24h.json
  → 调 ai-daily skill 排版（产出 article.json + 合规 HTML）
  → 调本 skill: python push_draft.py article.json
  → 进入草稿箱，人工预览后发布
```

三环里只有 ai-daily 烧模型 token；ai-source（GH Actions 零模型）和 ai-gzh-push（本地零模型）都是确定性流程。
