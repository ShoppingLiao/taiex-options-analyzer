#!/usr/bin/env python3
"""
批量更新所有 HTML 檔案的 border-radius 為 50%
規則：
- 16px -> 8px
- 12px -> 6px
- 10px -> 5px
- 8px -> 4px
- 6px -> 3px
- 4px -> 2px
- 20px -> 10px
- 3px -> 1.5px (已經很小，保持 2px)
"""

import re
import os
from pathlib import Path

def update_border_radius(content):
    """更新 border-radius 值為 50%"""
    
    # 定義轉換規則
    radius_map = {
        '20px': '10px',
        '16px': '8px',
        '12px': '6px',
        '10px': '5px',
        '8px': '4px',
        '6px': '3px',
        '4px': '2px',
        '3px': '2px',  # 已經很小，保持 2px
    }
    
    # 處理單一值的 border-radius
    for old_val, new_val in radius_map.items():
        # border-radius: 12px
        content = re.sub(
            rf'border-radius:\s*{re.escape(old_val)}(?![0-9])',
            f'border-radius: {new_val}',
            content
        )
    
    # 處理組合值的 border-radius (例如: border-radius: 8px 8px 0 0)
    def replace_multi_radius(match):
        full_match = match.group(0)
        for old_val, new_val in radius_map.items():
            full_match = full_match.replace(old_val, new_val)
        return full_match
    
    content = re.sub(
        r'border-radius:\s*[\d\s]+(px\s*)+',
        replace_multi_radius,
        content
    )
    
    return content

def process_html_files():
    """處理所有 HTML 檔案"""
    base_dir = Path(__file__).parent
    
    # 需要處理的目錄
    directories = [
        base_dir / 'templates',
        base_dir / 'docs',
        base_dir / 'reports',
    ]
    
    updated_files = []
    
    for directory in directories:
        if not directory.exists():
            continue
            
        for html_file in directory.glob('*.html'):
            try:
                # 讀取檔案
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 更新 border-radius
                updated_content = update_border_radius(content)
                
                # 如果有變更，寫回檔案
                if updated_content != content:
                    with open(html_file, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    updated_files.append(str(html_file.relative_to(base_dir)))
                    print(f"✅ 已更新: {html_file.relative_to(base_dir)}")
                else:
                    print(f"⏭️  無需更新: {html_file.relative_to(base_dir)}")
                    
            except Exception as e:
                print(f"❌ 處理失敗 {html_file}: {e}")
    
    print(f"\n{'='*60}")
    print(f"總共更新了 {len(updated_files)} 個檔案")
    print(f"{'='*60}")
    
    if updated_files:
        print("\n更新的檔案列表：")
        for file in updated_files:
            print(f"  - {file}")

if __name__ == '__main__':
    print("開始批量更新 border-radius...")
    print("規則: 所有 border-radius 縮小為 50%")
    print(f"{'='*60}\n")
    process_html_files()
