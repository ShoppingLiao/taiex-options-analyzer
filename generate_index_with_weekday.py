#!/usr/bin/env python3
"""
生成首頁 index.html
動態掃描 docs/ 目錄中的所有報告檔案
"""

from datetime import datetime
from pathlib import Path
import re


def get_weekday_chinese(date_str: str) -> str:
    """將 YYYYMMDD 轉換為中文星期"""
    try:
        date_obj = datetime.strptime(date_str, '%Y%m%d')
        weekdays = ['一', '二', '三', '四', '五', '六', '日']
        return weekdays[date_obj.weekday()]
    except:
        return ""


def format_date_display(date_str: str) -> str:
    """格式化日期顯示 YYYY/MM/DD (週X)"""
    try:
        date_obj = datetime.strptime(date_str, '%Y%m%d')
        weekday = get_weekday_chinese(date_str)
        return f"{date_obj.strftime('%Y/%m/%d')} (週{weekday})"
    except:
        return date_str


def scan_daily_reports() -> list:
    """掃描每日報告檔案"""
    docs_dir = Path('docs')
    daily_reports = []

    # 查找 report_*.html 檔案（排除 _old 和週選 W 開頭的契約）
    for html_file in docs_dir.glob('report_*.html'):
        # 跳過 old 檔案
        if '_old' in html_file.name:
            continue

        # 解析檔名: report_20260109_202601.html 或 report_20260109_202601W2.html
        match = re.match(r'report_(\d{8})_(\d{6})(W\d)?\.html', html_file.name)
        if match:
            date_str = match.group(1)
            contract = match.group(2)
            week_contract = match.group(3)  # 可能是 None 或 W1, W2 等

            # 優先顯示月契約，週契約作為次要
            is_weekly = week_contract is not None

            daily_reports.append({
                'filename': html_file.name,
                'date': date_str,
                'contract': contract + (week_contract or ''),
                'is_weekly': is_weekly,
                'display_date': format_date_display(date_str),
            })

    # 按日期排序（最新的在前），月契約優先於週契約
    daily_reports.sort(key=lambda x: (x['date'], not x['is_weekly']), reverse=True)

    # 移除重複日期（保留月契約優先）
    seen_dates = set()
    unique_reports = []
    for report in daily_reports:
        if report['date'] not in seen_dates:
            seen_dates.add(report['date'])
            unique_reports.append(report)

    return unique_reports


def scan_settlement_reports() -> list:
    """掃描結算日報告檔案"""
    docs_dir = Path('docs')
    settlement_reports = []

    # 查找 settlement_*.html 檔案
    for html_file in docs_dir.glob('settlement_*.html'):
        # 解析檔名: settlement_20260108_wed.html
        match = re.match(r'settlement_(\d{8})_(wed|fri)\.html', html_file.name)
        if match:
            date_str = match.group(1)
            weekday_abbr = match.group(2)
            weekday_text = '週三' if weekday_abbr == 'wed' else '週五'

            # 格式化日期
            try:
                date_obj = datetime.strptime(date_str, '%Y%m%d')
                formatted_date = date_obj.strftime('%Y/%m/%d')
            except:
                formatted_date = date_str

            settlement_reports.append({
                'filename': html_file.name,
                'date': date_str,
                'formatted_date': formatted_date,
                'weekday_text': weekday_text,
                'weekday_abbr': weekday_abbr,
            })

    # 按日期排序（最新的在前）
    settlement_reports.sort(key=lambda x: x['date'], reverse=True)

    return settlement_reports


