#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ai-gzh-push —— 把 ai-daily 排版好的文章推进微信公众号草稿箱。

定位：零模型的薄传输层。
  读 ai-daily 产出的文章清单 JSON → 校验 HTML → 换 access_token → draft/add → 停。

安全边界：本脚本只实现草稿箱接口（draft/add），永不实现群发接口（freepublish）。
草稿箱是终点，是否发布由人工在公众号后台决定。

用法:
    python push_draft.py <article.json>          # 推送
    python push_draft.py <article.json> --dry    # 只校验，不推送

article.json 由 ai-daily skill 产出，字段见 README / SKILL.md。

退出码:
    0  成功进草稿箱
    1  参数/输入错误（文件不存在、JSON 不合法、HTML 不合规）
    2  access_token 获取失败
    3  推送失败（含 IP 白名单、media_id 无效等，errmsg 已翻译为人话）
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
CONFIG_PATH = HERE / "config.local.json"
TOKEN_CACHE = HERE / "token_cache.json"

# Windows 默认控制台是 GBK，打印中文会乱码。强制 stdout/stderr 用 utf-8。
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

REQUEST_TIMEOUT = 30
# access_token 提前 5 分钟认为过期，避免临界态
TOKEN_SAFETY_MARGIN = 300


# ----------------------------- 配置 ----------------------------- #

def load_config():
    if not CONFIG_PATH.exists():
        sys.exit(
            f"[ERROR] 配置文件不存在: {CONFIG_PATH}\n"
            f"        复制 config.example.json 为 config.local.json 并填入真实值。"
        )
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    for k in ("appid", "appsecret", "thumb_media_id"):
        if not cfg.get(k) or cfg[k] == "****":
            sys.exit(f"[ERROR] config.local.json 中 {k} 未填写（仍是占位符 ****）。")
    return cfg


def load_article(path):
    with open(path, "r", encoding="utf-8") as f:
        art = json.load(f)
    for k in ("title", "content_html_path"):
        if not art.get(k):
            sys.exit(f"[ERROR] article.json 缺少必填字段: {k}")
    return art


# ----------------------------- HTTP ----------------------------- #

