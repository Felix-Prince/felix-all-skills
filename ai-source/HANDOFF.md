# ai-source 交接文档

> 目标：搭建一套**完全自采、完全可控**的 AI 资讯采集 pipeline，替换当前靠 Hermes webFetch/webSearch 实时爬 36氪、钛媒体、The Verge RSS 的不稳定方式。
>
> 本文档自包含，任何 AI 读完即可接着执行，无需其它上下文。

---

## 一、背景与目标

**现状问题**：每天靠 AI 的 webFetch/webSearch 能力实时爬不同数据源（36氪、钛媒体、The Verge RSS 等）采集 AI 内容。这些数据源不稳定，可能被限制，导致采集不可靠。

**目标**：把"实时爬"改成"定时采集 + 本地缓存"，从根上解决稳定性。产出结构化 JSON，供后续整理成每日 AI 早报。

**已确认决策**：
1. 跑在 **GitHub Actions**（always-on、免费、数据 git 版本化）
2. **不覆盖微信公众号**，用官方 RSS 媒体替代（量子位/机器之心等）
3. **完全脱离第三方公开数据**，纯自采（不读 LearnPrompt 等任何第三方 JSON）

---

## 二、核心设计原则

### 1. 采集层零模型依赖
拉取、归一化、去重、AI 相关性评分、importance 评分——全是确定性规则代码，**不调任何模型**。理由：
- 零模型 token——采集层每天定时跑多次，依赖模型则成本与稳定性都不可控
- 可复现可审计——规则代码结果确定，`git log` 能回溯；模型输出每次不同
- AI 相关性用关键词表已够准——粗筛场景规则比模型性价比高
- 模型整合（摘要精炼/选题/排版）属下游消费方职责，不在本 pipeline 范围

采集层运行成本 = GH Actions 免费额度 + 零模型 token。

### 2. RSS 为绝对主干
GH runner 是美国出口，HTML 爬中文站会被限。对策：
- RSS 为绝对主干——RSS 端点基本不受地域限制
- HTML 抓取仅用于个别有稳定时间戳的静态页，且必须能优雅降级
- 访问不了的源会被 `source-status.json` 自动暴露，可决策替换

### 3. 抓用解耦
采集是定时被动跑的、产物是仓库里已提交的静态 JSON；消费方只读静态文件，不再实时爬。稳定性问题从"消费时爬"转移到"可监控的采集层"。

---

## 三、架构

```
GitHub Actions (每 2h)
   ↓ scripts/collect.py
   ↓ 读 config/sources.yaml（信源注册表）
   ↓ fetchers/rss.py + fetchers/static_page.py（RSS 优先，重试+超时+限并发）
   ↓ normalize.py → 归一成结构化条目
   ↓ dedupe.py → 对 archive.json 做哈希+近似去重
   ↓ score.py → AI 相关性 + importance 评分
   ↓ health.py → 写 source-status.json
   ↓ 输出 data/latest-24h.json（结构化 JSON）+ 滚动 archive.json
   ↓ git commit data/ 回仓库
```

**数据格式**：结构化 JSON（条目含标题/摘要/来源/链接/分类/时间/评分等字段）。具体字段集与聚合结构在实现时根据实际采集到的数据形态最终确定，**不预先锁死**。

---

## 四、信源阶梯（选源只认最高稳定梯级）

1. **官方 RSS/Atom/JSON** ← MVP 全在这里
2. 别人仓库 Actions 生成的公开 feed
3. 公开 newsletter 归档 RSS
4. 有稳定时间戳的公开静态页
5. OPML 私人订阅
6. 需密钥的 API（走 GitHub Secrets + 预算门控，后续扩展）
7. 私人邮箱 / cookies / 不稳定桥 ← **不碰**（公众号就在这级）

---

## 五、目录结构

```
ai-source/
├── HANDOFF.md                 # 本文档
├── requirements.txt           # feedparser, requests, beautifulsoup4, pyyaml, python-dateutil
├── config/
│   └── sources.yaml           # 信源注册表：name/url/type/category/tier/enabled
├── scripts/
│   ├── collect.py             # 主入口：读 sources.yaml → 抓 → 归一 → 去重 → 评分 → 输出
│   ├── fetchers/
│   │   ├── base.py            # 公共：重试3次/超时60s/伪装UA/限并发/→RawItem
│   │   ├── rss.py             # feedparser 解析 RSS/Atom（主干）
│   │   └── static_page.py     # requests+BS4，仅个别静态页
│   ├── normalize.py           # RawItem → 结构化条目
│   ├── dedupe.py              # 哈希 + SequenceMatcher 近似去重，对 archive.json
│   ├── score.py               # AI 关键词相关性分 + importance 启发式
│   └── health.py              # 写 source-status.json
├── data/
│   ├── latest-24h.json        # ★ 采集产物
│   ├── archive.json           # 滚动 30d，去重用，git 可 diff 审计
│   └── source-status.json     # 源健康看板
├── .github/workflows/collect.yml   # cron 每 2h，commit data/
└── tests/
    └── test_collect.py        # 断言产物结构完整、去重生效、评分合理
```

> 注：上述目录中 `config/` `requirements.txt` `scripts/fetchers/` 等尚未创建，目录骨架（`.github/` `data/` `scripts/fetchers/` `tests/`）已建好。交接后继续填充代码与文件。

---

## 六、候选信源（URL 需在家中网络逐一验证后写入 sources.yaml）

