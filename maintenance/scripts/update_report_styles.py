#!/usr/bin/env python3
"""
更新已生成報告的樣式腳本
將模板中最新的 CSS 樣式套用到已生成的報告
"""

import re
from pathlib import Path


def extract_css_from_template(template_path: Path) -> str:
    """從模板檔案中提取 CSS 內容"""
    content = template_path.read_text(encoding='utf-8')

    # 匹配 <style>...</style> 區塊
    match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
    if match:
        return match.group(1)
    return ""


def update_report_css(report_path: Path, new_css: str) -> bool:
    """更新報告中的 CSS"""
    content = report_path.read_text(encoding='utf-8')

    # 替換 <style>...</style> 區塊
    new_content = re.sub(
        r'<style>.*?</style>',
        f'<style>{new_css}</style>',
        content,
        flags=re.DOTALL
    )

    if new_content != content:
        report_path.write_text(new_content, encoding='utf-8')
        return True
    return False


def update_settlement_html_structure(report_path: Path) -> bool:
    """更新結算日報告的 HTML Tab 結構"""
    content = report_path.read_text(encoding='utf-8')
    original = content

    # 替換 Tab 容器結構
    # 從 <div class="tabs-container"><div class="tabs-header"> 改為 <div class="tabs">
    content = re.sub(
        r'<div class="tabs-container">\s*<div class="tabs-header">',
        '<div class="tabs">',
        content
    )

    # 移除 </div></div> 中多餘的一層（tabs-header 的閉合標籤）
    # 找到 tabs-header 閉合後緊接著 tabs-container 閉合的地方
    content = re.sub(
        r'</div>\s*</div>(\s*<!--\s*Technical Analysis Tab\s*-->)',
        r'</div>\1',
        content
    )

    # 移除 <span class="tab-icon">...</span>，直接把 emoji 放在按鈕文字中
    content = re.sub(
        r'<span class="tab-icon">([^<]+)</span>',
        r'\1 ',
        content
    )

    # 替換 CSS 變數名稱（如果有殘留）
    content = content.replace('var(--success-color)', 'var(--put-color)')
    content = content.replace('var(--danger-color)', 'var(--call-color)')

    if content != original:
        report_path.write_text(content, encoding='utf-8')
        return True
    return False


def main():
    # 專案根目錄
    project_root = Path(__file__).parent.parent.parent
    docs_dir = project_root / 'docs'
    templates_dir = project_root / 'templates'

    # 讀取模板 CSS
    daily_template = templates_dir / 'report.html'
    settlement_template = templates_dir / 'settlement_report.html'

    daily_css = extract_css_from_template(daily_template)
    settlement_css = extract_css_from_template(settlement_template)

    print("=" * 60)
    print("報告樣式更新工具")
    print("=" * 60)

    # 統計
    updated_daily = 0
    updated_settlement = 0
    skipped = 0

    # 遍歷所有報告
    for report_file in docs_dir.glob('*.html'):
        # 跳過 index 和其他非報告檔案
        if report_file.name in ['index.html', 'rwd_demo.html']:
            skipped += 1
            continue

        # 判斷報告類型
        if report_file.name.startswith('settlement_'):
            # 結算日報告
            css_updated = update_report_css(report_file, settlement_css)
            html_updated = update_settlement_html_structure(report_file)

            if css_updated or html_updated:
                updated_settlement += 1
                print(f"✅ 已更新: {report_file.name}")
            else:
                print(f"⏭️  無變更: {report_file.name}")

        elif report_file.name.startswith('report_'):
            # 每日報告
            if update_report_css(report_file, daily_css):
                updated_daily += 1
                print(f"✅ 已更新: {report_file.name}")
            else:
                print(f"⏭️  無變更: {report_file.name}")
        else:
            skipped += 1
            print(f"⏭️  跳過: {report_file.name}")

    print()
    print("=" * 60)
    print("更新完成！")
    print(f"  每日報告更新: {updated_daily} 個")
    print(f"  結算日報告更新: {updated_settlement} 個")
    print(f"  跳過: {skipped} 個")
    print("=" * 60)


if __name__ == '__main__':
    main()
