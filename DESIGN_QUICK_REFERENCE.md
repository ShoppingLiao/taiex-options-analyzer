# Design System 快速參考

## 🎨 常用組件速查

### 數據展示

```html
<!-- 單行數據條 (移動端推薦) -->
<div class="data-bar primary">
  <span class="data-bar-label">📊 標籤：</span>
  <span class="data-bar-value">數值</span>
  <span class="data-bar-hint">說明</span>
</div>

<!-- 數據卡片 (桌面端推薦) -->
<div class="data-card">
  <div class="data-card-label">標籤</div>
  <div class="data-card-value">數值</div>
  <div class="data-card-subtitle">副標題</div>
</div>
```

### 區塊結構

```html
<!-- 標準 Section -->
<div class="section">
  <div class="section-header">
    <span class="section-icon">📊</span>
    <h2 class="section-title">標題</h2>
    <span class="section-count">5 份</span>
  </div>
  <!-- 內容 -->
</div>

<!-- 帶漸層背景的 Section -->
<div class="section gradient-primary">
  <!-- 藍色漸層背景 -->
</div>
```

### 頁首

```html
<header class="page-header">
  <h1>{{ title }}</h1>
  <p class="subtitle">{{ subtitle }}</p>

  <div class="info-items">
    <div class="info-item">
      <div class="info-label">標籤</div>
      <div class="info-value">數值</div>
    </div>
  </div>
</header>
```

### 標籤頁

```html
<!-- 按鈕組 -->
<div class="tabs-container">
  <button class="tab-button active">
    <span class="tab-icon">📊</span> 標籤1
  </button>
</div>

<!-- 內容區 -->
<div id="tab1" class="tab-content active">...</div>
```

### 網格佈局

```html
<div class="grid grid-4">...</div>
<!-- 4 欄 -->
<div class="grid grid-auto-md">...</div>
<!-- 自適應 -->
```

## 🎨 色彩變體

```html
<!-- Border 顏色 -->
.primary → 藍色 .success → 綠色 (看多/Put) .danger → 紅色 (看空/Call) .warning →
橙色 (中性/結算) .purple → 紫色 (AI)

<!-- 漸層背景 -->
.gradient-primary .gradient-success .gradient-danger .gradient-warning
.gradient-purple
```

## 📏 間距工具

```html
.mb-sm .mb-md .mb-lg .mb-xl → margin-bottom .mt-sm .mt-md .mt-lg .mt-xl →
margin-top .p-sm .p-md .p-lg .p-xl → padding
```

## 🔤 文字工具

```html
<!-- 大小 -->
.text-xxl .text-xl .text-lg .text-md .text-base .text-sm .text-xs .text-xxs

<!-- 粗細 -->
.font-bold .font-semibold .font-medium

<!-- 顏色 -->
.text-primary .text-success .text-danger .text-warning .text-muted
```

## 🔄 快速調整

### 調整主色調

```css
/* templates/design_system.html */
:root {
  --primary-color: #新顏色;
}
```

### 調整移動端字體

```css
:root {
  --font-xl-mobile: 1.8rem; /* 調大 */
}
```

### 調整間距

```css
:root {
  --space-lg: 24px; /* 調大 */
}
```

## 📱 響應式

系統會自動在 `@media (max-width: 768px)` 套用移動端樣式：

- 字體自動縮小 30-40%
- 間距自動縮小 50%
- 網格自動調整欄數

## 🚀 使用流程

1. **引入設計系統**

   ```html
   {% include 'design_system.html' %}
   ```

2. **使用組件 class**

   ```html
   <div class="section">
     <div class="data-bar primary">...</div>
   </div>
   ```

3. **需要調整時修改 `design_system.html`**
   - 一次修改，全站生效！

## ⚠️ 注意事項

❌ **不要這樣做:**

```html
<div style="color: #2563eb; font-size: 1.5rem;"></div>
```

✅ **應該這樣做:**

```html
<div class="text-md text-primary"></div>
```

---

**完整文檔**: 請參考 `DESIGN_GUIDELINE.md`
