#!/usr/bin/env python3
"""
ai-daily: 原始数据格式化工具 (format_data.py)

将不同来源的原始采集数据统一格式化为标准 JSON，确保每条有明确的 publishedAt。

用法：
    python3 format_data.py <input> [选项]

输入自动检测：
    .xml        → Atom RSS (The Verge)
    .json       → 已加工的 JSON（重新提取并归一化 publishedAt）
    .txt 或其它  → 原始采集文本（含 36kr / 钛媒体 / Edge Daily / The Verge 文本摘要）

选项：
    --date YYYY-MM-DD    覆盖参考日期（默认从数据中提取）
    --output PATH        输出路径（默认 stdout）
    --hour HH            参考时间点（默认 8）

输出格式：
    {
      "meta": { "date": "...", "collection_time": "..." },
      "items": [
        {
          "title": "...",
          "summary": "...",
          "source": "...",
          "sourceUrl": "...",
          "category": "domestic|international",
          "publishedAt": "2026-07-12T09:08:00+08:00",
          "importance": 5,
          "featured": false
        }
      ]
    }
"""

import json
import re
import sys
import os
import html
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

TZ_CST = timezone(timedelta(hours=8))


# ── 时间解析工具 ──

def parse_iso_datetime(s):
    if not s or not isinstance(s, str):
        return None
    s = s.strip()
    try:
        if s.endswith('Z') or s.endswith('z'):
            s = s[:-1] + '+00:00'
        return datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return None


def parse_time_ago(time_ago, ref_dt, ref_date):
    if not time_ago or not isinstance(time_ago, str):
        return None
    tz = ref_dt.tzinfo or TZ_CST

    m = re.match(r'^(\d+)分钟前$', time_ago)
    if m:
        return ref_dt - timedelta(minutes=int(m.group(1)))

    m = re.match(r'^(\d+)小时前$', time_ago)
    if m:
        return ref_dt - timedelta(hours=int(m.group(1)))

    if time_ago == '昨天':
        d = ref_date - timedelta(days=1)
        return datetime(d.year, d.month, d.day, 12, 0, tzinfo=tz)

    m = re.match(r'^(\d{1,2})月(\d{1,2})日$', time_ago)
    if m:
        return datetime(ref_date.year, int(m.group(1)), int(m.group(2)), 12, 0, tzinfo=tz)

    m = re.match(r'^(\d{4})-(\d{2})-(\d{2})$', time_ago)
    if m:
        return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), 12, 0, tzinfo=tz)

    return None


def resolve_to_iso(dt):
    if dt is None:
        return ''
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=TZ_CST)
    return dt.isoformat()


# ── 36氪 innerText 解析 ──

