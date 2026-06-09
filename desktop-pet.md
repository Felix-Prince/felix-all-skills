# 桌宠助手 — 完整设计文档

> 装上就用，丢进来就能活，感知你的活动

---

## 第一章：产品定义

### 1.1 产品概述

桌面宠物助手是一个轻量级桌面应用，以透明窗口形式在用户桌面上显示一个动画角色。该角色能够自动感知用户当前的活动（编码、游戏、浏览等），并以不同动画、状态徽章和语音气泡做出反应。

### 1.2 核心价值主张

- **零配置可用**：安装后立即运行，内置默认角色和活动识别规则
- **渐进增强**：从单张图片到视频到多状态，每一步都是可选的
- **格式无关**：图片/视频/GIF，丢进来就能用，自动识别格式
- **活动感知**：自动检测前台应用，支持多种信号源接入
- **工具无关**：不绑定任何特定 AI 编码工具，Claude Code / Codex / 手动开发一视同仁
- **极轻量**：~8MB 安装包，~30MB 运行内存

### 1.3 目标用户

| 用户类型 | 需求 | 使用方式 |
|---------|------|---------|
| 休闲用户 | 可爱的桌面陪伴 | 安装即用，内置默认角色 |
| IP 拥有者 | 展示自己的卡通形象 | 拖入一张图/一段视频，立刻变成自己的角色 |
| 开发者 | 开发状态可视化 | 自动检测 IDE 进程，可选接入 AI 编码工具获取细粒度状态 |
| 游戏玩家 | 游戏时桌面互动 | 自动检测游戏进程，切换游戏状态 |

### 1.4 渐进增强模型

产品设计的核心原则：每个功能层次都是可选的，从不强制用户做任何事就能获得价值。

```
Level 0 ── 安装后直接用      → 内置默认角色 + 自动检测活动        ← 零配置
Level 1 ── 拖入一张图        → 你的角色 + CSS动画驱动             ← 10秒
Level 2 ── 拖入视频/GIF      → AI生成的动态视频直接用              ← 丢进来就行
Level 3 ── 拖入多状态素材     → 不同场景不同姿态，每个状态可用不同格式 ← 5分钟
Level 4 ── 眼睛动画/分层     → 眨眼/看向鼠标/独立肢体运动          ← 高阶
```

每一层都比上一层更好，但上一层已经完全可用。用户随时可以停在任意层级。

**关键：视频/GIF 是推荐的主力格式——AI 首帧生视频、丢进来就能播。精灵表是专家选项，不作为默认路径。**

### 1.5 宠物状态体系 — 两层状态设计

状态是桌宠的核心。但状态不应该绑定任何特定工具——用户可能用 Claude Code、Codex、Cursor、或者纯手写代码，宠物都应该能正确表达。

**设计原则：基础状态通用且固定，扩展状态可选且可自定义。**

#### 基础状态（内置，不可修改）

基础状态是宠物永远能理解的"通用语言"，所有信号源最终都映射到基础状态：

| 基础状态 | 含义 | 徽章 | 播放模式 | 气泡示例 | 对应素材槽 |
|---------|------|------|---------|---------|-----------|
| **idle** | 空闲/待机 | 💤 | 循环 | 「今天也要加油哦~」 | idle |
| **active** | 正在做某事 | 🔧 | 循环 | 「忙碌中~」 | active |
| **gaming** | 游戏中 | 🎮 | 循环 | 「游戏时间~」 | gaming |
| **success** | 某事完成 | ✅ | 一次性→idle | 「搞定了！🎉」 | success |
| **failure** | 某事失败 | ❌ | 一次性→idle | 「出错了...」 | failure |
| **drink** | 喝水提醒 | 💧 | 一次性→idle | 「该喝水了!」 | drink |
| **rest** | 休息提醒 | 😴 | 一次性→idle | 「该休息了!」 | rest |

**关键：用户只需要为 7 个基础状态准备素材，宠物就能完整工作。**

#### 扩展状态（可选，用户/信号源自定义）

扩展状态是对基础状态的细化，仅影响气泡消息和徽章图标，**不影响动画切换**——它始终使用所属基础状态的动画：

```
基础状态                    扩展状态（示例）
─────────                  ──────────────
active ────────────────────┬── coding       「正在编码~」      🤖
                           ├── ai-coding    「AI 正在帮我写代码!」 🤖
                           ├── designing    「设计中~」         🎨
                           ├── writing      「写作中~」         ✍️
                           ├── browsing     「随便看看~」       🔍
                           ├── chatting     「聊聊天~」         💬
                           ├── office       「办公模式~」       📊
                           └── (用户自定义...)

active ─── thinking ────────┬── ai-thinking  「AI 思考中...」    🧠
                           └── human-thinking「构思中...」       🧠

active ─── waiting ─────────┬── ai-waiting   「等待 AI 响应...」 ⏳
                           └── human-idle   「等你操作~」       ⏳
```

**扩展状态的工作方式：**

1. 信号源可以推送扩展状态（如 `ai-coding`）
2. 宠物先找到它属于哪个基础状态（`ai-coding` → `active`）
3. 使用基础状态的动画和素材
4. 但使用扩展状态自己的徽章和气泡消息

**这意味着：**
- 只有内置规则的用户：宠物用基础状态（`active`），7 个素材槽就够
- 接入了 AI 编码信号源的用户：宠物能区分 `ai-coding` / `ai-thinking`，显示更精准的气泡
- 用 Codex 的用户：可以定义自己的 `codex-coding` / `codex-reviewing` 扩展状态
- 纯手写代码的用户：IDE 前台时显示 `coding` 扩展状态，一样有编码体验

#### 扩展状态映射规则

扩展状态到基础状态的映射在规则文件中定义：

```json
{
  "state_map": {
    "coding":       { "base": "active",  "badge": "🤖", "messages": ["正在编码~", "写代码中!"] },
    "ai-coding":    { "base": "active",  "badge": "🤖", "messages": ["AI正在帮我写代码!", "AI协作中~"] },
    "ai-thinking":  { "base": "active",  "badge": "🧠", "messages": ["AI思考中...", "分析中..."] },
    "ai-waiting":   { "base": "active",  "badge": "⏳", "messages": ["等待AI响应...", "AI处理中~"] },
    "designing":    { "base": "active",  "badge": "🎨", "messages": ["设计中~"] },
    "browsing":     { "base": "active",  "badge": "🔍", "messages": ["随便看看~"] },
    "chatting":     { "base": "active",  "badge": "💬", "messages": ["聊聊天~"] },
    "office":       { "base": "active",  "badge": "📊", "messages": ["办公模式~"] }
  }
}
```

未在映射表中定义的状态，默认归入 `idle` 基础状态。

### 1.6 核心功能清单

**窗口与显示：**

| 功能 | 说明 | 优先级 |
|------|------|--------|
| 透明无边框窗口 | 始终置顶，无窗口边框和背景 | P0 |
| 角色渲染 | 自动识别格式，支持单图/视频/GIF | P0 |
| 拖拽移动 | 使用 OS 原生拖拽 API | P0 |
| 缩放调整 | 右键菜单或滚轮调整大小 | P1 |
| 位置记忆 | 关闭后重新打开恢复到上次位置 | P1 |

**活动感知：**

| 功能 | 说明 | 优先级 |
|------|------|--------|
| 前台窗口检测 | 每秒扫描前台进程和窗口标题 | P0 |
| 信号源系统 | 通用事件接入机制，支持 Hook/文件/HTTP 等多种信号源 | P0 |
| 文件变化检测 | 监听项目文件变化频率推断开发状态 | P1 |
| 游戏检测 | 全屏窗口 + 已知游戏进程名匹配 | P0 |
| 规则引擎 | JSON 配置的活动识别规则 | P0 |

