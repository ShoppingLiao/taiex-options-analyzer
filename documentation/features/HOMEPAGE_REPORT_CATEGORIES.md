# 首頁報告分類功能

## 📋 更新內容

在首頁新增報告類型分類，讓使用者更容易找到不同類型的報告。

## 🎯 報告類型

### 1. 📅 單日報告

**說明**：每日選擇權市場分析，包含 OI 分佈、價格走勢、結算情境預測等詳細資訊

**內容包含**：

- OI 分佈分析（蝴蝶圖）
- OI 變化表格
- 價格走勢（開高低收）
- Max Pain 分析
- P/C Ratio 分析
- 結算情境預測（3-4 種情境）
- AI 情境分析

**報告範例**：

- 2026/01/09 (五) - 最新報告
- 2026/01/08 (四) - 歷史報告
- 2026/01/07 (三) - 歷史報告
- ...

---

### 2. 🎯 結算日報告

**說明**：選擇權結算日專題分析，包含結算價預測、莊家佈局、歷史結算統計等深度內容

**狀態**：即將推出 📦

**規劃內容**：

- 結算日倒數提醒
- 結算價預測分析
- 莊家佈局追蹤
- 歷史結算價統計
- 結算日交易策略建議
- 結算週期分析

**預計功能**：

1. 結算日前 3 天的市場動態追蹤
2. 結算日當天的即時分析
3. 結算後的覆盤報告
4. 歷史結算日數據庫

---

## 🎨 視覺設計

### 首頁佈局

```
┌──────────────────────────────────────────┐
│      📊 台指選擇權分析報告                │
│   Taiwan Stock Index Options Analysis    │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│ 📅 單日報告              [5 份報告]      │
├──────────────────────────────────────────┤
│ 每日選擇權市場分析，包含 OI 分佈...       │
│                                          │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐     │
│ │2026/1/9 │ │2026/1/8 │ │2026/1/7 │     │
│ │ (五)    │ │ (四)    │ │ (三)    │     │
│ │最新報告 │ │歷史報告 │ │歷史報告 │     │
│ └─────────┘ └─────────┘ └─────────┘     │
│ ┌─────────┐ ┌─────────┐                 │
│ │2026/1/6 │ │2026/1/5 │                 │
│ │ (二)    │ │ (一)    │                 │
│ └─────────┘ └─────────┘                 │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│ 🎯 結算日報告          [即將推出]        │
├──────────────────────────────────────────┤
│ 選擇權結算日專題分析...                  │
│                                          │
│              📦                          │
│       結算日報告功能開發中                │
│     敬請期待更深入的結算日分析內容        │
│                                          │
└──────────────────────────────────────────┘
```

---

## 💻 技術實現

### HTML 結構

```html
<div class="report-section">
  <div class="section-header">
    <span class="section-icon">📅</span>
    <h2 class="section-title">單日報告</h2>
    <span class="section-count">5 份報告</span>
  </div>
  <p class="section-description">描述文字...</p>
  <div class="reports-grid">
    <!-- 報告卡片 -->
  </div>
</div>
```

### CSS 樣式

#### 1. 報告區塊

```css
.report-section {
  background: white;
  border-radius: 16px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
```

#### 2. 區塊標題列

```css
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
```

#### 3. 描述文字

```css
.section-description {
  color: #64748b;
  margin-bottom: 20px;
  font-size: 0.95rem;
}
```

#### 4. 空狀態提示

```css
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
```

---

## 🔧 生成腳本更新

### `generate_index_with_weekday.py`

#### 主要變更

1. **新增區塊結構**

```python
html_content += '''
        <!-- 單日報告區塊 -->
        <div class="report-section">
            <div class="section-header">
                <span class="section-icon">📅</span>
                <h2 class="section-title">單日報告</h2>
                <span class="section-count">''' + str(len(reports)) + ''' 份報告</span>
            </div>
            <p class="section-description">每日選擇權市場分析...</p>
            <div class="reports-grid">
'''
```

2. **加入結算日報告區塊**

```python
html_content += '''
        <!-- 結算日報告區塊 -->
        <div class="report-section">
            <div class="section-header">
                <span class="section-icon">🎯</span>
                <h2 class="section-title">結算日報告</h2>
                <span class="section-count">即將推出</span>
            </div>
            <p class="section-description">選擇權結算日專題分析...</p>
            <div class="empty-state">
                <div class="empty-state-icon">📦</div>
                <div class="empty-state-text">結算日報告功能開發中</div>
                <div class="empty-state-hint">敬請期待更深入的結算日分析內容</div>
            </div>
        </div>
'''
```

3. **動態計算報告數量**

```python
<span class="section-count">''' + str(len(reports)) + ''' 份報告</span>
```

---

## 📊 視覺效果

### 區塊標題設計

```
📅 單日報告                    [5 份報告]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**設計元素**：

- 📅 圖示：快速識別報告類型
- 標題：1.5rem 粗體字
- 計數標籤：淺灰背景，右側對齊

### 空狀態設計

```
        📦