def parse_36kr_text(lines, ref_dt, ref_date):
    """
    36kr innerText 排版：标题单独一行，空行后接摘要+来源+时间。
    每篇文章拆成两个连续块：[title] + [summary, source, time_ago]。
    做块配对再提取。
    """
    items = []

    header_pattern = re.compile(r'^(数据源|URL:|采集方法|采集时间|原始输出|={3,})')
    clean_lines = [l for l in lines if not header_pattern.match(l.strip())]

    # 按连续非空行分块
    blocks = []
    current = []
    for line in clean_lines:
        if line.strip():
            current.append(line.strip())
        else:
            if current:
                blocks.append(current)
                current = []
    if current:
        blocks.append(current)

    TIME_RX = re.compile(r'分钟前|小时前|昨天|\d{1,2}月\d{1,2}日|\d{4}-\d{2}-\d{2}')
    SKIP_KW = ['登录', '搜索', '首页', '快讯', '最新', '创投', '直播',
               '专题', '活动', '企业号', '红人', '我要入驻', '寻求报道',
               '投资者关系', '商务合作', '关于我们', '联系我们', '加入我们',
               '网络谣言', '热门', 'Ai产品日报']

    i = 0
    while i < len(blocks):
        block = blocks[i]

        # 情况 A: 单行块 + 下一个块末尾有时间 → 配对组合
        if len(block) == 1 and i + 1 < len(blocks):
            next_block = blocks[i + 1]
            last = next_block[-1] if next_block else ''
            if TIME_RX.search(last):
                title = block[0]
                if len(title) >= 6 and not any(kw in title for kw in SKIP_KW):
                    body = next_block
                    time_ago = body[-1]
                    source = body[-2] if len(body) >= 2 else ''
                    summary = body[0] if len(body) >= 3 else ''
                    # 如果只有 2 行（source + time），无摘要
                    if len(body) == 2:
                        summary = ''
                    if not any(kw in source for kw in SKIP_KW):
                        item_time = parse_time_ago(time_ago, ref_dt, ref_date)
                        items.append({
                            'title': title,
                            'summary': summary,
                            'source': source,
                            'sourceUrl': '',
                            'publishedAt': resolve_to_iso(item_time),
                            'importance': 5,
                        })
                        i += 2
                        continue

        # 情况 B: 本块末尾有时间 → 独立条目（首行作标题）
        if TIME_RX.search(block[-1]):
            title = block[0]
            if len(title) >= 6 and not any(kw in title for kw in SKIP_KW):
                time_ago = block[-1]
                source = block[-2] if len(block) >= 2 else ''
                summary = block[1] if len(block) >= 4 else ''
                if not any(kw in source for kw in SKIP_KW):
                    item_time = parse_time_ago(time_ago, ref_dt, ref_date)
                    items.append({
                        'title': title,
                        'summary': summary,
                        'source': source,
                        'sourceUrl': '',
                        'publishedAt': resolve_to_iso(item_time),
                        'importance': 5,
                    })

        i += 1

    return items


# ── 钛媒体 AGI accessibility snapshot 解析 ──

def parse_tmtpost_text(lines, ref_dt, ref_date):
    """
    变长模式解析，按信号行驱动：
    - 「· N分钟前/· M月D日」→ 时间，闭合当前条目
    - 非时间、非空的行 → 累积到当前条目
    - heading / paragraph 行 → 跳过
    """
    items = []
    link_lines = []
    for line in lines:
        m = re.match(r'link\s+"(.+)"', line)
        if m:
            text = m.group(1).strip()
            if text and text != 'null':
                link_lines.append(text)

    TIME_RE = re.compile(r'^·\s*(\d+分钟前|\d+小时前|昨天|\d{1,2}月\d{1,2}日|\d{4}-\d{2}-\d{2})')
    SKIP_RE = re.compile(r'^(heading|paragraph|link\s+)')

    current = {'title': '', 'summary': '', 'source': '', '_subtitle': '', 'lines': []}

    def flush_item():
        if not current['title']:
            return
        it = {
            'title': current['title'],
            'summary': current.get('summary', ''),
            'source': current.get('source', ''),
            'sourceUrl': '',
            'publishedAt': current.get('publishedAt', ''),
            'importance': 5,
        }
        # 清理：如果 source 是时间或数字，不要作为 source
        if re.match(r'^[\d.]+万?$', it['source']) or re.match(r'^·\s', it['source']):
            it['source'] = ''
        # 兜底 source
        if not it['source']:
            it['source'] = '钛媒体 AGI'
        items.append(it)

    for text in link_lines:
        # 跳过纯数字/阅读量行（不当作标题）
        if re.match(r'^[\d.]+万?$', text) and not re.search(r'分钟前|小时前|昨天|月\d+日', text):
            continue

        tm = TIME_RE.match(text)
        if tm:
            # 这是一个时间行 → 闭合当前条目
            time_str = tm.group(1)
            item_time = parse_time_ago(time_str, ref_dt, ref_date)
            current['publishedAt'] = resolve_to_iso(item_time)
            # 上一条累积的 lines 中最后一个非标题非时间的内容作为 source
            if not current['source'] and len(current['lines']) >= 2:
                # source 一般在倒数第二个位置（如果有 subtitle）
                src_candidates = [l for l in current['lines'] if l != current['title']
                                  and not TIME_RE.match(l)
                                  and not re.match(r'^[\d.]+万$', l)]
                for c in src_candidates:
                    if c != current.get('_subtitle', ''):
                        current['source'] = c
                        break
            flush_item()
            current = {'title': '', 'summary': '', 'source': '', '_subtitle': '', 'lines': []}
        else:
            # 非时间行 → 累积
            if not current['title']:
                current['title'] = text
            elif not current['_subtitle'] and len(text) > 8 and text != current['title']:
                current['_subtitle'] = text
                current['summary'] = text
            else:
                if not current['source'] and len(text) > 1 and not re.match(r'^[\d.]+万$', text):
                    current['source'] = text
            current['lines'].append(text)

    # 最后一条
    if current['title']:
        if not current['publishedAt'] and current['lines']:
            for l in reversed(current['lines']):
                tm = TIME_RE.match(l)
                if tm:
                    item_time = parse_time_ago(tm.group(1), ref_dt, ref_date)
                    current['publishedAt'] = resolve_to_iso(item_time)
                    break
        flush_item()

    return items