**交互与反馈：**

| 功能 | 说明 | 优先级 |
|------|------|--------|
| 右键菜单 | 切换状态、调整大小、打开设置 | P0 |
| 系统托盘 | 最小化到托盘，托盘图标菜单 | P0 |
| 语音气泡 | 状态切换时弹出气泡消息 | P0 |
| 状态徽章 | 角色脚下显示当前状态图标 | P0 |
| 眼睛动画 | 眨眼 + 跟随鼠标 | P2 |
| 喝水提醒 | 可配置间隔的定时提醒 | P1 |
| 休息提醒 | 可配置间隔的定时提醒 | P1 |

**配置与管理：**

| 功能 | 说明 | 优先级 |
|------|------|--------|
| 图形设置面板 | 右键→设置，可视化配置所有选项 | P0 |
| JSON 配置文件 | 底层配置文件，高级用户可直接编辑 | P1 |
| 信号源管理 | 添加/移除/配置信号源（含 AI 编码工具一键接入） | P0 |
| 拖拽导入素材 | 直接拖文件到宠物身上替换素材 | P0 |
| 导入/导出配置 | 分享配置给其他用户 | P2 |

### 1.7 非功能需求

| 维度 | 目标 |
|------|------|
| 安装包体积 | ≤ 10MB |
| 运行内存 | ≤ 50MB |
| CPU 空闲时占用 | ≤ 1% |
| 启动时间 | ≤ 2秒 |
| 状态切换延迟 | ≤ 1秒（事件信号），≤ 3秒（进程扫描） |
| MOV 转换时间 | ≤ 10秒（5秒视频） |
| 兼容平台 | Windows 10+（V1），macOS（V2），Linux（V3） |
| 自动更新 | 支持静默更新规则库和版本升级 |

---

## 第二章：素材格式与自动识别

### 2.1 格式优先级：视频优先，精灵表专家选项

现实中的素材生产流程：

```
方式 A（推荐，最简单）：
  AI 生成首帧图 → AI 图生视频（4-5秒）→ 丢进桌宠 → 完了 ✅

方式 B（静态也行）：
  一张 PNG → 丢进桌宠 → CSS 呼吸动画驱动 → 完了 ✅

方式 C（精灵表，最麻烦）：
  逐帧出图 → 拼精灵表 → 量帧宽/间距 → 配参数 → 才能用 ⚠️
```

**结论：精灵表需要测量步长、配置参数，反而不如视频简单。精灵表降级为专家选项，不主动引导用户使用。**

### 2.2 支持的素材格式

| 格式 | 扩展名 | 透明支持 | 生产难度 | 渲染方式 | 推荐度 |
|------|--------|---------|---------|---------|--------|
| **WebM 视频** | `.webm` | ✅ Alpha 通道 | 低（AI 直接出） | `<video>` 播放 | ⭐⭐⭐⭐⭐ |
| **GIF 动图** | `.gif` | ⚠️ 1-bit 透明 | 低（工具转） | `<img>` 直接播放 | ⭐⭐⭐⭐ |
| **APNG** | `.apng` | ✅ Alpha 通道 | 低（工具转） | `<img>` 直接播放 | ⭐⭐⭐⭐ |
| **MOV 视频** | `.mov` | ✅ Alpha 通道 | 低（剪映/AE 出） | 自动转 WebM 后播放 | ⭐⭐⭐⭐ |
| **PNG 单图** | `.png` | ✅ Alpha 通道 | 最低（一张图） | CSS 动画外壳驱动 | ⭐⭐⭐ |
| **精灵表 PNG** | `.png` | ✅ Alpha 通道 | 高（需拼图+配参数） | JS 逐帧驱动 | ⭐ 专家 |

### 2.3 自动格式识别流程

```
用户拖入文件
    │
    ├── 读取文件扩展名
    │   ├── .webm      → WebM 视频播放（推荐格式）
    │   ├── .gif       → GIF 直接播放
    │   ├── .mov       → 自动转 WebM 后播放
    │   ├── .apng      → APNG 直接播放
    │   ├── .png       → 单图模式（CSS 动画驱动）
    │   │   不再自动猜测是否为精灵表
    │   │   精灵表需用户在设置中手动指定
    │   └── 其他       → 尝试按单图处理
    │
    └── 多文件批量拖入
        ├── 1个文件 → 按上述规则识别
        └── 多个文件 → 自动按文件名匹配状态
            如：idle.webm, active.gif, gaming.webm ...
            → 混合模式：不同状态可用不同格式
```

**关键改变：PNG 不再被自动猜测为精灵表。** 所有 PNG 默认按单图处理（CSS 动画驱动），因为：
1. 视频/GIF 已经是更好的动态素材选择，不需要精灵表
2. 精灵表需要测量步长配参数，增加用户负担
3. 大多数用户不会有精灵表素材，但很容易有视频/GIF

### 2.4 精灵表 — 专家选项

精灵表不作为默认路径，仅在设置面板"高级"区域提供入口：

```
设置面板
  └── 🖼️ 我的角色
        └── ⚙️ 高级选项
              └── ☐ 此文件是精灵表（需手动配置帧参数）
                    帧宽：[___]  帧高：[___]  间距：[___]
                    帧数：[___]  帧间隔：[___ms]
```

精灵表参数配置（仅在用户勾选"此文件是精灵表"后出现）：

```json
"sprite_config": {
  "active": {
    "frame_width": 192,
    "frame_height": 192,
    "gap": 0,
    "frame_count": 6,
    "frame_duration_ms": 150
  }
}
```

| 参数 | 含义 | 默认值 |
|------|------|--------|
| `frame_width` | 单帧宽度（px） | 需用户填写 |
| `frame_height` | 单帧高度（px） | 需用户填写 |
| `gap` | 帧间距（px） | 0 |
| `frame_count` | 总帧数 | 需用户填写 |
| `frame_duration_ms` | 每帧持续时间 | 150 |

精灵表渲染使用 JS 逐帧驱动（非 CSS steps()），以支持不同帧宽和间距：

```javascript
class SpriteSheetRenderer {
  constructor(assetPath, config) {
    this.config = config;
    this.currentFrame = 0;
  }

  show(state) {
    const { frame_width, frame_height } = this.config;
    this.el = document.createElement('div');
    this.el.className = 'pet-sprite';
    this.el.style.width = frame_width + 'px';
    this.el.style.height = frame_height + 'px';
    this.el.style.backgroundImage = `url('${this.assetPath}')`;
    this.el.style.backgroundRepeat = 'no-repeat';
    this.currentFrame = 0;
    this.container.appendChild(this.el);
    this.animate();
  }

  animate() {
    if (!this.el) return;
    const { frame_width, gap, frame_duration_ms } = this.config;
    const step = frame_width + gap;
    const offset = this.currentFrame * step;
    this.el.style.backgroundPosition = `-${offset}px 0`;
    this.currentFrame = (this.currentFrame + 1) % this.config.frame_count;
    this.timer = setTimeout(() => this.animate(), frame_duration_ms);
  }

  pause()  { clearTimeout(this.timer); }
  resume() { this.animate(); }
  hide()   { clearTimeout(this.timer); this.el?.remove(); }
}
```

### 2.5 混合格式支持

不同状态可以使用不同格式，渲染引擎自动处理：