def http_get_json(url, timeout=REQUEST_TIMEOUT):
    req = urllib.request.Request(url, headers={"User-Agent": "ai-gzh-push/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def http_post_json(url, payload, timeout=REQUEST_TIMEOUT):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8",
                 "User-Agent": "ai-gzh-push/1.0"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


# ----------------------------- access_token ----------------------------- #
# access_token 2h 过期，且多端获取会互踢。本地缓存到文件，过期前刷新，单一来源。

def get_access_token(cfg):
    cached = _read_token_cache()
    now = time.time()
    if cached and cached.get("expires_at", 0) - now > TOKEN_SAFETY_MARGIN:
        return cached["access_token"]

    url = (
        f"{cfg['api_base']}/token"
        f"?grant_type=client_credential&appid={cfg['appid']}&secret={cfg['appsecret']}"
    )
    resp = http_get_json(url)
    if resp.get("errcode"):
        sys.exit(
            f"[ERROR] 获取 access_token 失败: errcode={resp.get('errcode')} "
            f"{resp.get('errmsg')}\n"
            f"        常见原因：AppID/AppSecret 错误、IP 不在白名单（40164）。"
        )
    token = resp["access_token"]
    expires_in = resp.get("expires_in", 7200)
    _write_token_cache(token, now + expires_in)
    return token


def refresh_token(cfg):
    """强制刷新（遇到 token 失效时）。"""
    if TOKEN_CACHE.exists():
        TOKEN_CACHE.unlink()
    return get_access_token(cfg)


def _read_token_cache():
    if not TOKEN_CACHE.exists():
        return None
    try:
        with open(TOKEN_CACHE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _write_token_cache(token, expires_at):
    try:
        with open(TOKEN_CACHE, "w", encoding="utf-8") as f:
            json.dump({"access_token": token, "expires_at": expires_at}, f)
    except Exception:
        pass  # 缓存写失败不影响主流程，下次重新获取


# ----------------------------- HTML 校验 ----------------------------- #

def load_html(article, cfg):
    html_path = Path(article["content_html_path"])
    if not html_path.is_absolute():
        # 相对路径基于 cwd 解析
        html_path = Path.cwd() / html_path
    if not html_path.exists():
        sys.exit(f"[ERROR] 正文 HTML 不存在: {html_path}")
    html = html_path.read_text(encoding="utf-8")
    size_kb = len(html.encode("utf-8")) / 1024
    warn_kb = cfg.get("html_size_warn_kb", 1900)
    if size_kb > warn_kb:
        sys.exit(
            f"[ERROR] 正文 HTML 过大: {size_kb:.1f}KB > {warn_kb}KB，"
            f"公众号接口会拒绝。请精简条目数。"
        )
    return html, html_path


def run_validate_script(html_path):
    """跑 ai-daily 的合规校验脚本兜底。脚本是 ERROR 才阻断；WARNING 只提示。"""
    skill_dir = HERE.parent / "ai-daily"
    validator = skill_dir / "scripts" / "validate_gzh_html.py"
    if not validator.exists():
        print(f"[WARN] 未找到校验脚本 {validator}，跳过合规校验。")
        return
    try:
        r = subprocess.run(
            [sys.executable, str(validator), str(html_path)],
            capture_output=True, text=True, timeout=30,
        )
    except Exception as e:
        print(f"[WARN] 校验脚本执行异常，跳过: {e}")
        return
    if r.stdout:
        print(r.stdout.rstrip())
    # 校验脚本 ERROR 时退出码=1
    if r.returncode != 0:
        sys.exit("[ERROR] HTML 合规校验未通过（见上方 ERROR），修复后再推送。")


# ----------------------------- 推送 ----------------------------- #

def build_article_payload(article, cfg, html):
    title = article["title"]
    digest = article.get("digest", "") or ""
    maxlen = cfg.get("default_digest_maxlen", 120)
    if len(digest) > maxlen:
        digest = digest[:maxlen]
    # 封面：优先用清单里指定的 thumb_media_id，否则用配置默认值
    thumb = (article.get("cover") or {}).get("thumb_media_id") or cfg["thumb_media_id"]
    return {
        "title": title,
        "author": article.get("author", cfg.get("default_author", "")) or "",
        "digest": digest,
        "content": html,
        "content_source_url": article.get("content_source_url", "") or "",
        "thumb_media_id": thumb,
        "need_open_comment": int(article.get("need_open_comment", 0)),
        "only_fans_can_comment": int(article.get("only_fans_can_comment", 0)),
    }


def call_draft_add(cfg, token, payload):
    url = f"{cfg['api_base']}/draft/add?access_token={token}"
    return http_post_json(url, {"articles": [payload]})


# errcode → 人话翻译 + 处理建议
ERRCODE_HINT = {
    40164: "当前出口 IP 不在白名单。去公众号后台「设置与开发 → 基本配置 → IP白名单」"
           "添加报错中显示的 IP，保存后重新运行本脚本。",
    40007: "thumb_media_id 无效（封面图）。封面图可能已被删除或属于别的素材类型，"
           "需重新上传缩略图获取新的 media_id。",
    41006: "thumb_media_id 缺失。",
    45009: "接口调用频率超限，稍等几分钟后重试。",
    40001: "access_token 无效或过期。",
    40125: "AppSecret 错误。",
    40013: "AppID 不合法。",
}


def handle_push_error(resp, cfg, payload, attempted_refresh):
    code = resp.get("errcode")
    msg = resp.get("errmsg", "")
    hint = ERRCODE_HINT.get(code, "未知错误，查看 errmsg 与微信官方文档。")

    # 40164 特殊处理：从 errmsg 里解析出当前出口 IP，给人工加白名单用
    if code == 40164:
        ip = _extract_ip(msg)
        ip_part = f"\n   当前出口 IP: {ip}" if ip else ""
        sys.exit(
            f"\n[ERROR] 推送失败：IP 不在白名单（errcode=40164）\n"
            f"   errmsg: {msg}{ip_part}\n"
            f"   → {hint}"
        )

    # 40001：token 失效，自动重刷一次重试
    if code == 40001 and not attempted_refresh:
        print("[WARN] access_token 失效，自动刷新后重试一次…")
        token = refresh_token(cfg)
        resp2 = call_draft_add(cfg, token, payload)
        if not resp2.get("errcode"):
            return resp2
        return handle_push_error(resp2, cfg, payload, attempted_refresh=True)

    sys.exit(
        f"\n[ERROR] 推送失败：errcode={code} errmsg={msg}\n"
        f"   → {hint}"
    )


def _extract_ip(msg):
    """从 40164 的 errmsg '... invalid ip 1.2.3.4, not in whitelist' 里抓 IP。"""
    import re
    m = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", msg or "")
    return m.group(1) if m else None


# ----------------------------- 主流程 ----------------------------- #

def main():
    ap = argparse.ArgumentParser(description="推送文章到微信公众号草稿箱")
    ap.add_argument("article", help="ai-daily 产出的文章清单 JSON 路径")
    ap.add_argument("--dry", action="store_true", help="只校验，不推送")
    args = ap.parse_args()

    cfg = load_config()
    article = load_article(args.article)
    html, html_path = load_html(article, cfg)

    print(f"📋 文章: {article['title']}")
    print(f"   正文: {html_path}")

    # 1. 合规校验兜底
    run_validate_script(html_path)

    if args.dry:
        print("\n[DRY] 校验通过，未推送。")
        return 0

    # 2. 取 token
    token = get_access_token(cfg)
    print(f"   access_token: 已获取（缓存）")

    # 3. 装配并推送
    payload = build_article_payload(article, cfg, html)
    resp = call_draft_add(cfg, token, payload)
    if resp.get("errcode"):
        handle_push_error(resp, cfg, payload, attempted_refresh=False)

    media_id = resp.get("media_id")
    print(f"\n✅ 已进入草稿箱（草稿 media_id: {media_id}）")
    print(f"   → 登录公众号后台「内容与互动 → 图文消息 → 草稿箱」预览后人工发布。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