# ── Edge AI Daily 文章正文解析 ──

def parse_edge_daily_text(text, ref_dt, ref_date):
    items = []
    lines = text.strip().split('\n')

    # 提取文章发布时间（首行 "2026.07.12 08:36"）
    article_time = None
    first_line = lines[0].strip() if lines else ''
    m = re.match(r'(\d{4})\.(\d{2})\.(\d{2})\s+(\d{2}):(\d{2})', first_line)
    if m:
        y, mo, d, h, mi = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5))
        article_time = datetime(y, mo, d, h, mi, tzinfo=TZ_CST)

    if not article_time:
        article_time = ref_dt

    # 匹配 "一、..." / "二、..." 等中文序号标题
    section_titles = re.findall(r'^[一二三四五六七八九十]+、(.+)$', text, re.MULTILINE)
    section_bodies = re.split(r'^[一二三四五六七八九十]+、', text, flags=re.MULTILINE)

    if len(section_titles) == len(section_bodies) - 1:
        bodies = section_bodies[1:]
        for idx, (title, body) in enumerate(zip(section_titles, bodies)):
            body_lines = [l.strip() for l in body.strip().split('\n') if l.strip()]
            summary = re.sub(r'^\d+[.．、]\s*', '', body_lines[0]) if body_lines else ''
            item_time = article_time + timedelta(minutes=idx * 2)

            items.append({
                'title': title.strip(),
                'summary': summary[:100],
                'source': 'Edge AI Daily',
                'sourceUrl': '',
                'publishedAt': resolve_to_iso(item_time),
                'importance': 5,
            })

    return items


# ── The Verge 文本摘要解析 ──

def parse_verge_txt_entries(lines, ref_dt, ref_date):
    items = []
    current = {}
    for line in lines:
        line = line.rstrip()

        if re.match(r'^Entry\s+\d+:', line):
            if current.get('title'):
                items.append(current)
            current = {}
            continue

        if line.startswith('Title: '):
            current['title'] = line[7:].strip()
        elif line.startswith('Published: '):
            dt = parse_iso_datetime(line[11:].strip())
            if dt:
                current['publishedAt'] = resolve_to_iso(dt)
        elif line.startswith('Link: '):
            current['sourceUrl'] = line[6:].strip()
        elif line.startswith('Author: '):
            current['source'] = line[8:].strip()
        elif line.startswith('Summary: '):
            current['summary'] = line[9:].strip()
        elif line.startswith('Categories: '):
            current['tags'] = [t.strip() for t in line[12:].split(',')]

    if current.get('title'):
        items.append(current)

    for item in items:
        item.setdefault('summary', '')
        item.setdefault('source', 'The Verge')
        item.setdefault('sourceUrl', '')
        item.setdefault('publishedAt', '')
        item.setdefault('importance', 5)

    return items


# ── The Verge RSS XML 解析 ──