```json
// 示例：用户为不同状态提供了不同格式的素材
{
  "idle":    "idle.webm",      // WebM → 视频播放（推荐）
  "active":  "active.gif",    // GIF → 直接播放
  "gaming":  "gaming.webm",   // WebM → 视频播放
  "success": "success.png",   // 单图 → CSS庆祝动画
  "drink":   "drink.apng"     // APNG → 直接播放
}
```

用户不需要关心格式差异，渲染引擎统一处理。

### 2.6 MOV 自动转换

MOV 是视频编辑软件（剪映、AE）最常见的带透明通道导出格式，但浏览器不直接支持。系统自动处理：

```
用户拖入 .mov 文件
    │
    ├── 首次导入时，后端调用 ffmpeg 转换
    │   ffmpeg -i input.mov -c:v libvpx-vp9 -pix_fmt yuva420p output.webm
    │
    ├── 转换结果缓存到 ~/.desktop-pet/cache/
    │   后续直接使用缓存，不重复转换
    │
    └── 转换完成后，渲染引擎按 WebM 模式播放
```

如果系统未安装 ffmpeg，提示用户一键安装或提供手动转换指引。

### 2.7 各格式的渲染能力对比

| 渲染能力 | 单图 PNG | 视频 WebM | GIF | APNG | 精灵表 PNG |
|---------|---------|----------|-----|------|-----------|
| 自动播放 | ❌ 需CSS驱动 | ✅ 原生播放 | ✅ 原生播放 | ✅ 原生播放 | ❌ 需JS驱动 |
| 真透明边缘 | ✅ | ✅ | ❌ 白边 | ✅ | ✅ |
| 循环/一次性 | N/A | ✅ 可控 | ⚠️ 有限 | ✅ | ✅ 可控 |
| 暂停/继续 | ✅ | ✅ | ⚠️ | ⚠️ | ✅ |
| 需配置参数 | ❌ | ❌ | ❌ | ❌ | ⚠️ 需配帧参数 |
| 状态徽章叠加 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 气泡叠加 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 生产难度 | 最低 | 低 | 低 | 低 | 高 |

核心原则：视频/GIF/APNG 丢进来就能播，零配置。精灵表是专家选项，需手动配参数。不管什么格式，状态徽章和气泡系统都正常工作。

---

## 第三章：技术架构

### 3.1 技术选型

| 层级 | 选型 | 理由 |
|------|------|------|
| 桌面框架 | **Tauri v2** | ~8MB 安装包（vs Electron ~150MB），Rust 后端高效，前端仍是 HTML/CSS/JS |
| 后端语言 | **Rust** | 状态机、文件监听、窗口管理、进程扫描，内存安全 |
| 前端 | **纯 HTML/CSS/JS** | 零框架零构建，静态文件直接服务，极致轻量 |
| 视频转换 | **ffmpeg** | MOV→WebM 转换，按需调用 |
| 打包分发 | **Tauri 内置** | `tauri build` 直接输出安装包 |

**为什么选 Tauri 而不是 Electron：**

| 对比项 | Electron | Tauri |
|--------|---------|-------|
| 打包体积 | ~150MB | ~5-10MB |
| 内存占用 | 80-150MB | 20-50MB |
| 后端语言 | Node.js | Rust |
| 透明窗口 | ✅ 成熟 | ✅ Windows/Mac 支持 |
| 前端能力 | 完全一样 | 完全一样 |

桌面宠物的特性是"常驻 + 小型"，150MB 的 Electron 跑一个手指大小的角色太重了。

### 3.2 整体架构图

```
┌─────────────────────────────────────────────────────────┐
│                       用户视角                            │
│  下载.exe → 双击安装 → 桌宠出现 → 拖入素材 → 右键设置     │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│                    Tauri 应用层                           │
│                                                          │
│  ┌──────────┐  ┌───────────┐  ┌───────────┐            │
│  │ 透明窗口  │  │ 系统托盘   │  │ 设置窗口   │            │
│  │ (渲染进程) │  │ (右键菜单) │  │ (GUI配置)  │            │
│  └──────────┘  └───────────┘  └───────────┘            │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │              前端渲染引擎                        │    │
│  │                                                 │    │
│  │  素材格式识别器 ──→ 自动选择渲染策略               │    │
│  │  ┌──────────────────────────────────────────┐  │    │
│  │  │ 渲染策略（按格式自动选择）：                 │  │    │
│  │  │  单图 → CSS动画外壳 + 状态变速 + 徽章       │  │    │
│  │  │  视频 → <video> 直接播放                   │  │    │
│  │  │  GIF/APNG → <img> 直接播放                │  │    │
│  │  │  精灵表 → JS逐帧驱动（专家选项，需配参数）  │  │    │
│  │  └──────────────────────────────────────────┘  │    │
│  │                                                 │    │
│  │  CSS动画外壳 ──→ 呼吸/弹跳/摇摆/庆祝             │    │
│  │  状态徽章   ──→ 基础+扩展状态图标                 │    │
│  │  气泡系统   ──→ 个性化对话                       │    │
│  │  眼睛动画   ──→ 眨眼 + 看向鼠标                  │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │              Rust 后端引擎                        │    │
│  │                                                 │    │
│  │  Activity Scanner  ──→ 前台窗口/进程扫描         │    │
│  │  Signal Router     ──→ 信号源统一路由与分发       │    │
│  │  Rule Engine       ──→ JSON规则匹配              │    │
│  │  State Manager     ──→ 去抖/冷却/两层状态机      │    │
│  │  Config Manager    ──→ 位置/设置持久化            │    │
│  │  Source Manager    ──→ 信号源注册/启停/配置       │    │
│  │  Reminder Timer    ──→ 喝水/休息定时器            │    │
│  │  Format Converter  ──→ MOV→WebM 自动转换         │    │
│  │  Asset Resolver    ──→ 素材格式自动识别           │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │              信号源层（可插拔）                    │    │
│  │                                                 │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐       │    │
│  │  │ 进程扫描  │ │ 文件监听  │ │ Hook事件  │       │    │
│  │  │ (内置)    │ │ (内置)    │ │ (可扩展)  │       │    │
│  │  └──────────┘ └──────────┘ └──────────┘       │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐       │    │
│  │  │ HTTP API │ │ 定时器    │ │ 自定义脚本│       │    │
│  │  │ (可扩展)  │ │ (内置)    │ │ (可扩展)  │       │    │
│  │  └──────────┘ └──────────┘ └──────────┘       │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │              内置资源包                           │    │
│  │                                                 │    │
│  │  default-mascot/ ──→ 默认角色素材                 │    │
│  │  default-rules.json──→ 默认活动识别规则           │    │
│  │  default-messages.json──→ 默认气泡消息            │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### 3.3 Tauri 窗口配置

```javascript
// tauri.conf.json — 透明窗口核心配置
{
  "app": {
    "windows": [
      {
        "label": "pet",
        "title": "DesktopPet",
        "width": 200,
        "height": 200,
        "transparent": true,
        "frame": false,
        "alwaysOnTop": true,
        "resizable": false,
        "decorations": false,
        "skipTaskbar": true
      }
    ]
  }
}
```

### 3.4 项目目录结构

```
desktop-pet/
│
├── src-tauri/
│   ├── src/
│   │   ├── main.rs              ← 启动：透明窗口 + 托盘 + 事件循环
│   │   ├── scanner.rs           ← Windows API 前台窗口/进程扫描
│   │   ├── signal_router.rs     ← 信号源统一路由与分发
│   │   ├── source_manager.rs    ← 信号源注册/启停/配置
│   │   ├── classifier.rs        ← 规则引擎匹配
│   │   ├── state_manager.rs     ← 去抖/冷却/两层状态机
│   │   ├── watcher.rs           ← 文件变化监听
│   │   ├── config.rs            ← 设置持久化 + 位置记忆
│   │   ├── reminder.rs          ← 喝水/休息定时器
│   │   ├── converter.rs         ← MOV→WebM 自动转换
│   │   ├── asset_resolver.rs    ← 素材格式自动识别
│   │   └── commands.rs          ← 暴露给前端的所有 Tauri 命令
│   ├── Cargo.toml
│   └── tauri.conf.json
│
├── src/                          ← 前端（纯 HTML/CSS/JS，零框架零构建）
│   ├── index.html               ← 主窗口（宠物渲染）
│   ├── settings.html            ← 设置面板窗口
│   ├── pet.js                   ← 状态机 + 渲染引擎 + 眼睛动画
│   ├── pet.css                  ── 所有 CSS 动画（呼吸/弹跳/眨眼/徽章/气泡）
│   └── assets/
│       ├── default/             ← 内置默认角色资源
│       │   ├── mascot.png       ← 默认角色单图
│       │   ├── mascot/          ← 默认角色各状态素材（可选）
│       │   └── messages.json    ← 默认消息库
│       └── rules-default.json   ← 内置活动识别规则
│
├── package.json
└── README.md
```

---

## 第四章：渲染引擎

### 4.1 渲染引擎核心 — 自动格式适配

渲染引擎的核心职责：根据素材格式自动选择渲染策略，用户无需关心技术细节。

```javascript
class PetRenderer {
  constructor(config) {
    this.baseStates = {};      // 基础状态 → 素材路径映射
    this.renderers = {};       // 基础状态 → 渲染器实例映射
    this.currentRenderer = null;
    this.init();
  }

