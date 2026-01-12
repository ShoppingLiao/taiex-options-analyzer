#!/usr/bin/env python3
"""
生成帶星期的首頁 index.html
"""

from datetime import datetime
from pathlib import Path

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
        return f"{date_obj.strftime('%Y/%m/%d')} ({weekday})"
    except:
        return date_str

# 報告日期列表
reports = [
    ('20260109', True),   # (日期, 是否最新)
    ('20260108', False),
    ('20260107', False),
    ('20260106', False),
    ('20260105', False),
]

# 生成 HTML
html_content = '''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>台指選擇權分析報告 - 總覽</title>
    <style>
        :root {
            --primary-color: #2563eb;
            --bg-color: #f8fafc;
            --card-bg: #ffffff;
            --text-color: #1e293b;
            --border-color: #e2e8f0;
        }
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        header {
            background: white;
            border-radius: 16px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        h1 {
            font-size: 2.5rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #64748b;
            font-size: 1.1rem;
        }
        
        /* 報告類型區塊 */
        .report-section {
            background: white;
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        
        .section-header {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e2e8f0;
        }
        
        .section-icon {
            font-size: 1.8rem;
            margin-right: 12px;
        }
        
        .section-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #1e293b;
            margin: 0;
        }
        
        .section-count {
            margin-left: auto;
            background: #f1f5f9;
            color: #64748b;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.9rem;
            font-weight: 600;
        }
        
        .section-description {
            color: #64748b;
            margin-bottom: 20px;
            font-size: 0.95rem;
        }
        
        .reports-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }
        
        /* 空狀態提示 */
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #94a3b8;
        }
        
        .empty-state-icon {
            font-size: 4rem;
            margin-bottom: 16px;
            opacity: 0.5;
        }
        
        .empty-state-text {
            font-size: 1.1rem;
            margin-bottom: 8px;
        }
        
        .empty-state-hint {
            font-size: 0.9rem;
            color: #cbd5e1;
        }
        
        .reports-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .report-card {
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
            text-decoration: none;
            color: var(--text-color);
            display: block;
        }
        .report-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
        }
        .report-date {
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 8px;
            color: #2563eb;
        }
        .report-month {
            font-size: 0.95rem;
            color: #64748b;
            margin-bottom: 4px;
        }
        .report-badge {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85rem;
            margin-top: 8px;
        }
        .latest-badge {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        footer {
            text-align: center;
            color: white;
            margin-top: 40px;
            padding: 20px;
        }
        footer a {
            color: white;
            text-decoration: underline;
        }
        @media (max-width: 768px) {
            h1 {
                font-size: 1.8rem;
            }
            .reports-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 台指選擇權分析報告</h1>
            <p class="subtitle">Taiwan Stock Index Options Analysis</p>
        </header>
        
        <!-- 單日報告區塊 -->
        <div class="report-section">
            <div class="section-header">
                <span class="section-icon">📅</span>
                <h2 class="section-title">單日報告</h2>
                <span class="section-count">''' + str(len(reports)) + ''' 份報告</span>
            </div>
            <p class="section-description">每日選擇權市場分析，包含 OI 分佈、價格走勢、結算情境預測等詳細資訊</p>
            <div class="reports-grid">
'''

# 加入報告卡片
for date_str, is_latest in reports:
    display_date = format_date_display(date_str)
    badge_class = 'latest-badge' if is_latest else ''
    badge_text = '最新報告' if is_latest else '歷史報告'
    
    html_content += f'''                <a href="report_{date_str}_202601.html" class="report-card">
                    <div class="report-date">{display_date}</div>
                    <div class="report-month">202601 月份契約</div>
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
                <span class="section-count">即將推出</span>
            </div>
            <p class="section-description">選擇權結算日專題分析，包含結算價預測、莊家佈局、歷史結算統計等深度內容</p>
            <div class="empty-state">
                <div class="empty-state-icon">📦</div>
                <div class="empty-state-text">結算日報告功能開發中</div>
                <div class="empty-state-hint">敬請期待更深入的結算日分析內容</div>
            </div>
        </div>
        
        <footer>
            <p>🚀 自動生成於 2026年1月12日</p>
            <p><a href="https://github.com/ShoppingLiao/taiex-options-analyzer" target="_blank">查看專案原始碼</a></p>
        </footer>
    </div>
</body>
</html>
'''

# 寫入檔案
output_path = Path('docs/index.html')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"✅ 首頁已更新: {output_path}")
print("\n報告日期與星期：")
for date_str, is_latest in reports:
    print(f"  {'⭐' if is_latest else '  '} {format_date_display(date_str)}")