| 源 | URL | 分类 | 梯级 |
|----|-----|------|------|
| 36氪 | https://36kr.com/feed | domestic | 1 |
| InfoQ 中文 | https://www.infoq.cn/feed | domestic | 1 |
| 量子位 | https://www.qbitai.com/feed | domestic | 1 |
| 机器之心 | https://www.jiqizhixin.com/rss | domestic | 1 |
| Hacker News | https://news.ycombinator.com/rss | international | 1 |
| The Verge | https://www.theverge.com/rss/index.xml | international | 1 |
| TechCrunch | https://techcrunch.com/feed/ | international | 1 |
| Ars Technica | https://feeds.arstechnica.com/arstechnica/index | international | 1 |
| OpenAI blog | https://openai.com/news/rss.xml | international | 0 |
| Anthropic news | https://www.anthropic.com/news/rss.xml | international | 0 |
| Hugging Face blog | https://huggingface.co/blog/feed.xml | international | 0 |
| arXiv cs.AI | https://export.arxiv.org/rss/cs.AI | international | 0 |

> 说明：梯级 0 = 官方一手源（OpenAI/Anthropic/HF/arXiv），importance 评分时权重最高。

---

## 七、关键设计点

1. **RSS 优先 + 优雅降级**：单个源失败不阻断整轮；source-status 记失败原因；连续失败可在 sources.yaml 里 `enabled: false` 关掉。
2. **去重**：哈希(title+url) 精确去重 + SequenceMatcher 相似度>0.8 近似去重（同一新闻多源合并的基础，MVP 先去重不做完整故事线合并，留 hook）。
3. **importance 评分**：`tier权重 × AI相关性分 × 新鲜度`。AI 相关性用关键词表（gpt/claude/llm/agent/大模型…），低于阈值的不进产物。
4. **零密钥默认**：MVP 不需要任何 API Key。付费源(X/TikHub)属梯级 6，后续扩展，密钥只进 GitHub Secrets。
5. **数据 git 版本化**：archive.json + latest-24h.json 提交回仓库，可 `git log` 回溯。

---

## 八、执行计划（MVP 单源闭环先行）

> 省 token 原则：先本地跑通核心，再上 GH Actions，避免远程调试烧 token。

### 阶段 0：家中网络准备（前置）
1. 批量 curl 验证上表 12 个候选 URL 可达性：
   ```bash
   UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
   for url in \
     "https://36kr.com/feed" "https://www.infoq.cn/feed" \
     "https://www.qbitai.com/feed" "https://www.jiqizhixin.com/rss" \
     "https://news.ycombinator.com/rss" "https://www.theverge.com/rss/index.xml" \
     "https://techcrunch.com/feed/" "https://feeds.arstechnica.com/arstechnica/index" \
     "https://openai.com/news/rss.xml" "https://www.anthropic.com/news/rss.xml" \
     "https://huggingface.co/blog/feed.xml" "https://export.arxiv.org/rss/cs.AI" \
   ; do
     code=$(curl -s --max-time 15 -o /dev/null -w "%{http_code}" -A "$UA" "$url")
     printf "%-55s %s\n" "$url" "$code"
   done
   ```
   返回 200 的源可用；选 1 个结构干净的作为 MVP 首源（建议 Hacker News 或 Hugging Face blog，结构干净）。
2. `python -m pip install -r requirements.txt`（Python 3 已有；依赖：feedparser/requests/beautifulsoup4/pyyaml/python-dateutil）

### 阶段 1：单源本地闭环
3. 建 `requirements.txt` + `config/sources.yaml`（先只填 1 个源，enabled:true）
4. `fetchers/base.py` + `rss.py`：抓单源 → RawItem
5. `normalize.py` + `score.py` + `dedupe.py`：产出 `data/latest-24h.json`
6. `health.py` + `tests/test_collect.py`
7. 本地 `python scripts/collect.py --output-dir data --window-hours 24` 跑通 ← **阶段 1 落点**

### 阶段 2：扩源 + 稳定性
8. sources.yaml 批量补到 8-10 个官方 RSS（URL 逐一 curl 验证）
9. 补 normalize 对各源字段/时间格式差异的适配
10. 本地多源跑通，查 `source-status.json` 成功率

### 阶段 3：接 CI
11. `.github/workflows/collect.yml`：每 2h 跑 + commit data/
12. 首轮 CI 跑通，查远程各源可达性（US 出口约束在这步暴露）

### 验证
- 本地：`python scripts/collect.py` → `python -m tests.test_collect` 断言结构完整、去重生效、评分合理
- CI：查 `source-status.json` 各源成功率；查 `latest-24h.json` 的 total/generated_at 是否新鲜
- 稳定性观察：连续跑 3 天，看有没有源持续失败，决定保留/替换

---

## 九、不在本期范围

- 公众号覆盖（已决定不做，靠官方 RSS 媒体替代）
- 完整故事线合并（MVP 只做去重，留 hook）
- 付费源 X/TikHub（梯级 6，后续按预算门控扩展）
- 下游交付与数据格式的最终锁定（实现时根据实际数据形态再定）

---

## 十、方法论来源（仅供理解，不要照搬代码）

本项目吸收了 LearnPrompt/ai-news-radar 仓库的方法论：信源阶梯、源健康监控、抓用解耦、付费源预算门控、RSS 优先替换 RSSHub 公共实例。但**代码与信源全归自己**，不依赖任何第三方数据，不 fork 别人仓库。

关键借鉴点：
- GitHub Actions 定时跑 + 静态 JSON 产物 + git commit 回写
- 用 `source-status.json` 做源健康看板，失败源自动暴露
- config 里的 `replacements`（把 RSSHub 公共实例替换成官方 RSS）和 `skipPrefixes`（跳过不稳定源）思路——本项目直接选官方 RSS，从源头规避
- HTTP 稳定性：重试 + 超时 + 限并发 + 伪装 UA
