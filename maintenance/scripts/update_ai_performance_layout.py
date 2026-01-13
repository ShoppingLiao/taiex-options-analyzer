#!/usr/bin/env python3
"""
批量更新結算日報告的 AI 預測績效總覽樣式
從舊版的 grid 布局更新為新版的橫排單行布局
"""

import re
from pathlib import Path

def update_ai_performance_section(content: str) -> tuple[str, bool]:
    """更新 AI 預測績效總覽區塊的樣式"""
    
    # 檢查是否包含舊版樣式（grid-template-columns: repeat(auto-fit）
    old_pattern = r'<!-- AI Performance Overview -->.*?<div class="section" style="background: linear-gradient\(135deg, #dbeafe 0%, #3b82f6 100%\);">.*?<div class="section-header".*?AI 預測績效總覽</h2>.*?</div>\s*.*?<!-- Best Prediction -->.*?</div>\s*</div>'
    
    if not re.search(old_pattern, content, re.DOTALL):
        return content, False
    
    # 新版樣式（橫排單行布局）
    new_section = '''<!-- AI Performance Overview - 重新設計為橫排緊湊格式 -->
            {% if ai_performance and ai_performance.statistics.total_predictions > 0 %}
            <div class="section" style="background: linear-gradient(135deg, #dbeafe 0%, #3b82f6 100%);">
                <div class="section-header" style="border-bottom-color: rgba(30, 64, 175, 0.2);">
                    <span class="section-icon">📈</span>
                    <h2 class="section-title" style="color: #1e40af;">AI 預測績效總覽</h2>
                </div>
                
                <!-- 統計數據 - 橫排格式 -->
                <div style="display: grid; gap: 12px; margin-bottom: 20px;">
                    <div style="background: rgba(255, 255, 255, 0.95); padding: 12px 15px; border-radius: 2px; border-left: 4px solid #3b82f6; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 0.85rem; color: #1e40af; font-weight: 600;">📊 總預測次數：</span>
                            <span style="font-size: 1.2rem; font-weight: 700; color: #2563eb; margin-left: 8px;">{{ ai_performance.statistics.total_predictions }}</span>
                        </div>
                        <div style="font-size: 0.75rem; color: #60a5fa;">累積經驗</div>
                    </div>
                    
                    <div style="background: rgba(255, 255, 255, 0.95); padding: 12px 15px; border-radius: 2px; border-left: 4px solid #10b981; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 0.85rem; color: #065f46; font-weight: 600;">✅ 平均準確度：</span>
                            <span style="font-size: 1.2rem; font-weight: 700; color: #059669; margin-left: 8px;">{{ ai_performance.statistics.avg_accuracy }}%</span>
                        </div>
                        <div style="font-size: 0.75rem; color: #34d399;">整體表現</div>
                    </div>
                    
                    <div style="background: rgba(255, 255, 255, 0.95); padding: 12px 15px; border-radius: 2px; border-left: 4px solid #f59e0b; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 0.85rem; color: #92400e; font-weight: 600;">📏 平均誤差：</span>
                            <span style="font-size: 1.2rem; font-weight: 700; color: #d97706; margin-left: 8px;">{{ ai_performance.statistics.avg_price_error|round(1) }}</span>
                        </div>
                        <div style="font-size: 0.75rem; color: #fbbf24;">點數</div>
                    </div>
                    
                    <div style="background: rgba(255, 255, 255, 0.95); padding: 12px 15px; border-radius: 2px; border-left: 4px solid #8b5cf6; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 0.85rem; color: #5b21b6; font-weight: 600;">🎯 區間命中率：</span>
                            <span style="font-size: 1.2rem; font-weight: 700; color: #7c3aed; margin-left: 8px;">{{ ai_performance.statistics.range_success_rate }}%</span>
                        </div>
                        <div style="font-size: 0.75rem; color: #a78bfa;">預測精準度</div>
                    </div>
                </div>
                
                <!-- Best Prediction - 橫排格式 -->
                {% if ai_performance.best_prediction %}
                <div style="background: rgba(255, 255, 255, 0.95); padding: 15px; border-radius: 2px; border-left: 4px solid #fbbf24;">
                    <div style="font-size: 0.9rem; color: #92400e; margin-bottom: 10px; font-weight: 600;">⭐ 最佳預測記錄</div>
                    <div style="display: flex; flex-wrap: wrap; gap: 15px; align-items: center;">
                        <div style="flex: 1; min-width: 100px;">
                            <span style="font-size: 0.75rem; color: #78716c;">日期：</span>
                            <span style="font-size: 0.95rem; font-weight: 600; color: #1c1917; margin-left: 5px;">{{ ai_performance.best_prediction.date }}</span>
                        </div>
                        <div style="flex: 1; min-width: 100px;">
                            <span style="font-size: 0.75rem; color: #78716c;">誤差：</span>
                            <span style="font-size: 0.95rem; font-weight: 600; color: #059669; margin-left: 5px;">{{ ai_performance.best_prediction.price_error }} 點</span>
                        </div>
                        <div style="flex: 1; min-width: 100px;">
                            <span style="font-size: 0.75rem; color: #78716c;">準確度：</span>
                            <span style="font-size: 0.95rem; font-weight: 600; color: #2563eb; margin-left: 5px;">{{ ai_performance.best_prediction.accuracy }}%</span>
                        </div>
                        <div style="flex: 1; min-width: 100px;">
                            <span style="font-size: 0.75rem; color: #78716c;">評分：</span>
                            <span style="font-size: 0.95rem; font-weight: 600; color: #7c3aed; margin-left: 5px;">{{ ai_performance.best_prediction.score }}</span>
                        </div>
                    </div>
                </div>
                {% endif %}
            </div>
            {% endif %}'''
    
    # 由於已生成的文件沒有 Jinja2 變數，需要直接替換實際內容
    # 先嘗試簡單的模式匹配和替換
    pattern = r'(<div class="section" style="background: linear-gradient\(135deg, #dbeafe 0%, #3b82f6 100%\);">.*?<h2 class="section-title" style="color: #1e40af;">AI 預測績效總覽</h2>.*?)</div>\s*</div>\s*<!-- AI Settlement Prediction -->'
    
    # 如果找不到，返回未修改的內容
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return content, False
    
    # 提取實際數據
    total_predictions = re.search(r'<div style="font-size: 2rem; font-weight: 700; color: #2563eb;">(\d+)</div>', match.group(0))
    avg_accuracy = re.search(r'<div style="font-size: 2rem; font-weight: 700; color: #059669;">([0-9.]+)%</div>', match.group(0))
    avg_error = re.search(r'<div style="font-size: 2rem; font-weight: 700; color: #d97706;">([0-9.]+)</div>', match.group(0))
    range_success = re.search(r'<div style="font-size: 2rem; font-weight: 700; color: #7c3aed;">([0-9.]+)%</div>', match.group(0))
    
    best_date = re.search(r'<div style="font-size: 1\.1rem; font-weight: 600; color: #1c1917;">(\d+)</div>', match.group(0))
    best_error = re.search(r'<div style="font-size: 1\.1rem; font-weight: 600; color: #059669;">(\d+) 點</div>', match.group(0))
    best_accuracy = re.search(r'<div style="font-size: 1\.1rem; font-weight: 600; color: #2563eb;">(\d+)%</div>', match.group(0))
    best_score = re.search(r'<div style="font-size: 1\.1rem; font-weight: 600; color: #7c3aed;">(.*?)</div>', match.group(0))
    
    if not all([total_predictions, avg_accuracy, avg_error, range_success]):
        return content, False
    
    # 構建新的 HTML（實際數據版本）
    new_html = f'''<div class="section" style="background: linear-gradient(135deg, #dbeafe 0%, #3b82f6 100%);">
                <div class="section-header" style="border-bottom-color: rgba(30, 64, 175, 0.2);">
                    <span class="section-icon">📈</span>
                    <h2 class="section-title" style="color: #1e40af;">AI 預測績效總覽</h2>
                </div>
                
                <!-- 統計數據 - 橫排格式 -->
                <div style="display: grid; gap: 12px; margin-bottom: 20px;">
                    <div style="background: rgba(255, 255, 255, 0.95); padding: 12px 15px; border-radius: 2px; border-left: 4px solid #3b82f6; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 0.85rem; color: #1e40af; font-weight: 600;">📊 總預測次數：</span>
                            <span style="font-size: 1.2rem; font-weight: 700; color: #2563eb; margin-left: 8px;">{total_predictions.group(1)}</span>
                        </div>
                        <div style="font-size: 0.75rem; color: #60a5fa;">累積經驗</div>
                    </div>
                    
                    <div style="background: rgba(255, 255, 255, 0.95); padding: 12px 15px; border-radius: 2px; border-left: 4px solid #10b981; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 0.85rem; color: #065f46; font-weight: 600;">✅ 平均準確度：</span>
                            <span style="font-size: 1.2rem; font-weight: 700; color: #059669; margin-left: 8px;">{avg_accuracy.group(1)}%</span>
                        </div>
                        <div style="font-size: 0.75rem; color: #34d399;">整體表現</div>
                    </div>
                    
                    <div style="background: rgba(255, 255, 255, 0.95); padding: 12px 15px; border-radius: 2px; border-left: 4px solid #f59e0b; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 0.85rem; color: #92400e; font-weight: 600;">📏 平均誤差：</span>
                            <span style="font-size: 1.2rem; font-weight: 700; color: #d97706; margin-left: 8px;">{avg_error.group(1)}</span>
                        </div>
                        <div style="font-size: 0.75rem; color: #fbbf24;">點數</div>
                    </div>
                    
                    <div style="background: rgba(255, 255, 255, 0.95); padding: 12px 15px; border-radius: 2px; border-left: 4px solid #8b5cf6; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 0.85rem; color: #5b21b6; font-weight: 600;">🎯 區間命中率：</span>
                            <span style="font-size: 1.2rem; font-weight: 700; color: #7c3aed; margin-left: 8px;">{range_success.group(1)}%</span>
                        </div>
                        <div style="font-size: 0.75rem; color: #a78bfa;">預測精準度</div>
                    </div>
                </div>'''
    
    # 添加最佳預測記錄（如果有）
    if best_date and best_error and best_accuracy and best_score:
        new_html += f'''
                
                <!-- Best Prediction - 橫排格式 -->
                <div style="background: rgba(255, 255, 255, 0.95); padding: 15px; border-radius: 2px; border-left: 4px solid #fbbf24;">
                    <div style="font-size: 0.9rem; color: #92400e; margin-bottom: 10px; font-weight: 600;">⭐ 最佳預測記錄</div>
                    <div style="display: flex; flex-wrap: wrap; gap: 15px; align-items: center;">
                        <div style="flex: 1; min-width: 100px;">
                            <span style="font-size: 0.75rem; color: #78716c;">日期：</span>
                            <span style="font-size: 0.95rem; font-weight: 600; color: #1c1917; margin-left: 5px;">{best_date.group(1)}</span>
                        </div>
                        <div style="flex: 1; min-width: 100px;">
                            <span style="font-size: 0.75rem; color: #78716c;">誤差：</span>
                            <span style="font-size: 0.95rem; font-weight: 600; color: #059669; margin-left: 5px;">{best_error.group(1)} 點</span>
                        </div>
                        <div style="flex: 1; min-width: 100px;">
                            <span style="font-size: 0.75rem; color: #78716c;">準確度：</span>
                            <span style="font-size: 0.95rem; font-weight: 600; color: #2563eb; margin-left: 5px;">{best_accuracy.group(1)}%</span>
                        </div>
                        <div style="flex: 1; min-width: 100px;">
                            <span style="font-size: 0.75rem; color: #78716c;">評分：</span>
                            <span style="font-size: 0.95rem; font-weight: 600; color: #7c3aed; margin-left: 5px;">{best_score.group(1)}</span>
                        </div>
                    </div>
                </div>'''
    
    new_html += '\n            </div>'
    
    # 替換舊內容
    updated_content = re.sub(pattern, new_html + '\n            \n            <!-- AI Settlement Prediction -->', content, flags=re.DOTALL)
    
    return updated_content, True