結算日報告功能開發中
敬請期待更深入的結算日分析內容
```

**設計元素**：

- 📦 大圖示：4rem，半透明
- 提示文字：柔和灰色
- 垂直置中，padding 60px

---

## 🎯 使用者體驗優化

### 1. 清晰的分類

- ✅ 使用圖示快速識別
- ✅ 標題明確說明內容
- ✅ 描述文字提供詳細資訊

### 2. 狀態提示

- ✅ 最新報告：粉紅漸層標籤
- ✅ 歷史報告：藍紫漸層標籤
- ✅ 即將推出：淡灰色標籤

### 3. 視覺層次

- ✅ 白色卡片與紫色背景對比
- ✅ 分隔線區分不同區塊
- ✅ 陰影效果增加立體感

### 4. 響應式設計

```css
@media (max-width: 768px) {
  h1 {
    font-size: 1.8rem;
  }
  .reports-grid {
    grid-template-columns: 1fr; /* 手機版單欄 */
  }
}
```

---

## 📁 更新的檔案

1. ✅ `docs/index.html` - 首頁 HTML
2. ✅ `generate_index_with_weekday.py` - 首頁生成腳本

---

## 🚀 未來擴展計劃

### 結算日報告功能

#### Phase 1: 基礎功能

- [ ] 結算日期自動計算（每月第三個週三）
- [ ] 結算日倒數顯示
- [ ] 結算週報告頁面模板

#### Phase 2: 數據分析

- [ ] 結算日 OI 特殊分佈分析
- [ ] 結算價預測模型
- [ ] 莊家佈局追蹤

#### Phase 3: 歷史統計

- [ ] 歷史結算價數據庫
- [ ] 結算價分佈統計
- [ ] 結算週期模式分析

#### Phase 4: 策略建議

- [ ] 結算日交易策略
- [ ] 風險控管建議
- [ ] 實時監控提醒

---

## 🎨 設計理念

### 1. 資訊架構

```
首頁
├── Header (標題 + 副標題)
├── 單日報告區塊
│   ├── 標題列 (圖示 + 名稱 + 數量)
│   ├── 描述文字
│   └── 報告網格 (卡片列表)
├── 結算日報告區塊
│   ├── 標題列 (圖示 + 名稱 + 狀態)
│   ├── 描述文字
│   └── 空狀態提示
└── Footer (生成時間 + GitHub 連結)
```

### 2. 顏色系統

- **主色調**：藍紫漸層 (#667eea → #764ba2)
- **強調色**：粉紅漸層 (#f093fb → #f5576c)
- **背景色**：純白 (#ffffff)
- **文字色**：深灰 (#1e293b)
- **輔助色**：淺灰 (#64748b)

### 3. 間距系統

- **大區塊間距**：30px
- **卡片內距**：24px 或 30px
- **小元素間距**：8px - 20px
- **標題下邊距**：15px + 2px border

---

## ✅ 完成項目

- ✅ 新增報告類型分類結構
- ✅ 實現單日報告區塊
- ✅ 實現結算日報告區塊（空狀態）
- ✅ 更新首頁生成腳本
- ✅ 動態計算報告數量
- ✅ 空狀態視覺設計
- ✅ 響應式設計
- ✅ 語義化 HTML 結構
- ✅ 清晰的視覺層次
- ✅ 友善的使用者提示

---

## 📝 使用方式

### 重新生成首頁

```bash
python3 generate_index_with_weekday.py
```

### 輸出範例

```
✅ 首頁已更新: docs/index.html

報告日期與星期：
  ⭐ 2026/01/09 (五)
     2026/01/08 (四)
     2026/01/07 (三)
     2026/01/06 (二)
     2026/01/05 (一)
```

### 新增報告

在 `generate_index_with_weekday.py` 中修改 `reports` 列表：

```python
reports = [
    ('20260110', True),   # 新增最新報告
    ('20260109', False),  # 舊報告改為歷史
    ('20260108', False),
    # ...
]
```

### 未來新增結算日報告

當結算日報告功能開發完成後，在生成腳本中加入：

```python
# 結算日報告列表
settlement_reports = [
    ('202601', '2026/01/21'),  # (契約月份, 結算日期)
    ('202512', '2025/12/17'),
]

# 在 HTML 中替換空狀態為報告卡片
for month, date in settlement_reports:
    html_content += f'''
                <a href="settlement_{month}.html" class="report-card">
                    <div class="report-date">{date} 結算日</div>
                    <div class="report-month">{month} 月份契約</div>
                </a>
    '''
```

---

## 🎉 總結

這次更新為首頁增加了清晰的報告分類系統：

1. ✅ **視覺層次清晰**：使用區塊、標題、描述文字建立資訊架構
2. ✅ **功能擴展性強**：結算日報告區塊預留好位置
3. ✅ **使用者友善**：空狀態提示告知功能開發中
4. ✅ **維護性良好**：生成腳本自動化處理
5. ✅ **設計一致性**：延續整體風格和色彩系統

現在使用者可以清楚看到兩種報告類型，並了解未來會有更深入的結算日分析功能！