  init() {
    for (const [state, assetPath] of Object.entries(this.baseStates)) {
      const spriteConfig = config.sprite_config?.[state] || null;
      this.renderers[state] = this.createRenderer(state, assetPath, spriteConfig);
    }
  }

  createRenderer(state, assetPath, spriteConfig) {
    const format = this.detectFormat(assetPath, spriteConfig);

    switch (format) {
      case 'single-image':    return new SingleImageRenderer(assetPath);
      case 'sprite-sheet':    return new SpriteSheetRenderer(assetPath, spriteConfig);
      case 'gif':             return new GifRenderer(assetPath);
      case 'webm':            return new VideoRenderer(assetPath);
      case 'apng':            return new ApngRenderer(assetPath);
      case 'mov':             return new MovRenderer(assetPath);
    }
  }

  detectFormat(assetPath, spriteConfig) {
    const ext = assetPath.split('.').pop().toLowerCase();

    if (ext === 'gif')  return 'gif';
    if (ext === 'webm') return 'webm';
    if (ext === 'mov')  return 'mov';
    if (ext === 'apng') return 'apng';

    if (ext === 'png') {
      // 仅当用户在设置中明确勾选了"此文件是精灵表"时
      if (spriteConfig) return 'sprite-sheet';
      return 'single-image';  // 默认按单图处理
    }

    return 'single-image';
  }

  /**
   * 切换状态 — 核心方法
   * 接收扩展状态，自动映射到基础状态后切换渲染
   */
  setState(extendedState) {
    const baseState = this.mapToBaseState(extendedState);
    const stateInfo = this.getStateInfo(extendedState);

    // 所有格式都做的三件事：
    this.petEl.dataset.state = baseState;          // 1. 触发CSS动画变速
    badge.textContent = stateInfo.badge;            // 2. 切换徽章（扩展状态自带）
    showBubble(randomMessage(stateInfo.messages));  // 3. 显示状态气泡（扩展状态消息）

    // 基础状态切换渲染器：
    if (this.currentRenderer) this.currentRenderer.hide();
    this.currentRenderer = this.renderers[baseState];
    this.currentRenderer.show(baseState);
  }

  mapToBaseState(extendedState) {
    const mapping = config.state_map[extendedState];
    if (mapping) return mapping.base;
    if (['idle','active','gaming','success','failure','drink','rest'].includes(extendedState)) {
      return extendedState;
    }
    return 'idle';
  }

  getStateInfo(extendedState) {
    const mapping = config.state_map[extendedState];
    if (mapping) {
      return { badge: mapping.badge, messages: mapping.messages };
    }
    const baseBadges = { idle:'💤', active:'🔧', gaming:'🎮', success:'✅', failure:'❌', drink:'💧', rest:'😴' };
    return { badge: baseBadges[extendedState] || '💤', messages: config.defaultMessages[extendedState] };
  }
}
```

### 4.2 单图渲染器 — CSS 动画外壳

让静态 PNG 通过 CSS 变活的核心设计：

```css
/* 基础呼吸动画 — 让任何静态图看起来"活着" */
.pet-image {
  animation: pet-breathe 3s ease-in-out infinite;
  filter: drop-shadow(0 4px 6px rgba(0,0,0,0.15));
}

@keyframes pet-breathe {
  0%, 100% { transform: translateY(0) scale(1); }
  50%      { transform: translateY(-4px) scale(1.03); }
}

/* 阴影同步呼吸 */
.pet-shadow {
  animation: shadow-sync 3s ease-in-out infinite;
}
@keyframes shadow-sync {
  0%, 100% { transform: scaleX(1); opacity: 0.3; }
  50%      { transform: scaleX(0.85); opacity: 0.2; }
}

/* 状态变速 — 同一张图，不同基础状态不同节奏 */
.pet-image[data-state="idle"]    { animation: pet-breathe   3s   ease-in-out infinite; }
.pet-image[data-state="active"]  { animation: pet-breathe   1.2s ease-in-out infinite; }
.pet-image[data-state="gaming"]  { animation: pet-bounce    0.8s ease-in-out infinite; }
.pet-image[data-state="success"] { animation: pet-celebrate 0.6s ease-in-out 1; }
.pet-image[data-state="failure"] { animation: pet-shake     0.5s ease-in-out 1; }
.pet-image[data-state="drink"]   { animation: pet-breathe   2s   ease-in-out 1; }
.pet-image[data-state="rest"]    { animation: pet-idle-sway 5s   ease-in-out infinite; }

@keyframes pet-bounce {
  0%, 100% { transform: translateY(0); }
  30%      { transform: translateY(-10px); }
  60%      { transform: translateY(-2px); }
}

@keyframes pet-celebrate {
  0%   { transform: translateY(0) scale(1); }
  30%  { transform: translateY(-15px) scale(1.1); }
  60%  { transform: translateY(-5px) scale(1.05); }
  100% { transform: translateY(0) scale(1); }
}

@keyframes pet-shake {
  0%, 100% { transform: translateX(0); }
  25%      { transform: translateX(-5px); }
  75%      { transform: translateX(5px); }
}

@keyframes pet-idle-sway {
  0%, 100% { transform: rotate(0deg); }
  25%      { transform: rotate(2deg); }
  75%      { transform: rotate(-2deg); }
}
```

### 4.3 视频/GIF/APNG 渲染器

这三种是主力渲染器——丢进来直接播，零配置：

```javascript
class VideoRenderer {
  show(state) {
    this.el = document.createElement('video');
    this.el.src = this.assetPath;
    this.el.autoplay = true;
    this.el.className = 'pet-animated-video';
    this.el.style.pointerEvents = 'none';
    const loopingStates = ['idle', 'active', 'gaming'];
    this.el.loop = loopingStates.includes(state);
    if (!this.el.loop) {
      this.el.onended = () => pet.setState('idle');
    }
    this.container.appendChild(this.el);
  }
  hide() { this.el?.pause(); this.el?.remove(); }
}

