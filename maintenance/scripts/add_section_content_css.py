#!/usr/bin/env python3
"""
批量在已生成的報告文件中添加 section-content CSS 樣式定義
"""

import re
from pathlib import Path

# section-content 的完整 CSS 定義
SECTION_CONTENT_CSS = """
        /* Section Content */
        .section-content {
            background: var(--card-bg);
            padding: 24px;
            border-radius: 2px;
            border-left: 4px solid var(--primary-color);
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            line-height: 1.9;
            white-space: pre-wrap;
            font-size: 0.95rem;
            color: #3c3c3c;
        }

        .section-content.success {
            border-left-color: var(--success-color);
        }

        .section-content.danger {
            border-left-color: var(--danger-color);
            background: #fef2f2;
        }

        .section-content.warning {
            border-left-color: var(--warning-color);
        }

        .section-content.purple {
            border-left-color: var(--purple-color);
        }

        @media (max-width: 768px) {
            .section-content {
                padding: 16px;
                font-size: 0.85rem;
            }
        }
"""

def add_section_content_css(content: str) -> tuple[str, bool]:
    """在 HTML 文件的 <style> 標籤中添加 section-content CSS"""
    
    # 檢查是否已經存在 section-content 定義
    if '.section-content' in content:
        return content, False
    
    # 尋找 .section { 的定義位置，在其後插入 section-content 定義
    # 使用正則表達式找到 .section 定義的結束位置
    pattern = r'(\.section\s*\{[^}]+\})'
    
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    if match:
        # 在 .section 定義之後插入 section-content CSS
        insert_pos = match.end()
        updated_content = content[:insert_pos] + '\n' + SECTION_CONTENT_CSS + content[insert_pos:]
        return updated_content, True
    
    return content, False

def process_html_files(directories: list[str]):
    """處理多個目錄中的 HTML 文件"""
    total_files = 0
    total_updated = 0
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            print(f"⚠️  目錄不存在: {directory}")
            continue
            
        print(f"\n📁 處理目錄: {directory}")
        print("-" * 60)
        
        html_files = sorted(dir_path.glob("*.html"))
        if not html_files:
            print(f"  ℹ️  沒有找到 HTML 文件")
            continue
            
        for file_path in html_files:
            # 跳過某些特殊文件
            if file_path.name in ['index.html', 'rwd_demo.html', 'report_20260109_old.html']:
                print(f"  ⊘  {file_path.name} - 跳過 (特殊文件)")
                continue
                
            try:
                # 讀取文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()
                
                # 添加 CSS
                updated_content, changed = add_section_content_css(original_content)
                
                if changed:
                    # 寫回文件
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    
                    print(f"  ✅ {file_path.name} - 已添加 section-content CSS")
                    total_files += 1
                    total_updated += 1
                else:
                    print(f"  ⊘  {file_path.name} - 已存在 CSS 定義，跳過")
                    
            except Exception as e:
                print(f"  ❌ {file_path.name} - 錯誤: {e}")
    
    return total_files, total_updated

def main():
    """主程序"""
    print("=" * 60)
    print("🎨 Section Content CSS 批量添加工具")
    print("=" * 60)
    print("在已生成的報告文件中添加 section-content 類別樣式定義")
    print()
    
    # 定義要處理的目錄
    directories = [
        'reports',
        'docs'
    ]
    
    # 處理所有文件
    total_files, total_updated = process_html_files(directories)
    
    # 顯示總結
    print()
    print("=" * 60)
    print("📊 更新總結")
    print("=" * 60)
    print(f"✅ 成功更新: {total_updated} 個文件")
    print()
    print("添加的 CSS 內容:")
    print("  • .section-content (基礎樣式)")
    print("  • .section-content.success (綠色)")
    print("  • .section-content.danger (紅色)")
    print("  • .section-content.warning (橙色)")
    print("  • .section-content.purple (紫色)")
    print("  • 響應式設計 (@media)")
    print()
    print("樣式特性:")
    print(f"  • 字體大小: 0.95rem (桌面) / 0.85rem (手機)")
    print(f"  • 行高: 1.9")
    print(f"  • 內距: 24px (桌面) / 16px (手機)")
    print(f"  • 邊框: 4px 左側")
    print(f"  • 陰影: 中等")
    print("=" * 60)

if __name__ == '__main__':
    main()
