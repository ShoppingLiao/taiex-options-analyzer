# 設計系統遷移對照表

本文檔幫助你將現有的 inline styles 轉換為設計系統的 class。

## 📋 色彩對照

| 舊寫法 (Inline Style)            | 新寫法 (Design System)                                    | 使用情境   |
| -------------------------------- | --------------------------------------------------------- | ---------- |
| `color: #2563eb`                 | `class="text-primary"`                                    | 主色調文字 |
| `color: #22c55e`                 | `class="text-success"`                                    | 成功/看多  |
| `color: #ef4444`                 | `class="text-danger"`                                     | 危險/看空  |
| `color: #f59e0b`                 | `class="text-warning"`                                    | 警告/中性  |
| `color: #64748b`                 | `class="text-muted"`                                      | 次要文字   |
| `background: #2563eb`            | 使用 `.badge-primary` 或 `.btn-primary`                   | 背景色     |
| `border-left: 4px solid #2563eb` | `class="data-bar primary"` 或 `class="info-card primary"` | 左側色條   |

## 📏 字體大小對照

| 舊寫法               | 新寫法                   | Desktop | Mobile |
| -------------------- | ------------------------ | ------- | ------ |
| `font-size: 3rem`    | `class="text-xxl"`       | 48px    | 32px   |
| `font-size: 2.5rem`  | `class="text-xl"`        | 40px    | 24px   |
| `font-size: 2rem`    | `class="text-lg"`        | 32px    | 20.8px |
| `font-size: 1.5rem`  | `class="text-md"`        | 24px    | 19.2px |
| `font-size: 1.3rem`  | `class="text-base"`      | 20.8px  | 16px   |
| `font-size: 1.1rem`  | `class="text-sm"`        | 17.6px  | 14.4px |
| `font-size: 0.95rem` | `class="text-xs"`        | 15.2px  | 13.6px |
| `font-size: 0.85rem` | `class="text-xxs"`       | 13.6px  | 12px   |
| `font-size: 0.75rem` | 使用 `var(--font-micro)` | 12px    | 11.2px |

## 🎯 組件替換對照

### 1. Header 資訊列

**舊寫法:**

```html
<div
  style="display: flex; gap: 30px; margin-top: 20px; padding-top: 20px; border-top: 2px solid rgba(255, 255, 255, 0.2);"
>
  <div style="flex: 1;">
    <div style="font-size: 0.85rem; opacity: 0.8; margin-bottom: 5px;">
      當前價格
    </div>
    <div style="font-size: 1.3rem; font-weight: 700;">30,372</div>
  </div>
</div>
```

**新寫法:**

```html
<div class="info-items">
  <div class="info-item">
    <div class="info-label">當前價格</div>
    <div class="info-value">30,372</div>
  </div>
</div>
```

### 2. Section Header

**舊寫法:**

```html
<div
  style="display: flex; align-items: center; margin-bottom: 25px; padding-bottom: 15px; border-bottom: 2px solid #e2e8f0;"
>
  <span style="font-size: 1.8rem; margin-right: 12px;">📊</span>
  <h2 style="font-size: 1.5rem; font-weight: 700; margin: 0;">標題</h2>
</div>
```

**新寫法:**

```html
<div class="section-header">
  <span class="section-icon">📊</span>
  <h2 class="section-title">標題</h2>
  <span class="section-count">5 份</span>
</div>
```

### 3. 數據卡片 (Grid 佈局)

**舊寫法:**

```html
<div
  style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;"
>
  <div
    style="background: white; padding: 15px; border-radius: 8px; border-left: 4px solid #2563eb;"
  >
    <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 5px;">
      標籤
    </div>
    <div style="font-size: 1.5rem; font-weight: 700; color: #2563eb;">數值</div>
  </div>
</div>
```

**新寫法:**

```html
<div class="grid grid-auto-sm">
  <div class="data-card">
    <div class="data-card-label">標籤</div>
    <div class="data-card-value text-primary">數值</div>
  </div>
</div>
```

### 4. 單行數據條 (移動端推薦)

**舊寫法:**

```html
<div
  style="background: white; padding: 12px 15px; border-radius: 8px; border-left: 4px solid #2563eb; 
            display: flex; justify-content: space-between; align-items: center;"
>
  <span style="font-size: 0.85rem; color: #2563eb; font-weight: 600;"
    >📊 總預測次數：</span
  >
  <span style="font-size: 1.2rem; font-weight: 700; color: #2563eb;">15</span>
  <span style="font-size: 0.75rem; color: #64748b;">累積經驗</span>
</div>
```

