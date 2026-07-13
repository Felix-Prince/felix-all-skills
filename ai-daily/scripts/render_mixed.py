#!/usr/bin/env python3
"""
ai-daily: 公众号文章渲染工具 (render_mixed.py)

将装配好的 HTML 整篇渲染为高清长图（PNG），公众号 100% 样式保真。

用法：
    python3 render_mixed.py <article.html> --output <output.png>

依赖：
    pip3 install --user playwright && python3 -m playwright install chromium
"""

import os
import sys


def wrap_full_page(section_html):
    """将 <section> 片段包成完整 HTML 页面供渲染。"""
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
        print("用法: python3 render_mixed.py <article.html> --output <output.png>")
        sys.exit(1)

    src = sys.argv[1]

    # 解析 --output
    output_path = None
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--output' and i + 1 < len(sys.argv):
            output_path = sys.argv[i + 1]
            i += 2
        else:
            i += 1

    if not os.path.isfile(src):
        print(f"✗ 找不到文件: {src}")
        sys.exit(1)

    if not output_path:
        basename = os.path.splitext(src)[0]
        output_path = f"{basename}.png"

    # 读取 HTML 正文片段
    with open(src, 'r', encoding='utf-8') as f:
        html = f.read()

    full_page = wrap_full_page(html)

    print(f"  渲染整页截图...")
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": 677, "height": 800},
            device_scale_factor=2,
        )
        page.set_content(full_page, wait_until="networkidle")
        page.wait_for_timeout(500)

        # 整页截图
        page.screenshot(path=output_path, full_page=True)
        browser.close()

    img_size = os.path.getsize(output_path)
    print(f"  ✓ 长图已保存: {output_path}")
    print(f"    文件大小: {img_size // 1024} KB")
    print()


if __name__ == '__main__':
    main()
