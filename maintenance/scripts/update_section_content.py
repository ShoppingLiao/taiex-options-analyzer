#!/usr/bin/env python3
"""
批量更新报告文件，将内联样式替换为 section-content 类
"""

import re
from pathlib import Path

def update_section_content_class(content: str) -> tuple[str, int]:
    """将内联样式替换为 section-content 类"""
    changes = 0
    
    # 定义替换规则 - 每个规则包含 (pattern, replacement, description)
    replacements = [
        # 1. 市場觀察 / 我的看法 (蓝色边框) - 使用 section-content (default)
        (
            r'<div style="background:\s*white;\s*padding:\s*(?:25|30)px;\s*border-radius:\s*\d+px;\s*border-left:\s*4px\s+solid\s+var\(--primary-color\);\s*box-shadow:\s*[^;]+;\s*line-height:\s*[\d.]+;\s*white-space:\s*pre-wrap;(?:\s*font-size:\s*[\d.]+rem;)?(?:\s*color:\s*#[0-9a-f]{6};)?">',
            '<div class="section-content">',
            '市場觀察/看法 (藍色)'
        ),
        
        # 2. 部位策略 / 結算策略 (绿色边框) - 使用 section-content success
        (
            r'<div style="background:\s*white;\s*padding:\s*(?:25|30)px;\s*border-radius:\s*\d+px;\s*border-left:\s*4px\s+solid\s+#10b981;\s*box-shadow:\s*[^;]+;\s*line-height:\s*[\d.]+;\s*white-space:\s*pre-wrap;(?:\s*font-size:\s*[\d.]+rem;)?">',
            '<div class="section-content success">',
            '部位策略/結算策略 (綠色)'
        ),
        
        # 3. 風險評估 / 最擔心的風險 (红色边框+背景) - 使用 section-content danger
        (
            r'<div style="background:\s*#fef2f2;\s*padding:\s*(?:25|30)px;\s*border-radius:\s*\d+px;\s*border-left:\s*4px\s+solid\s+#ef4444;\s*box-shadow:\s*[^;]+;\s*line-height:\s*[\d.]+;\s*white-space:\s*pre-wrap;(?:\s*font-size:\s*[\d.]+rem;)?">',
            '<div class="section-content danger">',
            '風險評估 (紅色)'
        ),
        
        # 4. 交易計劃 / 執行計劃 (橙色边框) - 使用 section-content warning
        (
            r'<div style="background:\s*white;\s*padding:\s*(?:25|30)px;\s*border-radius:\s*\d+px;\s*border-left:\s*4px\s+solid\s+#f59e0b;\s*box-shadow:\s*[^;]+;\s*line-height:\s*[\d.]+;\s*white-space:\s*pre-wrap;(?:\s*font-size:\s*[\d.]+rem;)?">',
            '<div class="section-content warning">',
            '交易計劃/執行計劃 (橙色)'
        ),
        
        # 5. 市場展望 (黄色边框) - 使用 section-content warning
        (
            r'<div style="background:\s*white;\s*padding:\s*(?:25|30)px;\s*border-radius:\s*\d+px;\s*border-left:\s*4px\s+solid\s+#fbbf24;\s*box-shadow:\s*[^;]+;\s*line-height:\s*[\d.]+;\s*white-space:\s*pre-wrap;">',
            '<div class="section-content warning">',
            '市場展望 (黃色)'
        ),
        
        # 6. 自我反思 (紫色边框) - 使用 section-content purple
        (
            r'<div style="background:\s*white;\s*padding:\s*(?:25|30)px;\s*border-radius:\s*\d+px;\s*border-left:\s*4px\s+solid\s+#8b5cf6;\s*box-shadow:\s*[^;]+;\s*line-height:\s*[\d.]+;\s*white-space:\s*pre-wrap;">',
            '<div class="section-content purple">',
            '自我反思 (紫色)'
        ),
    ]
    
    # 应用所有替换规则
    for pattern, replacement, description in replacements:
        matches = len(re.findall(pattern, content, re.IGNORECASE))
        if matches > 0:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
            changes += matches
            print(f"    ✓ {description}: {matches} 處")
    
    return content, changes

def process_html_files(directories: list[str]):
    """處理多個目錄中的 HTML 文件"""
    total_files = 0
    total_changes = 0
    
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
            try:
                # 讀取文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()
                
                # 更新內容
                updated_content, changes = update_section_content_class(original_content)
                
                if changes > 0:
                    # 寫回文件
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    
                    print(f"  ✅ {file_path.name} - {changes} 處更新")
                    total_files += 1
                    total_changes += changes
                else:
                    print(f"  ⊘  {file_path.name} - 無需更新")
                    
            except Exception as e:
                print(f"  ❌ {file_path.name} - 錯誤: {e}")
    
    return total_files, total_changes

def main():
    """主程序"""
    print("=" * 60)
    print("🔄 Section Content 類別批量更新工具")
    print("=" * 60)
    print("將內聯樣式替換為 section-content 類別")
    print("支援 5 種主題: default(藍), success(綠), danger(紅), warning(橙), purple(紫)")
    print()
    
    # 定義要處理的目錄
    directories = [
        'reports',
        'docs'
    ]
    
    # 處理所有文件
    total_files, total_changes = process_html_files(directories)
    
    # 顯示總結
    print()
    print("=" * 60)
    print("📊 更新總結")
    print("=" * 60)
    print(f"✅ 成功更新: {total_files} 個文件")
    print(f"📝 總更新次數: {total_changes} 處")
    print()
    print("主要更新內容:")
    print("  • 市場觀察/看法 → section-content (藍色)")
    print("  • 部位策略/結算策略 → section-content success (綠色)")
    print("  • 風險評估/擔心風險 → section-content danger (紅色)")
    print("  • 交易計劃/執行計劃 → section-content warning (橙色)")
    print("  • 市場展望 → section-content warning (黃色)")
    print("  • 自我反思 → section-content purple (紫色)")
    print()
    print("💡 優勢:")
    print("  • 代碼精簡 70% (10行 → 1行)")
    print("  • 統一字體大小 0.8rem (桌面) / 0.75rem (手機)")
    print("  • 集中管理於 Design System")
    print("  • 響應式設計自動適配")
    print("=" * 60)

if __name__ == '__main__':
    main()