**新寫法:**

```html
<div class="data-bar primary">
  <span class="data-bar-label">📊 總預測次數：</span>
  <span class="data-bar-value">15</span>
  <span class="data-bar-hint">累積經驗</span>
</div>
```

### 5. 資訊卡片 (帶標題與內容)

**舊寫法:**

```html
<div
  style="background: white; padding: 15px; border-radius: 8px; border-left: 4px solid #f59e0b;"
>
  <div
    style="font-weight: 600; color: #92400e; margin-bottom: 10px; font-size: 1.05rem;"
  >
    🕐 結算前準備
  </div>
  <div style="color: #78350f; margin-bottom: 8px;">
    <span style="font-weight: 500;">時機：</span>結算前 1 小時
  </div>
  <div style="color: #78350f; margin-bottom: 8px;">
    <span style="font-weight: 500;">動作：</span>調整部位
  </div>
</div>
```

**新寫法:**

```html
<div class="info-card warning">
  <div class="info-card-header">
    <span class="info-card-title">🕐 結算前準備</span>
  </div>
  <div class="info-card-content">
    <p><span class="font-semibold">時機：</span>結算前 1 小時</p>
    <p><span class="font-semibold">動作：</span>調整部位</p>
  </div>
</div>
```

### 6. Tab 按鈕

**舊寫法:**

```html
<div
  style="display: flex; gap: 12px; margin-bottom: 30px; background: white; padding: 12px; border-radius: 12px;"
>
  <button
    style="flex: 1; padding: 16px 20px; background: linear-gradient(135deg, #2563eb, #1d4ed8); 
                   border: none; border-radius: 8px; color: white; font-weight: 600;"
  >
    <span style="font-size: 1.1rem;">📊</span> 技術分析
  </button>
</div>
```

**新寫法:**

```html
<div class="tabs-container">
  <button class="tab-button active">
    <span class="tab-icon">📊</span>
    技術分析
  </button>
</div>
```

### 7. 圖表容器

**舊寫法:**

```html
<div
  style="background: white; border-radius: 12px; padding: 24px; margin-bottom: 30px; 
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); border: 1px solid #e2e8f0;"
>
  <h3
    style="font-size: 1.25rem; font-weight: 600; margin-bottom: 20px; 
               padding-bottom: 10px; border-bottom: 2px solid #e2e8f0;"
  >
    圖表標題
  </h3>
  <div id="chart"></div>
</div>
```

**新寫法:**

```html
<div class="chart-container">
  <h3 class="chart-title">圖表標題</h3>
  <div id="chart"></div>
</div>
```

### 8. Badge/徽章

**舊寫法:**

```html
<span
  style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
             color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.85rem;"
  >最新報告</span
>
```

**新寫法:**

```html
<span class="badge badge-latest">最新報告</span>
```

## 🔧 間距替換對照

| 舊寫法                | 新寫法           | 數值                 |
| --------------------- | ---------------- | -------------------- |
| `margin-bottom: 30px` | `class="mb-xxl"` | 30px / 15px (mobile) |
| `margin-bottom: 25px` | `class="mb-xl"`  | 24px / 12px (mobile) |
| `margin-bottom: 20px` | `class="mb-lg"`  | 20px / 10px (mobile) |
| `margin-bottom: 15px` | `class="mb-md"`  | 16px / 8px (mobile)  |
| `margin-bottom: 12px` | `class="mb-sm"`  | 12px / 6px (mobile)  |
| `padding: 30px`       | `class="p-xl"`   | 24px / 12px (mobile) |
| `padding: 20px`       | `class="p-lg"`   | 20px / 10px (mobile) |
| `gap: 20px`           | `class="gap-lg"` | 20px                 |
| `gap: 15px`           | `class="gap-md"` | 16px                 |

## 📱 響應式對照

### Mobile Header Scrolling

**舊寫法:**

```html
@media (max-width: 768px) { .info-items { overflow-x: auto;
-webkit-overflow-scrolling: touch; scrollbar-width: thin; }
.info-items::-webkit-scrollbar { height: 3px; } }
```

**新寫法:**

```html
<!-- 已內建在 .info-items 中，無需額外處理 -->
<div class="info-items">
  <!-- 自動支援移動端橫向滾動 -->
</div>
```

### Grid 響應式