class GifRenderer {
  show(state) {
    this.el = document.createElement('img');
    this.el.src = this.assetPath;
    this.el.className = 'pet-animated-image';
    this.container.appendChild(this.el);
  }
  hide() { this.el?.remove(); }
}

class ApngRenderer {
  // 与 GifRenderer 相同，浏览器自动处理 APNG 动画
}
```

### 4.4 MOV 渲染器 — 自动转换

```javascript
class MovRenderer {
  async show(state) {
    let webmPath = await this.checkCache(this.assetPath);
    if (!webmPath) {
      showBubble('正在转换视频格式...');
      webmPath = await window.__TAURI__.invoke('convert_mov_to_webm', {
        path: this.assetPath
      });
    }
    this.inner = new VideoRenderer(webmPath);
    this.inner.show(state);
  }
  async checkCache(movPath) {
    return await window.__TAURI__.invoke('get_cached_webm', { movPath });
  }
  hide() { this.inner?.hide(); }
}
```

后端 Rust 转换逻辑：

```rust
#[tauri::command]
async fn convert_mov_to_webm(mov_path: String) -> Result<String, String> {
    let cache_dir = get_cache_dir();
    let cache_key = format!("{:x}", md5::compute(&mov_path));
    let webm_path = cache_dir.join(format!("{}.webm", cache_key));

    if webm_path.exists() {
        return Ok(webm_path.to_string_lossy().to_string());
    }

    let output = Command::new("ffmpeg")
        .args(["-i", &mov_path,
               "-c:v", "libvpx-vp9",
               "-pix_fmt", "yuva420p",
               "-auto-alt-ref", "0",
               webm_path.to_str().unwrap()])
        .output()
        .map_err(|e| format!("ffmpeg 调用失败: {}", e))?;

    if !output.status.success() {
        return Err("MOV→WebM 转换失败".into());
    }

    Ok(webm_path.to_string_lossy().to_string())
}
```

### 4.5 状态徽章与气泡

所有渲染模式共享的 UI 层，始终叠加在角色上方：

```html
<div class="pet-container" data-state="idle">
  <div class="pet-bubble" id="bubble">今天也要加油哦~</div>
  <div class="pet-render-area" id="renderArea"></div>
  <div class="pet-badge" id="badge">💤</div>
  <div class="pet-shadow"></div>
</div>
```

```css
.pet-bubble {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: white;
  border-radius: 12px;
  padding: 8px 14px;
  font-size: 13px;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  animation: bubble-in 0.3s ease forwards,
             bubble-out 0.3s ease 3s forwards;
}
.pet-bubble::after {
  content: '';
  position: absolute;
  bottom: -6px;
  left: 50%;
  border-left: 6px solid transparent;
  border-right: 6px solid transparent;
  border-top: 6px solid white;
}

@keyframes bubble-in  { to { opacity: 1; transform: translateX(-50%) translateY(-8px); } }
@keyframes bubble-out { to { opacity: 0; } }

.pet-badge {
  position: absolute;
  bottom: -8px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 16px;
  background: white;
  border-radius: 50%;
  width: 26px;
  height: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
}
```

### 4.6 眼睛动画（可选高阶功能）

用户在设置界面标记眼睛位置后，宠物叠加眨眼动画层：

```css
.eye-blink {
  position: absolute;
  width: 12px;
  height: 12px;
  background: rgba(0,0,0,0.85);
  border-radius: 50%;
  animation: blink 4s ease-in-out infinite;
}

@keyframes blink {
  0%, 42%, 46%, 100% { transform: scaleY(1); }
  44%                { transform: scaleY(0.1); }
}

/* 基础状态影响眨眼频率 */
.pet-container[data-state="active"] .eye-blink { animation-duration: 2.5s; }
.pet-container[data-state="idle"]   .eye-blink { animation-duration: 5s; }
```

眼睛跟随鼠标：

```javascript
document.addEventListener('mousemove', (e) => {
  const rect = petContainer.getBoundingClientRect();
  const cx = rect.left + rect.width / 2;
  const cy = rect.top + rect.height / 2;
  const angle = Math.atan2(e.clientY - cy, e.clientX - cx);
  const maxOffset = 2;
  leftEye.style.transform  = `translate(${Math.cos(angle)*maxOffset}px, ${Math.sin(angle)*maxOffset}px)`;
  rightEye.style.transform = `translate(${Math.cos(angle)*maxOffset}px, ${Math.sin(angle)*maxOffset}px)`;
});
```

---

## 第五章：活动感知系统

### 5.1 信号源架构

活动感知的核心设计原则：**信号源是可插拔的，宠物不依赖任何特定工具。**

```
各种信号源（可插拔）
    │
    ├── 内置信号源
    │   ├── 进程扫描器 ────→ 前台窗口 / 进程列表
    │   ├── 文件变化监听 ──→ 项目文件写入频率
    │   └── 定时器 ────────→ 喝水/休息提醒
    │
    ├── 可扩展信号源
    │   ├── Hook 事件 ─────→ Claude Code / Codex / 其他 AI 工具的 Hook 推送
    │   ├── HTTP API ──────→ 本地 HTTP 服务，任何工具可 POST 状态
    │   ├── 自定义脚本 ────→ 用户指定脚本，定期执行读取输出
    │   └── 文件监听 ──────→ 监听任意文件内容变化
    │
    ↓
 ┌──────────────────────────┐
 │   Signal Router (Rust)    │ ← 统一接收所有信号源的输出
 │   标准化为统一事件格式     │
 └──────────┬───────────────┘
            ↓
 ┌──────────────────────────┐
 │   Rule Engine (JSON规则)  │ ← 匹配规则 → 映射到宠物状态（基础+扩展）
 └──────────┬───────────────┘
            ↓
 ┌──────────────────────────┐
 │   State Manager           │ ← 去抖/冷却 → 两层状态切换
 │   扩展状态 → 基础状态映射  │    动画用基础状态，气泡用扩展状态
 └──────────────────────────┘