def generate_index_html():
    """生成首頁 HTML"""
    # 掃描報告
    daily_reports = scan_daily_reports()
    settlement_reports = scan_settlement_reports()

    # 當前時間
    now = datetime.now().strftime('%Y年%m月%d日 %H:%M')

    # 生成 HTML
    html_content = f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>台指選擇權分析報告 - 總覽</title>
    <style>
        :root {{
            --primary-color: #2563eb;
            --bg-color: #f8fafc;
            --card-bg: #ffffff;
            --text-color: #1e293b;
            --border-color: #e2e8f0;
        }}
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: var(--bg-color);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        header {{
            background: linear-gradient(135deg, var(--primary-color), #1d4ed8);
            color: white;
            border-radius: 2px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            text-align: center;
        }}
        h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
        }}
        .subtitle {{
            opacity: 0.9;
            font-size: 1.1rem;
        }}

        /* 報告類型區塊 */
        .report-section {{
            background: white;
            border-radius: 2px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            border: 1px solid var(--border-color);
        }}

        .section-header {{
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid var(--border-color);
        }}

        .section-icon {{
            font-size: 1.8rem;
            margin-right: 12px;
        }}

        .section-title {{
            font-size: 1.5rem;
            font-weight: 700;
            color: #1e293b;
            margin: 0;
        }}

        .section-count {{
            margin-left: auto;
            background: #f1f5f9;
            color: #64748b;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.9rem;
            font-weight: 600;
        }}

        .section-description {{
            color: #64748b;
            margin-bottom: 20px;
            font-size: 0.95rem;
        }}

        .reports-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 16px;
        }}

        .report-card {{
            background: var(--bg-color);
            border-radius: 2px;
            padding: 20px;
            border: 1px solid var(--border-color);
            transition: all 0.3s ease;
            text-decoration: none;
            color: var(--text-color);
            display: block;
        }}
        .report-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            border-color: var(--primary-color);
        }}
        .report-date {{
            font-size: 1.3rem;
            font-weight: 700;
            margin-bottom: 8px;
            color: var(--primary-color);
        }}
        .report-month {{
            font-size: 0.9rem;
            color: #64748b;
            margin-bottom: 8px;
        }}
        .report-badge {{
            display: inline-block;
            background: var(--primary-color);
            color: white;
            padding: 3px 10px;
            border-radius: 2px;
            font-size: 0.8rem;
        }}
        .latest-badge {{
            background: #ef4444;
        }}

        /* 空狀態 */
        .empty-state {{
            text-align: center;
            padding: 40px 20px;
            color: #94a3b8;
        }}
        .empty-state-icon {{
            font-size: 3rem;
            margin-bottom: 12px;
            opacity: 0.5;
        }}

        footer {{
            text-align: center;
            color: #64748b;
            margin-top: 40px;
            padding: 20px;
            font-size: 0.9rem;
        }}
        footer a {{
            color: var(--primary-color);
            text-decoration: none;
        }}
        footer a:hover {{
            text-decoration: underline;
        }}

        @media (max-width: 768px) {{
            h1 {{
                font-size: 1.8rem;
            }}
            .reports-grid {{
                grid-template-columns: 1fr;
            }}
            header {{
                padding: 24px 16px;
            }}
            .report-section {{
                padding: 20px 16px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>台指選擇權分析報告</h1>
            <p class="subtitle">Taiwan Stock Index Options Analysis</p>
        </header>

        <!-- 每日報告區塊 -->
        <div class="report-section">
            <div class="section-header">
                <span class="section-icon">📊</span>
                <h2 class="section-title">每日報告</h2>
                <span class="section-count">{len(daily_reports)} 份報告</span>
            </div>
            <p class="section-description">每日選擇權市場分析，包含 OI 分佈、Max Pain、結算情境預測等</p>
            <div class="reports-grid">
'''

    # 每日報告卡片
    for i, report in enumerate(daily_reports):
        badge_class = 'latest-badge' if i == 0 else ''
        badge_text = '最新' if i == 0 else '歷史'
        contract_display = report['contract'][:6] + ' 月份'
        if 'W' in report['contract']:
            contract_display = report['contract'] + ' 週選'

        html_content += f'''                <a href="{report['filename']}" class="report-card">
                    <div class="report-date">{report['display_date']}</div>
                    <div class="report-month">{contract_display}</div>
                    <span class="report-badge {badge_class}">{badge_text}</span>
                </a>
'''

    html_content += '''            </div>
        </div>

        <!-- 結算日報告區塊 -->
        <div class="report-section">
            <div class="section-header">
                <span class="section-icon">🎯</span>
                <h2 class="section-title">結算日報告</h2>
                <span class="section-count">''' + (f'{len(settlement_reports)} 份報告' if settlement_reports else '即將推出') + '''</span>
            </div>
            <p class="section-description">結算日專題分析，包含趨勢分析、結算劇本預測、AI 交易員視角等</p>
'''

    if settlement_reports:
        html_content += '''            <div class="reports-grid">
'''
        for i, report in enumerate(settlement_reports):
            badge_class = 'latest-badge' if i == 0 else ''
            badge_text = '最新' if i == 0 else '歷史'

            html_content += f'''                <a href="{report['filename']}" class="report-card">
                    <div class="report-date">{report['formatted_date']} ({report['weekday_text']})</div>
                    <div class="report-month">結算日預測分析</div>
                    <span class="report-badge {badge_class}">{badge_text}</span>
                </a>
'''
        html_content += '''            </div>
'''
    else:
        html_content += '''            <div class="empty-state">
                <div class="empty-state-icon">📦</div>
                <div>尚無結算日報告</div>
            </div>
'''

    html_content += f'''        </div>

        <footer>
            <p>自動生成於 {now}</p>
            <p><a href="https://github.com/ShoppingLiao/taiex-options-analyzer" target="_blank">GitHub 專案原始碼</a></p>
        </footer>
    </div>
</body>
</html>
'''

    # 寫入檔案
    output_path = Path('docs/index.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return daily_reports, settlement_reports


def main():
    """主函數"""
    print("=" * 50)
    print("首頁生成工具")
    print("=" * 50)

    daily_reports, settlement_reports = generate_index_html()

    print(f"\n✅ 首頁已更新: docs/index.html")
    print(f"\n📊 每日報告 ({len(daily_reports)} 份):")
    for i, report in enumerate(daily_reports[:5]):  # 只顯示前 5 個
        print(f"  {'⭐' if i == 0 else '  '} {report['display_date']}")
    if len(daily_reports) > 5:
        print(f"  ... 還有 {len(daily_reports) - 5} 份")

    print(f"\n🎯 結算日報告 ({len(settlement_reports)} 份):")
    for i, report in enumerate(settlement_reports):
        print(f"  {'⭐' if i == 0 else '  '} {report['formatted_date']} ({report['weekday_text']})")


if __name__ == '__main__':
    main()
