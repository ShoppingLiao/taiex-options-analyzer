# 日內價格走勢區塊 RWD 優化

## 📱 優化目標

修正「日內價格走勢」區塊在手機版的顯示問題，確保與其他區塊的 RWD 設計一致。

## 🔍 原始問題

### Before (舊版)

#### HTML 結構問題
```html
<div class="chart-container">
    <div style="text-align: center; padding: 40px;">
        <div style="font-size: 3rem;">收盤價</div>
        <div class="grid" style="max-width: 800px; margin: 0 auto;">
            <div style="padding: 15px; background: #f1f5f9;">
                開盤價格...
            </div>
            <!-- 其他價格項目 -->
        </div>
    </div>
</div>
```

#### CSS 問題
```css
.chart-container {
    padding: 24px;  /* 所有裝置都是 24px */
}

/* 沒有手機版特殊處理 */
```

#### 存在的問題
1. ❌ **過多 inline style**：維護困難，無法統一管理
2. ❌ **固定 padding**：手機版留白過多，浪費空間
3. ❌ **max-width 800px**：在小螢幕上限制了佈局靈活性
4. ❌ **字體大小固定**：手機版 3rem 太大，佔用過多空間
5. ❌ **與其他區塊不一致**：沒有套用統一的 RWD 優化

---

## ✅ 優化方案

### 1. CSS Class 化

#### HTML 結構優化
```html
<div class="chart-container">
    <div class="price-info-wrapper">
        <div class="close-price-display">30,456</div>
        <div class="close-price-label">收盤價格</div>
        <div class="grid price-grid">
            <div class="price-item" style="background: #f1f5f9;">
                <div class="price-item-label">開盤</div>
                <div class="price-item-value">30,234</div>
            </div>
            <!-- 其他價格項目 -->
        </div>
    </div>
</div>
```

**改善**：
- ✅ 移除 inline style
- ✅ 使用語義化 class 名稱
- ✅ 結構清晰，易於維護

---

### 2. Container Padding 優化

```css
.chart-container {
    background: var(--card-bg);
    border-radius: 12px;
    padding: 24px;  /* 電腦版 */
    margin-bottom: 30px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    border: 1px solid var(--border-color);
}

/* 手機版減少 chart-container padding */
@media (max-width: 767px) {
    .chart-container {
        padding: 12px;  /* 手機版減半 */
    }
}
```

**效果**：
- 💻 電腦版：24px padding，舒適間距
- 📱 手機版：12px padding，節省 24px 空間

---

### 3. 價格資訊 Wrapper

```css
.price-info-wrapper {
    text-align: center;
    padding: 40px 20px;  /* 電腦版 */
}

@media (max-width: 767px) {
    .price-info-wrapper {
        padding: 20px 12px;  /* 手機版減少 */
    }
}
```

**效果**：
- 💻 電腦版：40px 上下 padding
- 📱 手機版：20px 上下 padding，節省 40px 垂直空間

---

### 4. 收盤價顯示優化

```css
.close-price-display {
    font-size: 3rem;      /* 電腦版 */
    margin-bottom: 20px;
    font-weight: 600;
}

@media (max-width: 767px) {
    .close-price-display {
        font-size: 2rem;      /* 手機版減小 */
        margin-bottom: 12px;
    }
}
```

**效果**：
- 💻 電腦版：3rem (48px)，醒目顯示
- 📱 手機版：2rem (32px)，適中不過大

---

### 5. 價格標籤優化

```css
.close-price-label {
    font-size: 1.2rem;    /* 電腦版 */
    color: var(--text-muted);
    margin-bottom: 30px;
}

@media (max-width: 767px) {
    .close-price-label {
        font-size: 1rem;      /* 手機版 */
        margin-bottom: 20px;
    }
}
```

**效果**：
- 💻 電腦版：1.2rem (19.2px)
- 📱 手機版：1rem (16px)

---

### 6. Price Grid 優化

