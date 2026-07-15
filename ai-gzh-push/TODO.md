# ai-gzh-push 待办

## [ ] 闭合 ai-daily → ai-gzh-push 的衔接契约

**背景**：ai-gzh-push 的输入是 `article.json`（含 `title` / `digest` / `content_html_path` / `cover.thumb_media_id`），但 ai-daily skill 现在产出的是**裸 HTML 文件**，并没有产出这个清单 JSON。两环之间还差一步装配。

**要做的**：更新 `../ai-daily/SKILL.md` 的第 5 步（输出），让 ai-daily 排版完成后额外产出一个 `article.json`：

```json
{
  "title": "AI 早报｜<要点新闻>",
  "digest": "≤120 字摘要",
  "content_html_path": "<生成的 _排版_AI 早报.html 的路径>",
  "cover": { "thumb_media_id": "可选，覆盖默认封面" }
}
```

其中 `title` 复用 ai-daily 已有的"外标题建议"，`digest` 从速览/首条提炼，`content_html_path` 指向排版产物。

**触发时机**：用户确认要把 ai-daily 接入完整 workflow 时再动。当前 ai-gzh-push 已就绪，可独立用 `--dry` 或手写 `article.json` 测试。

**相关文件**：
- `push_draft.py` 的 `load_article()` 定义了 article.json 的必填字段
- `SKILL.md` 的「输入契约」章节
