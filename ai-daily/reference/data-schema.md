# AI 早报 · JSON 数据结构规范

> 标准简讯条目格式 · 后续有真实数据后可调整字段

---

## 一、标准条目结构

```json
{
  "id": "20260708-001",
  "title": "智谱 GLM-5 开源，参数量 130B 推理降本 60%",
  "summary": "国产大模型持续追赶，开源协议支持商用，企业可本地化部署。",
  "source": "量子位",
  "sourceUrl": "https://example.com/article/123",
  "category": "domestic",
  "publishedAt": "2026-07-08T08:30:00+08:00",
  "relativeTime": "5h 前",
  "tags": ["开源", "大模型", "智谱"],
  "importance": 8,
  "featured": false
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 唯一标识，建议格式 `YYYYMMDD-序号` |
| `title` | string | 是 | 条目标题（≤30 字） |
| `summary` | string | 是 | 一句话摘要（≤50 字） |
| `source` | string | 是 | 来源媒体名 |
| `sourceUrl` | string | 否 | 原文链接 |
| `category` | string | 是 | 分类：`domestic`（国内）/ `international`（国际） |
| `publishedAt` | string | 否 | ISO 8601 发布时间 |
| `relativeTime` | string | 否 | 相对时间（如"5h 前"），可由 publishedAt 计算 |
| `tags` | string[] | 否 | 标签列表 |
| `importance` | number | 否 | 重要性评分 1-10，用于排序和选速览 |
| `featured` | boolean | 否 | 是否放入内容速览区（默认按 importance 自动选） |

---

## 二、早报聚合结构

```json
{
  "date": "2026-07-08",
  "weekday": "周三",
  "total": 8,
  "domestic": 4,
  "international": 4,
  "items": [
    { /* 标准条目 */ },
    { /* 标准条目 */ }
  ],
  "featured": [
    { /* 速览条目（从 items 中精选 3-5 条） */ }
  ]
}
```

### 聚合字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `date` | string | 日期 `YYYY-MM-DD` |
| `weekday` | string | 星期（周一/周二/...） |
| `total` | number | 总条数 |
| `domestic` | number | 国内条数 |
| `international` | number | 国际条数 |
| `items` | array | 所有条目列表 |
| `featured` | array | 速览条目（3-5 条） |

---

## 三、外标题生成规则

```
格式：AI 早报｜<要点新闻>
要点新闻：从 items 中选 importance 最高的 title
```

示例：`AI 早报｜DeepSeek 自研芯片，三星利润暴增 1810%`

---

## 四、内容速览选取规则

```
1. 按 importance 降序排序
2. 取前 3-5 条
3. 国内/国际尽量均衡（如 2 国内 +2 国际）
```

---

## 五、排序规则

```
1. 先按 category 分组（国内在前，国际在后）
2. 组内按 importance 降序
3. importance 相同按 publishedAt 降序
```

---

## 六、字段调整记录

| 日期 | 调整内容 | 原因 |
|------|---------|------|
| 2026-07-08 | 初始版本 | 基于 v9 预览设计 |
| | | |

> 后续有真实数据后，根据实际字段调整本规范