```css
.price-grid {
    max-width: 800px;  /* 電腦版限制最大寬度 */
    margin: 0 auto;
}

@media (max-width: 767px) {
    .price-grid {
        max-width: 100%;   /* 手機版使用全寬 */
    }
}
```

**說明**：
- 💻 電腦版：最大 800px，避免過寬
- 📱 手機版：100% 寬度，充分利用空間
- ✅ 自動套用 `.grid` 的 4 欄/3 欄佈局

---

### 7. 價格項目優化

```css
.price-item {
    padding: 15px;  /* 電腦版 */
    border-radius: 8px;
}

.price-item-label {
    font-size: 0.875rem;  /* 電腦版 */
    color: var(--text-muted);
    margin-bottom: 5px;
}

.price-item-value {
    font-size: 1.5rem;  /* 電腦版 */
    font-weight: 600;
}

@media (max-width: 767px) {
    .price-item {
        padding: 10px 8px;  /* 手機版更緊湊 */
    }

    .price-item-label {
        font-size: 0.75rem;  /* 手機版 */
        margin-bottom: 4px;
    }

    .price-item-value {
        font-size: 1.1rem;  /* 手機版 */
    }
}
```

**效果對比**：

| 元素 | 電腦版 | 手機版 | 說明 |
|------|--------|--------|------|
| Item padding | 15px | 10px 8px | 減少留白 |
| Label 字體 | 0.875rem (14px) | 0.75rem (12px) | 更緊湊 |
| Value 字體 | 1.5rem (24px) | 1.1rem (17.6px) | 適中可讀 |

---

## 📊 視覺效果對比

### 電腦版 (1920px)

```
┌──────────────────────────────────────────────────┐
│              日內價格走勢                         │
├──────────────────────────────────────────────────┤
│                                                  │
│                   30,456                         │
│                   收盤價格                        │
│                                                  │
│  ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐       │
│  │ 開盤  │ │ 最高  │ │ 最低  │ │震盪幅度│       │
│  │30,234 │ │30,567 │ │30,123 │ │  444  │       │
│  └───────┘ └───────┘ └───────┘ └───────┘       │
│                                                  │
└──────────────────────────────────────────────────┘
```

- 收盤價：3rem (48px)，醒目
- Grid：4 欄佈局，max-width 800px
- Item padding：15px
- 整體 padding：24px

### 手機版 (375px)

```
┌────────────────────┐
│  日內價格走勢      │
├────────────────────┤
│                    │
│     30,456         │ ← 2rem (32px)
│     收盤價格       │
│                    │
│ ┌────┐┌────┐┌────┐│ ← 3 欄佈局
│ │開盤││最高││最低││
│ │234 ││567 ││123 ││
│ └────┘└────┘└────┘│
│ ┌────────────────┐│
│ │  震盪幅度: 444 ││
│ └────────────────┘│
│                    │
└────────────────────┘
```

- 收盤價：2rem (32px)，適中
- Grid：3 欄佈局 (套用全域 grid 設定)
- Item padding：10px 8px
- 整體 padding：12px
- Wrapper padding：20px 12px

---

## 🎯 優化成效

### 空間節省

| 項目 | 電腦版 | 手機版 | 節省空間 |
|------|--------|--------|----------|
| Container padding | 24px | 12px | 24px (垂直) |
| Wrapper padding | 40px 20px | 20px 12px | 40px + 16px |
| 收盤價高度 | ~48px | ~32px | 16px |
| Item padding | 15px | 10px 8px | 10px + 14px |
| **總計節省** | - | - | **~120px** |

### 字體大小優化

| 元素 | 電腦版 | 手機版 | 改善 |
|------|--------|--------|------|
| 收盤價 | 3rem (48px) | 2rem (32px) | ✅ 減少 33% |
| 標籤 | 1.2rem (19.2px) | 1rem (16px) | ✅ 減少 17% |
| 項目標籤 | 0.875rem (14px) | 0.75rem (12px) | ✅ 減少 14% |
| 項目數值 | 1.5rem (24px) | 1.1rem (17.6px) | ✅ 減少 27% |

