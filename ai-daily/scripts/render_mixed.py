#!/usr/bin/env python3
"""
ai-daily: 混合渲染工具 (render_mixed.py)

将公众号 HTML 中容易样式丢失的深色容器部分渲染为截图，
正文条目保持 HTML 文本，兼顾视觉效果与可复制性。

用法：
    python3 render_mixed.py <article.html>

输出：
    {article}_混合.html       — 深色容器替换为 <img> 的最终 HTML
    {article}_header.png      — 深色容器的截图

依赖：pip3 install --user playwright && python3 -m playwright install chromium
"""

import os
import re
import sys
from html.parser import HTMLParser


def find_dark_container(html):
    """
    简化方法：找到首个 style 含 background:#0B1220 的 <section>，
    返回 (start_tag_start, start_tag_end, container_end) 用于替换。
    用 HTMLParser 不够精确，这里用基于索引的 tag 匹配。
    """
    # 查找 pattern: <section style*="background:#0B1220"*>
    # 不区分大小写，带 padding 进一步确认是深色容器非 CTA
    pat = re.compile(
        r'(<section\s+style="[^"]*background:#0B1220[^"]*padding:28px[^"]*">)',
        re.IGNORECASE
    )
    m = pat.search(html)
    if not m:
        # 兜底：只查 background:#0B1220
        pat2 = re.compile(
            r'(<section\s+style="[^"]*background:#0B1220[^"]*">)',
            re.IGNORECASE
        )
        m = pat2.search(html)
    if not m:
        return None

    start = m.start(1)
    tag_start = m.start(1)
    tag_end = m.end(1)

    # 找到匹配的 </section>（跟踪嵌套）
    pos = tag_end
    depth = 1
    while pos < len(html) and depth > 0:
        next_open = html.find('<section', pos)
        next_close = html.find('</section>', pos)

        if next_close == -1:
            break

        if next_open != -1 and next_open < next_close:
            depth += 1
            pos = next_open + len('<section')
        else:
            depth -= 1
            pos = next_close + len('</section>')

    container_end = pos
    return (tag_start, container_end, html[tag_start:container_end])


def wrap_as_full_page(section_html):
    """将片段包成完整 HTML，供 Playwright 渲染。"""
    return f'''<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  width: 677px;
  margin: 0 auto;
  background: #ffffff;
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  -webkit-font-smoothing: antialiased;
}}
</style>
</head><body>
{section_html}
</body></html>'''


def main():
    if len(sys.argv) < 2:
        print("用法: python3 render_mixed.py <article.html>")
        sys.exit(1)

    src = sys.argv[1]
    if not os.path.isfile(src):
        print(f"✗ 找不到文件: {src}")
        sys.exit(1)

    # 读取 HTML
    with open(src, 'r', encoding='utf-8') as f:
        html = f.read()

    # 找到深色容器
    result = find_dark_container(html)
    if result is None:
        print("✗ 未找到深色容器（background:#0B1220），退出")
        sys.exit(1)

    tag_start, container_end, container_html = result
    print(f"  找到深色容器: {len(container_html)} 字符")

    # 输出路径
    basename = os.path.splitext(src)[0]
    img_path = f"{basename}_header.png"
    out_path = f"{basename}_混合.html"

    # ── 用 Playwright 截图 ──
    from playwright.sync_api import sync_playwright

    full_page = wrap_as_full_page(container_html)

    print(f"  启动 Chromium 渲染截图...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": 677, "height": 800},
            device_scale_factor=2,  # Retina 清晰度
        )
        page.set_content(full_page, wait_until="networkidle")

        # 找到深色容器对应的 section
        # 取第一个 background:#0B1220 的 section
        el = page.locator('section[style*="background:#0B1220"]').first
        # 等待渲染
        page.wait_for_timeout(300)

        el.screenshot(path=img_path)
        browser.close()

    print(f"  ✓ 截图已保存: {img_path}")

    # 确认截图尺寸
    img_size = os.path.getsize(img_path)
    print(f"    文件大小: {img_size // 1024} KB")

    # ── 替换为 <img> ──
    img_tag = (
        f'<img src="{os.path.basename(img_path)}" '
        f'alt="AI 早报报头" '
        f'style="width:100%;max-width:677px;display:block;border-radius:0;margin:0;padding:0;" '
        f'>'
    )

    new_html = html[:tag_start] + img_tag + html[container_end:]

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(new_html)

    print(f"  ✓ 混合 HTML 已保存: {out_path}")
    print(f"\n📋 使用说明:")
    print(f"  1. 将 {os.path.basename(img_path)} 和 {os.path.basename(out_path)} 放在同一目录")
    print(f"  2. 用浏览器打开 {os.path.basename(out_path)} 检查效果")
    print(f"  3. 将 {os.path.basename(img_path)} 上传至微信公众号素材库")
    print(f"  4. 把 {os.path.basename(out_path)} 的内容粘贴到公众号编辑器")
    print(f"  5. 在公众号编辑器中替换 <img> 的 src 为微信素材链接")
    print()


if __name__ == '__main__':
    main()