```

**所有信号源输出统一的事件格式：**

```json
{
  "source": "进程扫描",
  "timestamp": 1717891200,
  "data": {
    "foreground_process": "Code.exe",
    "foreground_title": "my-project — Visual Studio Code",
    "is_fullscreen": false
  }
}
```

Hook 类信号源输出：

```json
{
  "source": "hook:claude-code",
  "timestamp": 1717891200,
  "data": {
    "event": "PreToolUse",
    "detail": "正在分析代码"
  }
}
```

**Signal Router 不关心信号来自哪里，只负责标准化和分发。**

### 5.2 内置信号源：进程扫描器

Rust 后端每 1-2 秒调用 Windows API 采集原始信号：

```rust
fn scan_activity() -> ActivitySignal {
    let hwnd = unsafe { GetForegroundWindow() };
    let title = get_window_text(hwnd);
    let pid = get_window_pid(hwnd);
    let process_name = get_process_name(pid);
    let is_fullscreen = check_fullscreen(hwnd);
    let all_processes = enumerate_processes();

    ActivitySignal {
        foreground_title: title,
        foreground_process: process_name,
        is_fullscreen,
        running_processes: all_processes,
    }
}
```

仅凭这一层已能做出基本判断：

| 采集到的信号 | 可推断的活动 |
|-------------|------------|
| 进程 Code.exe / cursor.exe 在前台 | 开发中（→ active 基础状态） |
| 进程 LeagueClient.exe + 全屏 | 在打游戏（→ gaming 基础状态） |
| 进程 WeChat.exe 在前台 | 在聊天（→ active / chatting 扩展状态） |
| 进程 chrome.exe + 标题含 "YouTube" | 在看视频（→ active / browsing 扩展状态） |

### 5.3 可扩展信号源：Hook 事件

Hook 是最灵活的信号源——任何支持 Hook/事件回调的工具都可以把状态推送给宠物。

**以 AI 编码工具为例：**

| 工具 | Hook 机制 | 推送的事件 |
|------|----------|----------|
| Claude Code | settings.json hooks | PreToolUse / PostToolUse / Stop |
| Codex | 类似 hook 机制 | 开始/编码中/完成 |
| Cursor | 未来可能有类似机制 | 同上 |
| 任何工具 | 只要能写文件或调 HTTP API | 任意事件 |

**统一接入方式：** 所有 Hook 类信号源都通过写 `~/.desktop-pet/events.json` 或 POST 本地 HTTP API 来推送事件。

```json
// ~/.desktop-pet/events.json — Hook 信号源写入此文件
{
  "source": "hook:claude-code",
  "event": "PreToolUse",
  "detail": "正在分析代码",
  "timestamp": 1717891200
}
```

**一键接入 AI 编码工具：**

当用户在设置中选择"添加信号源 → Hook 事件"，选择工具后后端自动写入 Hook 配置：

```rust
#[tauri::command]
fn add_signal_source(source_type: String, config: Value) -> Result<bool, String> {
    match source_type.as_str() {
        "hook:claude-code" => configure_claude_code_hooks(&config),
        "hook:codex"       => configure_codex_hooks(&config),
        "http-api"         => start_http_listener(config.port),
        _ => Err(format!("未知信号源类型: {}", source_type))
    }
}
```

### 5.4 可扩展信号源：HTTP API

启动一个本地 HTTP 服务，任何工具都可以 POST 状态变化：

```
POST http://localhost:17532/state
Content-Type: application/json

{
  "state": "ai-coding",
  "detail": "Claude 正在编码",
  "ttl_seconds": 30
}
```

最通用的信号源——不需要安装 Hook，不需要写文件，一行 curl 就行：

```bash
curl -X POST http://localhost:17532/state -d '{"state":"ai-coding","detail":"编码中"}'
```

### 5.5 可扩展信号源：文件监听

监听任意文件的内容变化，用于不支持 Hook 的工具或自定义场景：

```json
{
  "type": "file-watch",
  "path": "/path/to/project/build.log",
  "rules": [
    { "contains": "BUILD SUCCESS", "state": "success" },
    { "contains": "BUILD FAILED",  "state": "failure" },
    { "contains": "Compiling",     "state": "active" }
  ]
}
```

### 5.6 规则引擎

用户可配置的 JSON 规则文件，匹配信号到宠物状态（基础+扩展）：

```json
// ~/.desktop-pet/rules.json
{
  "state_map": {
    "coding":      { "base": "active", "badge": "🤖", "messages": ["正在编码~", "写代码中!"] },
    "ai-coding":   { "base": "active", "badge": "🤖", "messages": ["AI正在帮我写代码!", "AI协作中~"] },
    "ai-thinking": { "base": "active", "badge": "🧠", "messages": ["AI思考中...", "分析中..."] },
    "designing":   { "base": "active", "badge": "🎨", "messages": ["设计中~"] },
    "browsing":    { "base": "active", "badge": "🔍", "messages": ["随便看看~"] },
    "chatting":    { "base": "active", "badge": "💬", "messages": ["聊聊天~"] },
    "office":      { "base": "active", "badge": "📊", "messages": ["办公模式~"] }
  },

  "rules": [
    {
      "name": "AI Coding (Hook事件)",
      "priority": 100,
      "match": { "source": "hook:*", "event_data": { "event": "PostToolUse" } },
      "pet_state": "ai-coding"
    },
    {
      "name": "AI Thinking (Hook事件)",
      "priority": 100,
      "match": { "source": "hook:*", "event_data": { "event": "PreToolUse" } },
      "pet_state": "ai-thinking"
    },
    {
      "name": "Game: League of Legends",
      "priority": 85,
      "match": { "foreground_process": ["LeagueClient.exe", "League of Legends.exe"] },
      "pet_state": "gaming"
    },
    {
      "name": "Gaming (Generic)",
      "priority": 80,
      "match": { "is_fullscreen": true },
      "pet_state": "gaming"
    },
    {
      "name": "Coding (IDE前台)",
      "priority": 50,
      "match": { "foreground_process": ["Code.exe", "cursor.exe", "IntelliJ.exe", "windsurf.exe"] },
      "pet_state": "coding"
    },
    {
      "name": "Office",
      "priority": 45,
      "match": { "foreground_process": ["excel.exe", "word.exe", "powerpnt.exe"] },
      "pet_state": "office"
    },
    {
      "name": "Designing",
      "priority": 48,
      "match": { "foreground_process": ["figma.exe", "Photoshop.exe", "Illustrator.exe"] },
      "pet_state": "designing"
    },
    {
      "name": "Browsing",
      "priority": 30,
      "match": { "foreground_process": ["chrome.exe", "msedge.exe", "firefox.exe"] },
      "pet_state": "browsing"
    },
    {
      "name": "Chatting",
      "priority": 35,
      "match": { "foreground_process": ["WeChat.exe", "Telegram.exe", "Discord.exe"] },
      "pet_state": "chatting"
    }
  ]
}
```

**优先级（priority）是关键**——Hook 事件的规则优先级为 100，高于进程扫描的 50。所以当 Hook 推送了 `ai-coding` 事件时，即使进程扫描同时匹配到 "Coding (IDE前台)"，最终仍使用 `ai-coding` 扩展状态。

### 5.7 去抖与冷却机制

状态切换不能像翻书一样快，用户 Alt+Tab 一瞬间不应触发误切换：

```rust
struct StateManager {
    current_base: BaseState,
    current_extended: String,
    candidate_base: Option<BaseState>,
    candidate_extended: Option<String>,
    candidate_since: Instant,
    cooldown_until: Instant,
    min_dwell: Duration,
}

impl StateManager {
    fn evaluate(&mut self, new_extended: &str) -> Decision {
        let new_base = self.map_to_base(new_extended);

        // 冷却期内不切换
        if Instant::now() < self.cooldown_until {
            return Decision::Keep;
        }

        // 同基础 + 同扩展状态，不切换
        if new_base == self.current_base && new_extended == self.current_extended {
            return Decision::Keep;
        }

        // 同基础状态，只换扩展状态（如 coding → ai-coding）
        // 不需要观察期，直接切换（动画不变，只是气泡不同）
        if new_base == self.current_base && new_extended != self.current_extended {
            self.current_extended = new_extended.to_string();
            return Decision::SwitchExtended;
        }

        // 基础状态变化，需要观察期
        if self.candidate_base != Some(new_base) {
            self.candidate_base = Some(new_base);
            self.candidate_extended = Some(new_extended.to_string());
            self.candidate_since = Instant::now();
            return Decision::Observe;
        }

        if self.candidate_since.elapsed() < Duration::from_secs(3) {
            return Decision::Observe;
        }

        // 确认切换基础状态
        self.current_base = new_base;
        self.current_extended = new_extended.to_string();
        self.candidate_base = None;
        self.cooldown_until = Instant::now() + self.min_dwell;
        Decision::SwitchBase
    }
}
```

关键设计：
- **扩展状态切换（同基础状态）**：无需观察期，立即切换（动画不变，只是气泡消息变了）
- **基础状态切换**：需要 3 秒观察期 + 5 秒冷却期（因为要切换动画素材）

### 5.8 完整信号流示例

**场景 A：你在用 Claude Code 编码**

```
00:00  你打开 VSCode，Claude Code 开始工作
       → 进程扫描：Code.exe 在前台 → coding 扩展状态（active 基础状态）
       → 气泡：「正在编码~」
       → 动画：active 快速呼吸