### Grid 佈局一致性

| 螢幕尺寸 | 舊版 | 新版 | 改善 |
|----------|------|------|------|
| 電腦 (≥1024px) | auto-fit | 4 欄 | ✅ 固定佈局 |
| 平板 (768-1023px) | auto-fit | 3 欄 | ✅ 固定佈局 |
| 手機 (<768px) | auto-fit | 3 欄 | ✅ 固定佈局 |

---

## 💡 設計理念

### 1. 語義化 Class 命名
```
price-info-wrapper    → 價格資訊包裝器
close-price-display   → 收盤價顯示
close-price-label     → 收盤價標籤
price-grid           → 價格網格
price-item           → 價格項目
price-item-label     → 項目標籤
price-item-value     → 項目數值
```

**優點**：
- 一看就懂用途
- 易於維護和擴展
- 符合 BEM 命名規範精神

### 2. 漸進式增強
```
基礎樣式 (所有裝置)
    ↓
電腦版優化 (大螢幕)
    ↓
手機版優化 (小螢幕)
```

### 3. 一致性設計
- Grid 佈局：與全域設定一致（4欄/3欄）
- Padding 策略：與其他 container 一致（24px/12px）
- 字體縮放：與整體設計系統一致

---

## 🔧 HTML 結構對比

### Before (舊版)
```html
<div class="chart-container">
    <div style="text-align: center; padding: 40px;">
        <div style="font-size: 3rem; margin-bottom: 20px;">
            30,456
        </div>
        <div style="font-size: 1.2rem; color: var(--text-muted); margin-bottom: 30px;">
            收盤價格
        </div>
        <div class="grid" style="max-width: 800px; margin: 0 auto;">
            <div style="padding: 15px; background: #f1f5f9; border-radius: 8px;">
                <div style="font-size: 0.875rem; color: var(--text-muted); margin-bottom: 5px;">開盤</div>
                <div style="font-size: 1.5rem; font-weight: 600;">30,234</div>
            </div>
            <!-- ... -->
        </div>
    </div>
</div>
```

**問題**：
- ❌ 大量 inline style
- ❌ 維護困難
- ❌ 無法統一調整
- ❌ 手機版無優化

### After (新版)
```html
<div class="chart-container">
    <div class="price-info-wrapper">
        <div class="close-price-display">30,456</div>
        <div class="close-price-label">收盤價格</div>
        <div class="grid price-grid">
            <div class="price-item" style="background: #f1f5f9;">
                <div class="price-item-label">開盤</div>
                <div class="price-item-value">30,234</div>
            </div>
            <!-- ... -->
        </div>
    </div>
</div>
```

**優點**：
- ✅ 語義化 class
- ✅ 易於維護
- ✅ 統一管理樣式
- ✅ RWD 完整支援

---

## 📱 實際效果展示

### iPhone 13 Pro (390px)

#### 舊版問題
```
收盤價佔用空間: 48px (字體) + 20px (margin) = 68px
Wrapper padding: 40px × 2 = 80px
Container padding: 24px × 2 = 48px
總浪費空間: ~196px
```

#### 新版優化
```
收盤價佔用空間: 32px (字體) + 12px (margin) = 44px
Wrapper padding: 20px × 2 = 40px
Container padding: 12px × 2 = 24px
總使用空間: ~108px
節省空間: 196px - 108px = 88px (減少 45%)
```

### iPad (1024px)

- Grid：3 欄佈局（平板版固定設定）
- 每項寬度：約 320px
- Gap：12px
- 顯示效果：整齊、專業

---

## ✅ 完成項目