def process_settlement_reports():
    """處理結算日報告文件"""
    directories = ['reports', 'docs']
    total_files = 0
    total_updated = 0
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            continue
            
        print(f"\n📁 處理目錄: {directory}")
        print("-" * 60)
        
        # 只處理結算日報告
        settlement_files = sorted(dir_path.glob("settlement_*.html"))
        
        for file_path in settlement_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                updated_content, changed = update_ai_performance_section(content)
                
                if changed:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                    
                    print(f"  ✅ {file_path.name} - 已更新 AI 預測績效總覽樣式")
                    total_updated += 1
                else:
                    print(f"  ⊘  {file_path.name} - 未找到需要更新的內容")
                
                total_files += 1
                
            except Exception as e:
                print(f"  ❌ {file_path.name} - 錯誤: {e}")
    
    return total_files, total_updated

def main():
    print("=" * 60)
    print("🎨 AI 預測績效總覽樣式更新工具")
    print("=" * 60)
    print("將舊版 grid 布局更新為新版橫排單行布局")
    print()
    
    total_files, total_updated = process_settlement_reports()
    
    print()
    print("=" * 60)
    print("📊 更新總結")
    print("=" * 60)
    print(f"✅ 成功更新: {total_updated} 個文件")
    print(f"📝 處理文件: {total_files} 個")
    print()
    print("更新內容:")
    print("  • 從 4個方塊並排 → 4個橫條單行排列")
    print("  • 數字和標籤在同一行（更緊湊）")
    print("  • 最佳預測記錄改為橫排 flex 布局")
    print("  • 優化手機端顯示效果")
    print("=" * 60)

if __name__ == '__main__':
    main()
