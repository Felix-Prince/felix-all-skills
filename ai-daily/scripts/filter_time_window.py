#!/usr/bin/env python3
"""
ai-daily: 时间窗口过滤器 (filter_time_window.py)

从标准化的 JSON 数据中过滤出 24 小时时间窗口内的条目。
输入必须是 format_data.py 输出的标准格式（每条含 publishedAt ISO 8601）。

用法：
    python3 filter_time_window.py <input.json> [选项]
    python3 filter_time_window.py <input.json> --output <output.json>

选项：
    --hour HH            参考时间点（默认 8，即上午 8 点）
    --output PATH        输出路径（默认覆盖原文件）
    --min-items N        保留无时间信息条目的阈值（默认 10）

时间窗口规则：
    1. 以 meta.date 为参考日期，确定当天 HH:00 为参考时间
    2. 窗口 = [参考时间 - 24h, 参考时间]
       例: date=2026-07-12, hour=8 → [2026-07-11 08:00, 2026-07-12 08:00]
    3. publishedAt 在窗口内 → 保留
    4. publishedAt 在窗口外 → 过滤
    5. 无 publishedAt 的条目：
       - 窗口内有效条目 ≥ min-items → 排除
       - 窗口内有效条目 < min-items  → 保留（兜底）
"""

import json
import re
import sys
from datetime import datetime, timedelta, timezone

TZ_CST = timezone(timedelta(hours=8))


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


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    ref_hour = 8
    output_path = None
    min_items_keep = 10

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--hour' and i + 1 < len(sys.argv):
            ref_hour = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--output' and i + 1 < len(sys.argv):
            output_path = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--min-items' and i + 1 < len(sys.argv):
            min_items_keep = int(sys.argv[i + 1])
            i += 2
        else:
            i += 1

    # 读取数据
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    meta = data.get('meta', {})
    items = data.get('items', [])

    if not items:
        print("错误: 数据中无 items", file=sys.stderr)
        sys.exit(1)

    # 确定参考时间
    date_str = meta.get('date')
    if not date_str:
        # 从第一条的 publishedAt 中提取日期
        for it in items:
            if it.get('publishedAt'):
                dt = parse_iso_datetime(it['publishedAt'])
                if dt:
                    date_str = dt.strftime('%Y-%m-%d')
                    break
    if not date_str:
        print("错误: 无法确定参考日期，meta.date 不存在且 items 无 publishedAt", file=sys.stderr)
        sys.exit(1)

    ref_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    ref_datetime = datetime(ref_date.year, ref_date.month, ref_date.day, ref_hour, 0, 0, tzinfo=TZ_CST)
    window_start = ref_datetime - timedelta(hours=24)
    window_end = ref_datetime

    # ---- 分类 ----
    within = []
    timeout = []
    unknown = []

    for item in items:
        pub = item.get('publishedAt')
        if not pub:
            unknown.append(item)
            continue

        dt = parse_iso_datetime(pub)
        if dt is None:
            unknown.append(item)
            continue

        if window_start <= dt <= window_end:
            within.append(item)
        else:
            timeout.append(item)

    # ---- 无时间条目兜底决策 ----
    excluded_items_report = []
    if unknown:
        if len(within) >= min_items_keep:
            excluded_items_report = [
                {'title': it.get('title', '(无标题)'), 'reason': '无时间信息'}
                for it in unknown
            ]
            # unknown items are discarded
        else:
            within.extend(unknown)
            print(f"  ⚠️  有效条目不足 {min_items_keep} 条，保留 {len(unknown)} 条无时间条目补数",
                  file=sys.stderr)

    # ---- 输出报告 ----
    total = len(items)
    print(f"\n⏰ 时间窗口过滤器", file=sys.stderr)
    print(f"{'='*50}", file=sys.stderr)
    print(f"  参考日期:  {date_str}", file=sys.stderr)
    print(f"  窗口范围:  {window_start}  ~  {window_end}", file=sys.stderr)
    print(f"  {'─'*45}", file=sys.stderr)
    print(f"  总条数:     {total:4d}", file=sys.stderr)
    print(f"  窗口内:     {len(within):4d}", file=sys.stderr)
    print(f"  超时排除:   {len(timeout):4d}", file=sys.stderr)
    print(f"  时间未知:   {len(unknown):4d}", file=sys.stderr)
    print(f"  {'─'*45}", file=sys.stderr)
    print(f"  ✅ 有效条目: {len(within)} 条", file=sys.stderr)

    if len(within) == 0:
        print(f"\n  ❌ 无有效数据在时间窗口内，终止处理。", file=sys.stderr)
        sys.exit(1)

    if timeout:
        print(f"\n  排除条目 ({len(timeout)}):", file=sys.stderr)
        for it in timeout[:15]:
            title = it.get('title', '(无标题)')[:35]
            pub = it.get('publishedAt', '')
            print(f"    · {title:<35s}  {pub[:19]}", file=sys.stderr)
        if len(timeout) > 15:
            print(f"    · ... 还有 {len(timeout)-15} 条", file=sys.stderr)

    if excluded_items_report:
        print(f"\n  无时间排除 ({len(excluded_items_report)}):", file=sys.stderr)
        for it in excluded_items_report:
            print(f"    · {it['title'][:40]}", file=sys.stderr)

    print(file=sys.stderr)

    # ---- 构建输出 ----
    output = dict(data)
    output['items'] = within
    output['total'] = len(within)

    _filter_info = {
        'applied': True,
        'window_start': window_start.isoformat(),
        'window_end': window_end.isoformat(),
        'within_window': len(within),
        'excluded_timeout': len(timeout),
        'excluded_unknown': len(excluded_items_report),
    }
    output['_filter_info'] = _filter_info

    output_json = json.dumps(output, ensure_ascii=False, indent=2)

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output_json)
        print(f"  已写入: {output_path}", file=sys.stderr)
    else:
        with open(input_path, 'w', encoding='utf-8') as f:
            f.write(output_json)
        print(f"  已更新: {input_path}", file=sys.stderr)

    print(file=sys.stderr)


if __name__ == '__main__':
    main()