- ✅ 移除 inline style，改用語義化 class
- ✅ chart-container padding：電腦 24px，手機 12px
- ✅ price-info-wrapper padding：電腦 40px 20px，手機 20px 12px
- ✅ 收盤價字體：電腦 3rem，手機 2rem
- ✅ 標籤字體：電腦 1.2rem，手機 1rem
- ✅ 項目 padding：電腦 15px，手機 10px 8px
- ✅ 項目字體：電腦 1.5rem/0.875rem，手機 1.1rem/0.75rem
- ✅ Grid 佈局：套用全域 4欄/3欄設定
- ✅ max-width：電腦 800px，手機 100%
- ✅ 手機版節省約 88px 垂直空間 (45%)
- ✅ 已更新模板：`templates/report.html`
- ✅ 已重新生成報告：`docs/report_20260109_202601.html`

---

## 🎨 CSS 完整清單

```css
/* 基礎樣式 */
.chart-container { padding: 24px; }
.price-info-wrapper { padding: 40px 20px; text-align: center; }
.close-price-display { font-size: 3rem; margin-bottom: 20px; font-weight: 600; }
.close-price-label { font-size: 1.2rem; color: var(--text-muted); margin-bottom: 30px; }
.price-grid { max-width: 800px; margin: 0 auto; }
.price-item { padding: 15px; border-radius: 8px; }
.price-item-label { font-size: 0.875rem; color: var(--text-muted); margin-bottom: 5px; }
.price-item-value { font-size: 1.5rem; font-weight: 600; }

/* 手機版優化 */
@media (max-width: 767px) {
    .chart-container { padding: 12px; }
    .price-info-wrapper { padding: 20px 12px; }
    .close-price-display { font-size: 2rem; margin-bottom: 12px; }
    .close-price-label { font-size: 1rem; margin-bottom: 20px; }
    .price-grid { max-width: 100%; }
    .price-item { padding: 10px 8px; }
    .price-item-label { font-size: 0.75rem; margin-bottom: 4px; }
    .price-item-value { font-size: 1.1rem; }
}
```

---

## 🚀 與全域設計的整合

### Grid 系統一致性
```css
/* 全域 Grid 設定 (已生效) */
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
}

@media (min-width: 1024px) {
    .grid { grid-template-columns: repeat(4, 1fr); }
}

@media (min-width: 768px) and (max-width: 1023px) {
    .grid { grid-template-columns: repeat(3, 1fr); }
}

@media (max-width: 767px) {
    .grid { 
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
    }
}

/* price-grid 自動繼承上述設定 */
.price-grid {
    /* 只需控制 max-width */
    max-width: 800px;  /* 電腦版 */
}

@media (max-width: 767px) {
    .price-grid {
        max-width: 100%;  /* 手機版 */
    }
}
```

**結果**：
- 電腦版：price-grid 顯示 4 欄
- 平板版：price-grid 顯示 3 欄  
- 手機版：price-grid 顯示 3 欄，gap 8px

---

## 📝 維護建議

### 修改字體大小
```css
/* 如果覺得手機版還太大 */
@media (max-width: 767px) {
    .close-price-display { font-size: 1.75rem; }  /* 更小 */
    .price-item-value { font-size: 1rem; }        /* 更緊湊 */
}
```

### 修改 Padding
```css
/* 如果需要更緊湊 */
@media (max-width: 767px) {
    .price-info-wrapper { padding: 16px 8px; }
    .price-item { padding: 8px 6px; }
}
```

### 修改 Grid 欄數
```css
/* 如果想在手機版顯示 2 欄 */
@media (max-width: 767px) {
    .price-grid {
        grid-template-columns: repeat(2, 1fr) !important;
    }
}
```

---

## 🎉 總結

這次優化將「日內價格走勢」區塊完全 RWD 化，並與全域設計系統保持一致：

1. ✅ **結構優化**：移除 inline style，使用語義化 class
2. ✅ **空間優化**：手機版節省 45% 垂直空間
3. ✅ **字體優化**：手機版字體大小適中，不過大也不過小
4. ✅ **佈局一致**：套用全域 Grid 4欄/3欄設定
5. ✅ **維護性**：統一在 CSS 中管理，易於調整

現在「日內價格走勢」區塊在手機版的顯示與其他區塊完全一致，提供了最佳的閱讀體驗！