**舊寫法:**

```html
<div style="display: grid; grid-template-columns: repeat(4, 1fr);">...</div>

@media (max-width: 768px) { div { grid-template-columns: repeat(2, 1fr); } }
```

**新寫法:**

```html
<div class="grid grid-4">
  <!-- 桌面 4 欄，移動端自動 2 欄 -->
</div>
```

## 🎨 漸層背景對照

| 舊寫法                                                          | 新寫法                             |
| --------------------------------------------------------------- | ---------------------------------- |
| `background: linear-gradient(135deg, #dbeafe 0%, #2563eb 100%)` | `class="section gradient-primary"` |
| `background: linear-gradient(135deg, #dcfce7 0%, #22c55e 100%)` | `class="section gradient-success"` |
| `background: linear-gradient(135deg, #fee2e2 0%, #ef4444 100%)` | `class="section gradient-danger"`  |
| `background: linear-gradient(135deg, #fef3c7 0%, #f59e0b 100%)` | `class="section gradient-warning"` |
| `background: linear-gradient(135deg, #ede9fe 0%, #8b5cf6 100%)` | `class="section gradient-purple"`  |

## 📝 實際遷移範例

### Before (舊代碼):

```html
<div
  style="background: rgba(255, 255, 255, 0.9); border-radius: 12px; padding: 25px; margin-bottom: 25px;"
>
  <h3 style="color: #5b21b6; margin-bottom: 15px; font-size: 1.3rem;">
    📊 準確度分析
  </h3>
  <div style="display: grid; gap: 10px;">
    <div
      style="background: white; padding: 12px 15px; border-radius: 8px; border-left: 4px solid #8b5cf6; 
                    display: flex; justify-content: space-between; align-items: center;"
    >
      <span style="font-size: 0.85rem; color: #6b21a8; font-weight: 600;"
        >📈 預測準確度：</span
      >
      <span style="font-size: 1.2rem; font-weight: 700; color: #5b21b6;"
        >100%</span
      >
    </div>
  </div>
</div>
```

### After (新代碼):

```html
<div class="section">
  <h3 class="text-base text-purple font-bold mb-md">📊 準確度分析</h3>
  <div class="data-bar purple">
    <span class="data-bar-label">📈 預測準確度：</span>
    <span class="data-bar-value">100%</span>
  </div>
</div>
```

**代碼減少**: ~80% ✅  
**可讀性**: 大幅提升 ✅  
**可維護性**: 統一調整 ✅

## 🔄 遷移檢查清單

遷移現有頁面時，請按此順序檢查：

1. ✅ 在 `<head>` 中添加 `{% include 'design_system.html' %}`
2. ✅ 替換所有 Header 為 `.page-header`
3. ✅ 替換所有 Section 為 `.section` + `.section-header`
4. ✅ 替換數據展示為 `.data-card` 或 `.data-bar`
5. ✅ 替換 Tab 為 `.tabs-container` + `.tab-button`
6. ✅ 替換 Grid 為 `.grid .grid-*`
7. ✅ 替換 inline colors 為 `.text-*` classes
8. ✅ 替換 inline font-size 為 `.text-*` classes
9. ✅ 替換 margin/padding 為 `.mb-*` / `.p-*` utilities
10. ✅ 刪除所有 `@media (max-width: 768px)` (已內建)
11. ✅ 測試桌面端顯示
12. ✅ 測試移動端顯示
13. ✅ 驗證所有互動功能正常

## 🚨 常見錯誤

❌ **錯誤 1**: 混用 inline style 和 class

```html
<div class="data-bar" style="color: red;"><!-- 不要這樣 --></div>
```

✅ **正確**:

```html
<div class="data-bar danger"><!-- 使用預定義變體 --></div>
```

❌ **錯誤 2**: 硬編碼數值

```html
<div style="padding: 20px;"><!-- 不要這樣 --></div>
```

✅ **正確**:

```html
<div class="p-lg"><!-- 使用設計變數 --></div>
```

❌ **錯誤 3**: 自己寫 media query

```html
@media (max-width: 768px) { ... }
<!-- 不需要 -->
```

✅ **正確**:

```html
<!-- 組件已內建響應式，無需額外處理 -->
```

---

**參考文檔**:

- 完整指南: `DESIGN_GUIDELINE.md`
- 快速參考: `DESIGN_QUICK_REFERENCE.md`
- 範例頁面: `templates/example_page.html`