00:10  Claude Code Hook 推送 PreToolUse
       → 匹配 "AI Thinking" (priority 100) → ai-thinking 扩展状态
       → 同基础状态 active，直接切换 ✅
       → 气泡变为：「AI思考中...」
       → 动画不变

00:30  Claude Code Hook 推送 PostToolUse
       → 匹配 "AI Coding" (priority 100) → ai-coding 扩展状态
       → 气泡变为：「AI正在帮我写代码!」

02:00  你 Alt+Tab 切到浏览器看文档（2秒后回来）
       → 进程扫描：chrome.exe → browsing 扩展状态（还是 active 基础状态）
       → 同基础状态，直接切换扩展状态
       → 气泡暂时：「随便看看~」
       → 2秒后你回来，Hook 仍在推送 ai-coding → 切回

02:30  Claude Code 任务完成，Hook 推送 Stop
       → 规则匹配 → success 基础状态
       → 观察3秒确认 → 切换动画
       → 气泡：「搞定了！🎉」
       → 3秒后自动回到 idle
```

**场景 B：你纯手写代码（无 AI 工具）**

```
00:00  你打开 VSCode 手动编码
       → 进程扫描：Code.exe 在前台 → coding 扩展状态
       → 气泡：「正在编码~」
       → 动画：active 快速呼吸
       → 没有 Hook 信号，但宠物依然知道你在编码 ✅

00:30  你切到浏览器查文档
       → 进程扫描：chrome.exe → browsing 扩展状态
       → 气泡：「随便看看~」
```

**场景 C：你在打游戏**

```
00:00  你启动英雄联盟，窗口全屏
       → 进程扫描：LeagueClient.exe + is_fullscreen=true
       → 匹配 "Game: LoL" (priority 85) → gaming 基础状态
       → 观察3秒确认 → 切换动画
       → 气泡：「排位中？加油!」

01:00  游戏结束，你切回桌面
       → 前台变为 Explorer.exe
       → 3秒观察后，匹配 idle 默认规则
       → 切换回 idle 状态
```

---

## 第六章：配置与交互设计

### 6.1 设置面板

右键宠物 → 设置 → 打开图形化设置窗口，不用 JSON 编辑器：

```
┌────────────── 桌宠助手 设置 ──────────────┐
│                                             │
│  🖼️ 我的角色                                │
│  ┌─────────────────────────────────────┐   │
│  │      ┌────────┐                      │   │
│  │      │ 当前角色 │ ← 预览当前角色动画   │   │
│  │      │  预览   │                      │   │
│  │      └────────┘                      │   │
│  │                                      │   │
│  │  [📂 选择图片/视频] [🔄 使用默认角色]  │   │
│  │                                      │   │
│  │  支持格式：PNG / GIF / WebM / MOV     │   │
│  │  系统自动识别，无需手动选择格式         │   │
│  │                                      │   │
│  │  ─ ─ ─ 多状态素材（可选）─ ─ ─ ─ ─   │   │
│  │  拖入多个文件，按文件名自动匹配状态     │   │
│  │  待机：[📂] 忙碌：[📂] 游戏：[📂]      │   │
│  │  成功：[📂] 失败：[📂] 喝水：[📂]      │   │
│  │  每个状态可用不同格式                   │   │
│  │                                      │   │
│  │  ─ ─ ─ 高级选项 ─ ─ ─ ─ ─ ─ ─ ─ ─   │   │
│  │  ☐ 此文件是精灵表（需手动配置帧参数）   │   │
│  │  帧宽：[___] 帧高：[___] 间距：[___]   │   │
│  │  帧数：[___] 帧间隔：[___ms]           │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  👁️ 眼睛动画                                │
│  ┌─────────────────────────────────────┐   │
│  │  ☑ 启用眨眼效果                       │   │
│  │  在角色图上标记眼睛位置：               │   │
│  │  ┌────────┐                          │   │
│  │  │ [角色图] │ ← 拖拽标记两只眼睛位置   │   │
│  │  │ ●  ●    │                          │   │
│  │  └────────┘                          │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  📡 信号源                                   │
│  ┌─────────────────────────────────────┐   │
│  │  已启用：                              │   │
│  │  ✅ 进程扫描（内置）                    │   │
│  │  ✅ 文件变化监听（内置）                 │   │
│  │                                      │   │
│  │  可添加：                              │   │
│  │  [＋ Hook 事件]                       │   │
│  │    → Claude Code / Codex / 自定义      │   │
│  │  [＋ HTTP API]                        │   │
│  │    → 任何工具通过 HTTP 推送状态         │   │
│  │  [＋ 文件监听]                         │   │
│  │    → 监听指定文件内容变化               │   │
│  │  [＋ 自定义脚本]                       │   │
│  │    → 定期执行脚本读取输出               │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ⏰ 提醒                                    │
│  ┌─────────────────────────────────────┐   │
│  │  ☑ 喝水提醒  每 [30] 分钟              │   │
│  │  ☑ 休息提醒  每 [60] 分钟              │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  💬 个性设置                                │
│  ┌─────────────────────────────────────┐   │
│  │  ☑ 显示气泡对话                       │   │
│  │  角色名称：[小伴___]                   │   │
│  │  [自定义消息] ← 打开消息编辑器         │   │
│  │  [自定义状态] ← 管理扩展状态           │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  🎮 活动识别规则                            │
│  ┌─────────────────────────────────────┐   │
│  │  [查看/编辑规则] ← 高级用户             │   │
│  │  当前：7 个基础状态 + 6 个扩展状态      │   │
│  └─────────────────────────────────────┘   │
│                                             │
│              [保存]  [重置默认]               │
└─────────────────────────────────────────────┘
```

### 6.2 添加 Hook 信号源

用户点击"＋ Hook 事件"后，选择工具类型：

```
┌── 添加 Hook 信号源 ──────────────┐
│                                   │
│  选择工具：                        │
│  ○ Claude Code                    │
│  ○ Codex                          │
│  ○ 自定义 Hook                    │
│                                   │
│  [下一步]                         │
└───────────────────────────────────┘

→ 选择 Claude Code 后：
┌── 配置 Claude Code Hook ─────────┐
│                                   │
│  状态映射：                        │
│  工具开始 → [ai-thinking ▾]       │
│  工具执行 → [ai-coding   ▾]       │
│  工具完成 → [success      ▾]       │
│  工具停止 → [idle         ▾]       │
│                                   │
│  ☑ 自动写入 Hook 配置到            │
│     ~/.claude/settings.json       │
│                                   │
│  [连接]  [取消]                    │
└───────────────────────────────────┘