def parse_verge_xml(filepath, ref_date):
    items = []
    tree = ET.parse(filepath)
    root = tree.getroot()

    ns = {'atom': 'http://www.w3.org/2005/Atom'}

    for entry in root.findall('atom:entry', ns):
        title_el = entry.find('atom:title', ns)
        pub_el = entry.find('atom:published', ns)
        link_el = entry.find('atom:link', ns)
        summary_el = entry.find('atom:summary', ns)
        author_el = entry.find('atom:author', ns)

        title = html.unescape(title_el.text) if title_el is not None and title_el.text else ''
        published = ''
        if pub_el is not None and pub_el.text:
            dt = parse_iso_datetime(pub_el.text)
            if dt:
                published = resolve_to_iso(dt)
        url = link_el.get('href', '') if link_el is not None else ''
        summary = html.unescape(summary_el.text.strip()) if summary_el is not None and summary_el.text else ''
        author = ''
        if author_el is not None:
            name_el = author_el.find('atom:name', ns)
            if name_el is not None and name_el.text:
                author = name_el.text

        items.append({
            'title': title,
            'summary': summary,
            'source': author or 'The Verge',
            'sourceUrl': url,
            'publishedAt': published,
            'importance': 5,
        })

    return items


# ── JSON 已加工数据解析 ──

def parse_json_input(data, ref_dt, ref_date, date_str):
    source_category_map = {
        '36kr_ai': 'domestic',
        'tmtpost_agi': 'domestic',
        'edge_ai_daily': 'domestic',
        'the_verge_rss': 'international',
    }

    items = []
    sources = data.get('sources', {})
    if sources:
        for src_key, src_data in sources.items():
            src_name = src_data.get('name', src_key)
            cat = source_category_map.get(src_key, 'international')
            for item in src_data.get('items', []):
                published = ''
                for field in ('publishedAt', 'published_utc'):
                    v = item.get(field)
                    if v:
                        dt = parse_iso_datetime(v)
                        if dt:
                            published = resolve_to_iso(dt)
                            break
                if not published and 'time_ago' in item:
                    dt = parse_time_ago(item['time_ago'], ref_dt, ref_date)
                    if dt:
                        published = resolve_to_iso(dt)

                items.append({
                    'title': item.get('title', ''),
                    'summary': item.get('summary', item.get('subtitle', '')),
                    'source': src_name,
                    'sourceUrl': item.get('url', item.get('sourceUrl', '')),
                    'category': cat,
                    'publishedAt': published,
                    'importance': item.get('importance', 5),
                })

    if not items:
        for item in data.get('items', []):
            published = ''
            for field in ('publishedAt', 'published_utc', 'published_at'):
                v = item.get(field)
                if v:
                    dt = parse_iso_datetime(v)
                    if dt:
                        published = resolve_to_iso(dt)
                        break
            if not published:
                v = item.get('time_ago')
                if v:
                    dt = parse_time_ago(v, ref_dt, ref_date)
                    if dt:
                        published = resolve_to_iso(dt)

            items.append({
                'title': item.get('title', ''),
                'summary': item.get('summary', ''),
                'source': item.get('source', ''),
                'sourceUrl': item.get('sourceUrl', item.get('url', '')),
                'category': item.get('category', 'international'),
                'publishedAt': published,
                'importance': item.get('importance', 5),
            })

    return items


# ── 主流程 ──

def detect_format(filepath, content):
    if filepath and filepath.endswith('.xml'):
        return 'xml'
    if filepath and filepath.endswith('.json'):
        return 'json'
    s = content.strip()
    if s.startswith('{') or s.startswith('['):
        return 'json'
    if s.startswith('<?xml') or s.startswith('<feed'):
        return 'xml'
    if '数据源 #' in content:
        return 'raw_txt'
    return 'raw_txt'


