# 台指選擇權分析系統 - Design System v1.0

## 📋 目錄

1. [概述](#概述)
2. [設計變數](#設計變數)
3. [組件清單](#組件清單)
4. [使用方式](#使用方式)
5. [調整指南](#調整指南)

---

## 概述

本設計系統提供統一的視覺規範與可重用組件，確保所有頁面的一致性。

### 設計原則

- **統一性**: 所有頁面使用相同的設計變數
- **響應式**: 自動適配桌面與移動設備
- **可維護**: 只需修改 `design_system.html` 即可全局調整
- **簡潔性**: 最小化組件數量，最大化重用性

### 檔案架構

```
templates/
  ├── design_system.html       # 設計系統核心文件
  ├── settlement_report.html   # 結算日報告 (使用設計系統)
  └── report.html              # 單日報告 (使用設計系統)
docs/
  └── index.html               # 首頁 (使用設計系統)
```

---

## 設計變數

### 1. 色彩系統

#### 主要色彩

```css
--primary-color: #2563eb     /* 主色調 - 藍色 */
--success-color: #22c55e     /* 成功/看多 - 綠色 */
--danger-color: #ef4444      /* 危險/看空 - 紅色 */
--warning-color: #f59e0b     /* 警告/中性 - 橙色 */
--purple-color: #8b5cf6      /* 紫色 - AI/特殊 */
```

#### 使用情境

- **Primary (藍色)**: 主要功能、連結、強調元素
- **Success (綠色)**: 看多方向、正面數據、Put 選擇權
- **Danger (紅色)**: 看空方向、負面數據、Call 選擇權
- **Warning (橙色)**: 中性方向、注意事項、結算相關
- **Purple (紫色)**: AI 功能、特殊分析、檢討報告

### 2. 字體系統

#### Desktop 字體階層

```css
--font-xxl: 3rem      /* 48px - 超大標題 */
--font-xl: 2.5rem     /* 40px - 大標題 */
--font-lg: 2rem       /* 32px - 標題 */
--font-md: 1.5rem     /* 24px - 中標題 */
--font-base: 1.3rem   /* 20.8px - 基礎大小 */
--font-sm: 1.1rem     /* 17.6px - 小字 */
--font-xs: 0.95rem    /* 15.2px - 更小字 */
--font-xxs: 0.85rem   /* 13.6px - 極小字 */
--font-micro: 0.75rem /* 12px - 微小字 */
```

#### Mobile 字體 (自動縮減 30-40%)

```css
--font-xxl-mobile: 2rem       /* 32px */
--font-xl-mobile: 1.5rem      /* 24px */
--font-lg-mobile: 1.3rem      /* 20.8px */
--font-md-mobile: 1.2rem      /* 19.2px */
--font-base-mobile: 1rem      /* 16px */
/* ... 以此類推 */
```

### 3. 間距系統

#### Desktop 間距

```css
--space-xs: 8px
--space-sm: 12px
--space-md: 16px
--space-lg: 20px
--space-xl: 24px
--space-xxl: 30px
--space-xxxl: 40px
```

#### Mobile 間距 (縮減 50%)

```css
--space-xs-mobile: 4px
--space-sm-mobile: 6px
--space-md-mobile: 8px
/* ... 以此類推 */
```

### 4. 其他設計變數

```css
--radius-sm: 8px      /* 小圓角 */
--radius-md: 12px     /* 中圓角 */
--radius-lg: 16px     /* 大圓角 */

--shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.1)
--shadow-md: 0 4px 12px rgba(0, 0, 0, 0.1)
--shadow-lg: 0 10px 40px rgba(0, 0, 0, 0.1)
```

---

## 組件清單

### 1. Layout Components (佈局組件)

#### 1.1 Container

```html
<div class="container">
  <!-- 內容, max-width: 1200px -->
</div>

<div class="container-wide">
  <!-- 較寬內容, max-width: 1400px -->
</div>
```

#### 1.2 Section

```html
<div class="section">
  <div class="section-header">
    <span class="section-icon">📊</span>
    <h2 class="section-title">標題</h2>
    <span class="section-count">5 份報告</span>
  </div>
  <p class="section-description">描述文字</p>
  <!-- 內容 -->
</div>
```

### 2. Card Components (卡片組件)

#### 2.1 Basic Card

```html
<div class="card">
  <!-- 基礎卡片內容 -->
</div>
```

#### 2.2 Data Card (數據展示)

```html
<div class="data-card">
  <div class="data-card-label">標籤</div>
  <div class="data-card-value">30,372</div>
  <div class="data-card-subtitle">副標題</div>
</div>
```

#### 2.3 Horizontal Data Bar (單行數據條) ⭐ 推薦

```html
<div class="data-bar primary">
  <span class="data-bar-label">📊 總預測次數：</span>
  <span class="data-bar-value">2</span>
  <span class="data-bar-hint">累積經驗</span>
</div>

<!-- 變體：success, danger, warning, purple -->
<div class="data-bar success">...</div>
<div class="data-bar danger">...</div>
```

#### 2.4 Info Card (資訊卡片)

```html
<div class="info-card primary">
  <div class="info-card-header">
    <span class="info-card-title">🕐 結算前準備</span>
  </div>
  <div class="info-card-content">
    <p><span class="font-medium">時機：</span>結算前 1 小時</p>
    <p><span class="font-medium">動作：</span>調整部位</p>
  </div>
</div>
```

### 3. Header Components (頁首組件)

#### 3.1 Page Header

```html
<header class="page-header">
  <h1>頁面標題</h1>
  <p class="subtitle">副標題</p>

  <div class="info-items">
    <div class="info-item">
      <div class="info-label">標籤</div>
      <div class="info-value">數值</div>
    </div>
    <!-- 更多 info-item -->
  </div>
</header>
```

### 4. Tab Components (標籤頁)

```html
<div class="tabs-container">
  <button class="tab-button active" onclick="switchTab('tab1')">
    <span class="tab-icon">📊</span>
    技術分析
  </button>
  <button class="tab-button" onclick="switchTab('tab2')">
    <span class="tab-icon">🤖</span>
    AI 分析
  </button>
</div>

<div id="tab1" class="tab-content active">
  <!-- Tab 1 內容 -->
</div>

<div id="tab2" class="tab-content">
  <!-- Tab 2 內容 -->
</div>
```

### 5. Grid & Layout (網格佈局)

```html
<!-- 固定欄數 -->
<div class="grid grid-2">...</div>
<!-- 2 欄 -->
<div class="grid grid-3">...</div>
<!-- 3 欄 -->
<div class="grid grid-4">...</div>
<!-- 4 欄 -->

<!-- 自適應欄數 -->
<div class="grid grid-auto-sm">...</div>
<!-- 最小 150px -->
<div class="grid grid-auto-md">...</div>
<!-- 最小 250px -->
<div class="grid grid-auto-lg">...</div>
<!-- 最小 350px -->

<!-- Flexbox -->
<div class="flex gap-md">...</div>
<div class="flex-between">...</div>
<div class="flex-center">...</div>
```

### 6. Typography (文字樣式)

```html
<h1 class="text-xl font-bold text-primary">標題</h1>
<p class="text-sm text-muted">描述文字</p>

<!-- 顏色 -->
<span class="text-primary">主色</span>
<span class="text-success">成功</span>
<span class="text-danger">危險</span>
<span class="text-warning">警告</span>
```

### 7. Badges (徽章)

```html
<span class="badge badge-primary">主要</span>
<span class="badge badge-success">成功</span>
<span class="badge badge-latest">最新報告</span>
```

### 8. Buttons (按鈕)

```html
<a href="#" class="btn btn-primary">
  <span>🏠</span>
  回首頁
</a>

<button class="btn btn-ghost">Ghost 按鈕</button>
```

### 9. Chart Container (圖表容器)

```html
<div class="chart-container">
  <h3 class="chart-title">圖表標題</h3>
  <div id="chart"></div>
</div>
```

### 10. Special Components (特殊組件)

```html
<!-- 漸層背景區塊 -->
<div class="section gradient-primary">...</div>
<div class="section gradient-success">...</div>

<!-- 可滾動容器 -->
<div class="scrollable">...</div>

<!-- 空狀態 -->
<div class="empty-state">
  <div class="empty-state-icon">📭</div>
  <div class="empty-state-text">沒有資料</div>
  <div class="empty-state-hint">提示文字</div>
</div>
```

---

## 使用方式

### 步驟 1: 引入設計系統

在 Jinja2 模板的 `<head>` 區域引入：

```html
<!DOCTYPE html>
<html lang="zh-TW">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>頁面標題</title>

    <!-- 引入設計系統 -->
    {% include 'design_system.html' %}

    <!-- 頁面特定樣式 (可選) -->
    <style>
      /* 僅在此頁面特有的樣式 */
    </style>
  </head>
</html>
```

### 步驟 2: 使用組件

直接使用預定義的 CSS class：

```html
<body>
  <div class="container">
    <header class="page-header">
      <h1>{{ title }}</h1>
      <p class="subtitle">{{ subtitle }}</p>
    </header>

    <div class="section">
      <div class="section-header">
        <span class="section-icon">📊</span>
        <h2 class="section-title">數據分析</h2>
      </div>

      <!-- 使用數據條組件 -->
      <div class="data-bar primary">
        <span class="data-bar-label">📈 當前價格：</span>
        <span class="data-bar-value">{{ price }}</span>
        <span class="data-bar-hint">點</span>
      </div>
    </div>
  </div>
</body>
```

### 步驟 3: 自定義樣式 (可選)

如果需要頁面特定的調整，在 `{% include %}` 後添加：

```html
<style>
  /* 覆寫或擴展設計系統 */
  .custom-component {
    /* 使用設計變數 */
    color: var(--primary-color);
    padding: var(--space-lg);
    border-radius: var(--radius-md);
  }
</style>
```

---

## 調整指南

### 如何進行全局調整？

所有視覺調整都在 `templates/design_system.html` 中進行。

#### 範例 1: 調整主色調

```css
/* 在 design_system.html 中修改 */
:root {
  --primary-color: #3b82f6; /* 改為較亮的藍色 */
}
```

✅ 影響: 所有使用主色的按鈕、連結、標題都會改變

#### 範例 2: 調整移動端字體大小

```css
:root {
  --font-xl-mobile: 1.8rem; /* 從 1.5rem 增加到 1.8rem */
}
```

✅ 影響: 所有使用 `.text-xl` 的移動端標題都會變大

#### 範例 3: 調整卡片圓角

```css
:root {
  --radius-md: 16px; /* 從 12px 增加到 16px */
}
```

✅ 影響: 所有使用 `border-radius: var(--radius-md)` 的卡片

#### 範例 4: 調整間距系統

```css
:root {
  --space-lg: 24px; /* 從 20px 增加到 24px */
  --space-lg-mobile: 12px; /* 從 10px 增加到 12px */
}
```

✅ 影響: 所有使用 `var(--space-lg)` 的元素間距

### 常見調整情境

#### 情境 1: 使用者反饋「移動端字太小」

```css
/* 統一增加所有移動端字體 10% */
:root {
  --font-xl-mobile: 1.65rem; /* 1.5 * 1.1 */
  --font-lg-mobile: 1.43rem; /* 1.3 * 1.1 */
  --font-md-mobile: 1.32rem; /* 1.2 * 1.1 */
  /* ... 依此類推 */
}
```

#### 情境 2: 使用者反饋「卡片太擁擠」

```css
/* 增加卡片內距 */
.data-card,
.card {
  padding: var(--space-xl); /* 從 var(--space-md) 改為 var(--space-xl) */
}
```

#### 情境 3: 改變色彩風格（例如深色主題）

```css
:root {
  --primary-color: #3b82f6;
  --bg-color: #1e293b;
  --card-bg: #334155;
  --text-color: #f1f5f9;
  --text-muted: #94a3b8;
  --border-color: #475569;
}
```

### 維護建議

1. **禁止在模板中使用硬編碼值**
   ❌ 錯誤: `<div style="font-size: 1.5rem; color: #2563eb;">`
   ✅ 正確: `<div class="text-md text-primary">`

2. **新增自定義樣式時優先使用設計變數**
   ❌ 錯誤: `padding: 20px;`
   ✅ 正確: `padding: var(--space-lg);`

3. **新增組件時考慮響應式**

   ```css
   .new-component {
     font-size: var(--font-base);
   }

   @media (max-width: 768px) {
     .new-component {
       font-size: var(--font-base-mobile);
     }
   }
   ```

4. **定期審查是否有重複組件可以合併**
   - 如果發現多個頁面使用相似的樣式
   - 將其抽象為新組件加入 design_system.html

---

## 組件選擇指南

### 何時使用哪種組件？

| 需求                  | 推薦組件                       | 原因                           |
| --------------------- | ------------------------------ | ------------------------------ |
| 顯示單一數據          | `.data-card`                   | 垂直佈局，適合強調單一指標     |
| 顯示多個數據 (移動端) | `.data-bar`                    | 水平佈局，節省垂直空間         |
| 顯示帶說明的資訊      | `.info-card`                   | 支援標題、內容、徽章           |
| 頁面主要分區          | `.section`                     | 帶標題、圖標、統計數的完整區塊 |
| 數據網格              | `.grid .grid-4` + `.data-card` | 桌面 4 欄，移動 2 欄           |
| 可滾動列表            | `.scrollable`                  | 自動添加美化的滾動條           |

### 範例組合

#### 移動優先的數據展示

```html
<div class="section">
  <div class="section-header">
    <span class="section-icon">📊</span>
    <h2 class="section-title">績效總覽</h2>
  </div>

  <!-- 使用 data-bar 在移動端效果更好 -->
  <div class="data-bar primary">
    <span class="data-bar-label">📈 總預測次數：</span>
    <span class="data-bar-value">{{ total }}</span>
    <span class="data-bar-hint">次</span>
  </div>

  <div class="data-bar success">
    <span class="data-bar-label">✅ 平均準確度：</span>
    <span class="data-bar-value">{{ accuracy }}%</span>
    <span class="data-bar-hint">整體表現</span>
  </div>
</div>
```

#### 桌面優先的數據展示

```html
<div class="section">
  <div class="grid grid-4">
    <div class="data-card">
      <div class="data-card-label">總預測次數</div>
      <div class="data-card-value text-primary">{{ total }}</div>
      <div class="data-card-subtitle">累積經驗</div>
    </div>
    <!-- 更多 data-card -->
  </div>
</div>
```

---

## 版本歷史

### v1.0 (2026/01/12)

- ✅ 初始版本發布
- ✅ 定義完整設計變數系統
- ✅ 創建 14 類核心組件
- ✅ 支援桌面與移動端響應式
- ✅ 統一色彩、字體、間距系統

---

## 聯絡與支持

如有問題或建議，請聯繫：

- GitHub: https://github.com/ShoppingLiao/taiex-options-analyzer
- 文檔位置: `/Users/shopping.liao/Documents/code/taiex-options-analyzer/DESIGN_GUIDELINE.md`
