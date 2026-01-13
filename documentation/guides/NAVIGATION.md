# 網站導航功能說明

## 🏠 回首頁功能

所有報告頁面的右上角（手機版在標題下方）都有「🏠 回首頁」按鈕，方便快速返回報告總覽。

### 功能特色

- **桌面版**：按鈕位於 header 右上角
- **手機版**：按鈕置中顯示在標題下方
- **視覺效果**：
  - 半透明白色背景 + 毛玻璃效果
  - Hover 時上浮動畫
  - 包含 🏠 emoji 圖標

### 技術實現

使用純 HTML + CSS 實現，無需額外 JavaScript：

```html
<a href="index.html" class="home-button">
    <span>🏠</span>
    <span>回首頁</span>
</a>
```

### CSS 樣式

- `backdrop-filter: blur(10px)` - 毛玻璃效果
- `position: absolute` - 桌面版固定在右上角
- `@media (max-width: 768px)` - 手機版響應式調整

### 為什麼不用 React？

選擇純 HTML 方案而非 React + React Router 的原因：

1. ✅ **簡單高效**：靜態報告不需要 SPA 複雜性
2. ✅ **載入速度快**：無需下載 React 框架（~45KB gzip）
3. ✅ **SEO 友好**：搜尋引擎直接索引 HTML
4. ✅ **零建置成本**：不需要 Webpack/Vite 等建置工具
5. ✅ **易於維護**：模板系統已足夠

### 瀏覽器支援

- Chrome/Edge: ✅ 完整支援
- Firefox: ✅ 完整支援
- Safari: ✅ 完整支援（含毛玻璃效果）
- Mobile: ✅ 完整響應式支援

## 導航流程

```
首頁 (index.html)
    ├── 2026/01/09 報告 → [🏠 回首頁]
    ├── 2026/01/08 報告 → [🏠 回首頁]
    ├── 2026/01/07 報告 → [🏠 回首頁]
    ├── 2026/01/06 報告 → [🏠 回首頁]
    └── 2026/01/05 報告 → [🏠 回首頁]
```

## 未來擴展

如需更複雜的導航（如：上一頁/下一頁），可以在模板中添加：

```html
<div class="navigation-buttons">
    <a href="report_20260108_202601.html">← 前一天</a>
    <a href="index.html">🏠 首頁</a>
    <a href="report_20260110_202601.html">後一天 →</a>
</div>
```