→ 选择 Codex 后：
┌── 配置 Codex Hook ───────────────┐
│                                   │
│  状态映射：                        │
│  编码中 → [coding      ▾]         │
│  审查中 → [ai-thinking ▾]         │
│  完成   → [success      ▾]        │
│  等待   → [idle         ▾]        │
│                                   │
│  [连接]  [取消]                    │
└───────────────────────────────────┘
```

### 6.3 拖拽导入素材

```javascript
petContainer.addEventListener('drop', async (e) => {
  e.preventDefault();
  const files = [...e.dataTransfer.files];

  if (files.length === 1) {
    await window.__TAURI__.invoke('import_asset', { path: files[0].path });
    showBubble('换上新衣服啦~');
  } else {
    await window.__TAURI__.invoke('import_assets_batch', {
      paths: files.map(f => f.path)
    });
    showBubble('新造型加载完成!');
  }
});
```

后端自动按文件名匹配基础状态：

```rust
fn match_filename_to_state(filename: &str) -> Option<String> {
    let name = filename.to_lowercase();
    if name.contains("idle") || name.contains("待机")   { return Some("idle".into()); }
    if name.contains("active") || name.contains("忙碌")  { return Some("active".into()); }
    if name.contains("game") || name.contains("游戏")    { return Some("gaming".into()); }
    if name.contains("success") || name.contains("完成") { return Some("success".into()); }
    if name.contains("fail") || name.contains("失败")    { return Some("failure".into()); }
    if name.contains("drink") || name.contains("喝水")   { return Some("drink".into()); }
    if name.contains("rest") || name.contains("休息")    { return Some("rest".into()); }
    if name.contains("work") || name.contains("工作")    { return Some("active".into()); }
    if name.contains("code") || name.contains("编码")    { return Some("active".into()); }
    None
}
```

### 6.4 配置文件结构

```json
// ~/.desktop-pet/config.json
{
  "version": "1.0.0",

  "character": {
    "assets": {
      "idle":    "C:/Users/Pengfei.Zhu3/Pictures/my-cat-idle.webm",
      "active":  "C:/Users/Pengfei.Zhu3/Pictures/my-cat-work.gif",
      "gaming":  "C:/Users/Pengfei.Zhu3/Pictures/my-cat-game.webm",
      "success": "C:/Users/Pengfei.Zhu3/Pictures/my-cat-yay.png",
      "failure": "C:/Users/Pengfei.Zhu3/Pictures/my-cat-fail.png",
      "drink":   "C:/Users/Pengfei.Zhu3/Pictures/my-cat-drink.apng",
      "rest":    "C:/Users/Pengfei.Zhu3/Pictures/my-cat-rest.png"
    },
    "sprite_config": null,
    "eye_positions": [
      { "x": 0.35, "y": 0.28 },
      { "x": 0.55, "y": 0.28 }
    ],
    "enable_blink": true,
    "use_default": false
  },

  "signal_sources": [
    { "type": "process-scanner", "enabled": true },
    { "type": "file-watcher", "enabled": true },
    { "type": "hook", "id": "claude-code", "enabled": true }
  ],

  "reminders": {
    "drink_interval_min": 30,
    "rest_interval_min": 60,
    "enabled": true
  },

  "window": {
    "x": 800,
    "y": 600,
    "scale": 1.0
  },

  "bubble": {
    "enabled": true,
    "character_name": "小伴",
    "custom_messages": null,
    "show_duration_ms": 3000
  }
}
```

所有 `null` 字段 = 使用内置默认值。用户只需要改他们想改的。

---

## 第七章：消息系统

### 7.1 默认消息库

消息按基础状态组织，扩展状态可覆盖：

```json
// 内置 messages.json
{
  "idle":    ["今天也要加油哦~", "有什么需要帮忙的吗？", "发呆中..."],
  "active":  ["忙碌中~", "加油!", "专注模式开启!"],
  "gaming":  ["游戏时间~", "你也在玩游戏？我陪你!", "好耶!"],
  "success": ["搞定了！🎉", "任务完成!", "太棒了!"],
  "failure": ["出错了...", "别灰心，再试试!", "需要帮忙吗？"],
  "drink":   ["该喝水了！💧", "30分钟没喝水了哦", "喝口水吧~"],
  "rest":    ["该休息了！😴", "起来走走吧~", "休息一下眼睛~"]
}
```

### 7.2 扩展状态消息

扩展状态的消息在 `state_map` 中定义，优先于基础状态消息：

```json
{
  "coding":      { "base": "active", "badge": "🤖", "messages": ["正在编码~", "写代码中!"] },
  "ai-coding":   { "base": "active", "badge": "🤖", "messages": ["AI正在帮我写代码!", "AI协作中~"] },
  "ai-thinking": { "base": "active", "badge": "🧠", "messages": ["AI思考中...", "分析中..."] },
  "designing":   { "base": "active", "badge": "🎨", "messages": ["设计中~"] },
  "browsing":    { "base": "active", "badge": "🔍", "messages": ["随便看看~", "网上冲浪🏄"] },
  "chatting":    { "base": "active", "badge": "💬", "messages": ["聊聊天~", "社交时间!"] },
  "office":      { "base": "active", "badge": "📊", "messages": ["办公模式~"] }
}
```

当宠物处于 `ai-coding` 扩展状态时：
- 动画：使用 `active` 基础状态的动画
- 徽章：🤖（扩展状态自定义）
- 气泡：从 `ai-coding` 的消息列表随机选

### 7.3 自定义消息

用户可在设置面板中编辑消息，或直接编辑 JSON：

```json
// ~/.desktop-pet/custom-messages.json
{
  "gaming":    ["又打游戏！作业写完了吗！", "上分上分!"],
  "ai-coding": ["AI又在帮我干活了~", "AI打工仔上线"],
  "success":   ["完美收官✨"]
}
```

自定义消息覆盖默认消息和扩展状态消息中对应状态的条目，未覆盖的状态仍使用默认。

---

## 第八章：开发路线图

### Phase 1 — MVP（2-3周）

- [x] 产品设计文档
- [ ] Tauri 项目初始化，透明窗口 + 系统托盘
- [ ] 前端渲染引擎（单图 CSS 动画 + 视频 + GIF + APNG）
- [ ] 状态徽章 + 语音气泡
- [ ] 两层状态体系（基础状态动画 + 扩展状态消息）
- [ ] 右键菜单（手动切换状态、调整大小、退出）
- [ ] 拖拽移动（OS 原生 API）
- [ ] 内置默认角色 + 默认消息
- [ ] 基本配置文件读写

### Phase 2 — 活动感知（2周）

- [ ] Windows API 进程扫描（scanner.rs）
- [ ] Signal Router 统一信号路由（signal_router.rs）
- [ ] 规则引擎（classifier.rs + rules.json）
- [ ] 去抖状态机（state_manager.rs）
- [ ] 内置默认规则 + 扩展状态映射
- [ ] 文件监听（watcher.rs）

### Phase 3 — 信号源生态（2周）

- [ ] 信号源管理框架（source_manager.rs）
- [ ] Hook 信号源（支持 Claude Code / Codex 等一键接入）
- [ ] HTTP API 信号源（本地 HTTP 服务）
- [ ] 文件监听信号源（自定义文件规则匹配）
- [ ] 设置面板中的信号源管理 UI

### Phase 4 — 产品打磨（2周）

- [ ] 图形设置面板（settings.html）
- [ ] 拖拽导入素材 + 格式自动识别
- [ ] MOV→WebM 自动转换
- [ ] 混合格式支持（不同状态不同格式）
- [ ] 精灵表专家选项（高级设置中可选启用）
- [ ] 位置/大小持久化
- [ ] 喝水/休息定时提醒
- [ ] 自定义消息编辑
- [ ] 打包分发（安装包）

### Phase 5 — 高阶功能（持续）

- [ ] 眼睛动画（眨眼 + 跟随鼠标）
- [ ] 规则库在线更新
- [ ] 自定义脚本信号源
- [ ] macOS 适配
- [ ] 导入/导出配置
- [ ] 角色市场（分享角色素材包）
