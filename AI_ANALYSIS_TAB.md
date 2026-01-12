# AI 操盤分析頁籤功能說明

## 📋 概述

為結算日預測報告新增「AI 操盤分析」頁籤，以資深選擇權操盤手的第一人稱視角，提供更具實戰性的分析內容。

## 🎯 設計理念

### 雙頁籤架構
- **📊 技術分析**：原有的趨勢訊號、結算劇本等系統性分析
- **🤖 AI 操盤分析**：以操盤手視角進行深度解讀和實戰建議

### AI 分析特色
1. **第一人稱視角**：以資深操盤手口吻，分享實戰經驗與判斷
2. **籌碼心理分析**：解讀莊家意圖、市場情緒
3. **實戰操作建議**：提供具體的進出場策略
4. **風險管理提醒**：強調停損和資金管理

## 📊 AI 分析內容架構

### 1. 操盤手人設介紹
```
👨‍💼 資深選擇權操盤手視角
20年實戰經驗 | 專注台指選擇權結算日策略
```

### 2. 結算區間預測：莊家的「最佳利益點」
- **上檔天花板**：Call OI 壓力分析
  - 阻力區間範圍
  - 夜盤測試情況
  - 莊家防守意圖
  
- **下檔地板**：Put OI 支撐分析
  - 支撐區間範圍
  - 回測反應判斷
  - 護盤可能性

- **結算價預測**：最大痛點理論
  - 雙方權利金消耗最大化
  - 莊家最佳利益區間

### 3. P/C Ratio 轉弱的實戰意義
- P/C Ratio 變化解讀
- 市場追價意願分析
- 預期盤勢型態（高檔震盪、雙向整理等）
- 操作心態建議

### 4. 今日操作觀察重點
#### 🔔 開盤位階
- 多空平衡判斷
- 偏高開/偏低開應對策略

#### ⏰ 最後 30 分鐘
- 結算價計算方式（現貨最後半小時平均價）
- 莊家可能的攻防動作
- 關鍵履約價攻防

#### 🎲 預期結算價
- 高機率落點區間
- 莊家收益最大化邏輯

### 5. 實戰小叮嚀
1. **時間價值流逝加速**
   - IV 波動率影響
   - Theta Decay 時間衰減

2. **持倉部位建議**
   - 出場價位參考
   - 風險報酬比評估

3. **新進場策略**
   - 結算日風險提醒
   - 新月份布局建議

4. **黑天鵝事件警示**
   - 重大國際消息影響
   - 停損設定重要性

### 6. 總結：我的結算日策略
- 持倉部位處理
- 新進場時機選擇
- 觀察重點提醒
- 風險管理理念

## 🎨 視覺設計特色

### 價格區間卡片
```css
- 上檔阻力：紅色邊框
- 下檔支撐：綠色邊框
- 清晰的區間範圍顯示
- 詳細的市場解讀
```

### 情境預測卡片
```css
- 開盤位階觀察
- 最後 30 分鐘關鍵時刻
- 預期結算價高機率區間
- Hover 動畫效果
```

### 實戰提醒區塊
```css
- 淡紅色背景（警示效果）
- 重要資訊高亮顯示
- 條列清晰易讀
```

## 💻 技術實現

### 模板變數
```python
ai_data = {
    # 價位區間
    'ai_resistance_range': '30,700 ~ 31,000',
    'ai_support_range': '30,000 ~ 30,300',
    'ai_settlement_range': '30,350 ~ 30,550',
    
    # 夜盤數據
    'night_high': '30,583',
    'night_low': '30,325',
    'night_close': '30,458',
    'night_trend': '並未突破昨日高點',
    
    # P/C Ratio 分析
    'pc_ratio_status': '大幅下滑（0.87）',
    'chase_willingness': '放緩',
    'expected_pattern': '高檔狹幅震盪',
    
    # 當日觀察
    'opening_ref_price': '30,450',
    'key_strike_price': '30,500',
    
    # 操作建議
    'contract_month': '1月',
    'exit_level_high': '30,550',
    'resistance_key_level': '30,700',
    'next_month_1': '1月',
    'next_month_2': '2月',
}
```

### JavaScript 頁籤切換
```javascript
function switchTab(tabName) {
    // 隱藏所有頁籤內容
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // 移除所有按鈕的 active 狀態
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // 顯示選中的頁籤
    if (tabName === 'technical') {
        document.getElementById('technical-tab').classList.add('active');
        document.querySelectorAll('.tab-button')[0].classList.add('active');
    } else if (tabName === 'ai-analysis') {
        document.getElementById('ai-analysis-tab').classList.add('active');
        document.querySelectorAll('.tab-button')[1].classList.add('active');
    }
}
```

## 📱 響應式設計

### 桌面版
- 頁籤按鈕橫向排列
- 雙欄卡片佈局
- 大字體易讀

### 手機版
- 頁籤按鈕垂直堆疊
- 單欄卡片佈局
- 保持所有資訊可讀性

## 🚀 使用方式

### 生成報告
```bash
# 週三結算報告（週一+週二數據）
python3 generate_settlement_report.py \
  --dates 20260105,20260106 \
  --settlement 2026/01/08 \
  --weekday wednesday

# 週五結算報告（週三+週四數據）
python3 generate_settlement_report.py \
  --dates 20260107,20260108 \
  --settlement 2026/01/10 \
  --weekday friday
```

### 查看報告
1. 開啟生成的 HTML 檔案
2. 預設顯示「技術分析」頁籤
3. 點擊「AI 操盤分析」頁籤查看深度分析
4. 在兩個頁籤間自由切換

## 🎓 學習價值

### 對新手
- 學習操盤手思維模式
- 理解籌碼心理分析
- 建立風險管理觀念

### 對進階交易者
- 驗證自己的分析邏輯
- 參考實戰操作建議
- 了解市場運作機制

## ⚠️ 免責聲明

本報告內容：
- ✅ 基於歷史數據與技術分析
- ✅ 提供參考性的市場觀點
- ❌ **不構成投資建議**
- ❌ **不保證獲利**

投資人應：
- 自行評估風險承受能力
- 建立個人交易系統
- 嚴格執行停損紀律
- 理性控制部位大小

---

**記住：市場永遠是對的，我們只是順勢而為** 🍀