def parse_raw_txt(text, ref_dt, ref_date):
    all_items = []
    # 按数据源分节
    section_starts = [m.start() for m in re.finditer(r'^数据源 #\d:', text, re.MULTILINE)]
    section_texts = []
    for i, start in enumerate(section_starts):
        end = section_starts[i + 1] if i + 1 < len(section_starts) else len(text)
        section_texts.append(text[start:end])

    for sec_text in section_texts:
        sec_lines = sec_text.split('\n')
        name_line = sec_lines[0] if sec_lines else ''

        if '36氪 AI板块' in name_line:
            src_items = parse_36kr_text(sec_lines, ref_dt, ref_date)
            for it in src_items:
                it['category'] = 'domestic'
            all_items.extend(src_items)
            print(f"  📰 36氪: 解析 {len(src_items)} 条", file=sys.stderr)

        elif '钛媒体 AGI专栏' in name_line:
            src_items = parse_tmtpost_text(sec_lines, ref_dt, ref_date)
            for it in src_items:
                it['category'] = 'domestic'
            all_items.extend(src_items)
            print(f"  📰 钛媒体 AGI: 解析 {len(src_items)} 条", file=sys.stderr)

        elif 'Edge AI Daily' in name_line:
            src_items = parse_edge_daily_text(sec_text, ref_dt, ref_date)
            for it in src_items:
                it['category'] = 'domestic'
            all_items.extend(src_items)
            print(f"  📰 Edge AI Daily: 解析 {len(src_items)} 条", file=sys.stderr)

        elif 'The Verge' in name_line:
            src_items = parse_verge_txt_entries(sec_lines, ref_dt, ref_date)
            for it in src_items:
                it['category'] = 'international'
            all_items.extend(src_items)
            print(f"  📰 The Verge: 解析 {len(src_items)} 条", file=sys.stderr)

    return all_items


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = None
    override_date = None
    ref_hour = 8

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--output' and i + 1 < len(sys.argv):
            output_path = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--date' and i + 1 < len(sys.argv):
            override_date = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--hour' and i + 1 < len(sys.argv):
            ref_hour = int(sys.argv[i + 1])
            i += 2
        else:
            i += 1

    # 读取输入
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    fmt = detect_format(input_path, content)
    print(f"\n📐 格式化工具", file=sys.stderr)
    print(f"{'='*45}", file=sys.stderr)
    print(f"  输入: {input_path}", file=sys.stderr)
    print(f"  检测格式: {fmt}", file=sys.stderr)

    # 确定参考日期
    date_str = override_date
    if not date_str:
        if fmt == 'json':
            try:
                date_str = json.loads(content).get('meta', {}).get('date', '')
            except json.JSONDecodeError:
                pass
        if not date_str:
            m = re.search(r'(\d{4})-(\d{2})-(\d{2})', content)
            if m:
                date_str = m.group(0)
        if not date_str:
            m = re.search(r'(\d{8})', input_path)
            if m:
                d = m.group(1)
                date_str = f'{d[:4]}-{d[4:6]}-{d[6:8]}'

    if not date_str:
        print("错误: 无法确定参考日期，请用 --date 指定", file=sys.stderr)
        sys.exit(1)

    ref_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    ref_dt = datetime(ref_date.year, ref_date.month, ref_date.day, ref_hour, 0, 0, tzinfo=TZ_CST)

    items = []
    if fmt == 'raw_txt':
        items = parse_raw_txt(content, ref_dt, ref_date)
    elif fmt == 'xml':
        items = parse_verge_xml(input_path, ref_date)
        for it in items:
            it['category'] = 'international'
        print(f"  📰 The Verge RSS: 解析 {len(items)} 条", file=sys.stderr)
    elif fmt == 'json':
        data = json.loads(content)
        items = parse_json_input(data, ref_dt, ref_date, date_str)
        print(f"  📰 JSON: 提取 {len(items)} 条", file=sys.stderr)

    domestic = sum(1 for i in items if i.get('category') == 'domestic')
    internat = sum(1 for i in items if i.get('category') == 'international')
    has_time = sum(1 for i in items if i.get('publishedAt'))
    no_time = sum(1 for i in items if not i.get('publishedAt'))

    print(f"  {'─'*45}", file=sys.stderr)
    print(f"  总计: {len(items)} 条", file=sys.stderr)
    print(f"  国内: {domestic} 条 / 国际: {internat} 条", file=sys.stderr)
    print(f"  有时间: {has_time} 条 / 无时间: {no_time} 条", file=sys.stderr)
    print(file=sys.stderr)

    output = {
        'meta': {
            'date': date_str,
            'collection_time': f'{date_str} {ref_hour:02d}:{ref_hour*7 % 60:02d}+08:00',
        },
        'items': items,
    }

    output_json = json.dumps(output, ensure_ascii=False, indent=2)

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_json)
        print(f"  已写入: {output_path}", file=sys.stderr)
    else:
        print(output_json)

    print(file=sys.stderr)


if __name__ == '__main__':
    main()
