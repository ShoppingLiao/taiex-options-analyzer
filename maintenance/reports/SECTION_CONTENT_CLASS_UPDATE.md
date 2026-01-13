# Section-Content Class 新增與應用

## 📊 更新總結

**更新時間**: 2026 年 1 月 13 日  
**更新目標**: 新增 `section-content` class 統一管理內容區塊樣式  
**更新範圍**: Design System + 交易員視角 Tab

---

## 🎨 新增的 Class: `section-content`

### 1. 基本樣式

```css
.section-content {
  background: var(--card-bg);
  padding: var(--space-xl); /* 24px */
  border-radius: var(--radius-sm); /* 8px */
  border-left: var(--border-width-thick) solid var(--primary-color); /* 4px */
  box-shadow: var(--shadow-md);
  line-height: 1.8;
  white-space: pre-wrap;
  font-size: 0.8rem; /* 統一字體大小 */
  color: #3c3c3c;
}
```

### 2. 主題變化 (Modifier Classes)

#### 預設主題 (藍色)

```html
<div class="section-content">內容...</div>
```

- 左側邊框: 藍色 (`--primary-color`)
- 背景: 白色

#### Success 主題 (綠色)

```html
<div class="section-content success">內容...</div>
```

- 左側邊框: 綠色 (`--success-color`)
- 背景: 白色
- 用途: 策略、成功案例

#### Danger 主題 (紅色)

```html
<div class="section-content danger">內容...</div>
```

- 左側邊框: 紅色 (`--danger-color`)
- 背景: 淺紅色 (`#fef2f2`)
- 用途: 風險警示、注意事項

#### Warning 主題 (橙色)

```html
<div class="section-content warning">內容...</div>
```

- 左側邊框: 橙色 (`--warning-color`)
- 背景: 白色
- 用途: 執行計劃、提醒事項

#### Purple 主題 (紫色)

```html
<div class="section-content purple">內容...</div>
```

- 左側邊框: 紫色 (`--purple-color`)
- 背景: 白色
- 用途: AI 分析、特殊內容

### 3. 手機版響應式

```css
@media (max-width: 768px) {
  .section-content {
    padding: var(--space-lg-mobile); /* 10px */
    font-size: 0.75rem; /* 縮小為 0.75rem */
  }
}
```

---

## 📝 應用範例：交易員視角 Tab

### Before (使用 inline style)

```html
<div class="section">
  <div class="section-header">
    <span class="section-icon">👁️</span>
    <h2 class="section-title">我對結算日的看法</h2>
  </div>
  <div
    style="background: white; padding: 25px; border-radius: 2px; border-left: 4px solid var(--primary-color); box-shadow: 0 4px 12px rgba(0,0,0,0.08); line-height: 1.8; white-space: pre-wrap; font-size: 0.85rem; color: #3c3c3c;"
  >
    {{ settlement_trader_analysis.settlement_outlook }}
  </div>
</div>
```

### After (使用 class)

```html
<div class="section">
  <div class="section-header">
    <span class="section-icon">👁️</span>
    <h2 class="section-title">我對結算日的看法</h2>
  </div>
  <div class="section-content">
    {{ settlement_trader_analysis.settlement_outlook }}
  </div>
</div>
```

### 已更新的區塊

1. **我對結算日的看法**
   - Class: `section-content` (預設藍色)
2. **我的結算日策略**
   - Class: `section-content success` (綠色)
3. **我最擔心的風險**
   - Class: `section-content danger` (紅色 + 淺紅背景)
4. **我的執行計劃**
   - Class: `section-content warning` (橙色)

---

## ✅ 優勢與改進

### 1. 程式碼簡潔度

**Before:**

- 每個區塊需要寫 8-10 行 inline style
- 難以維護和修改

**After:**

- 只需 1 個 class 名稱
- 樣式集中管理

### 2. 一致性

- ✅ 字體大小統一為 `0.8rem`
- ✅ Padding 統一為 `24px` (桌面) / `10px` (手機)
- ✅ 行高統一為 `1.8`
- ✅ 圓角統一為 `8px`

### 3. 可維護性

- ✅ 所有樣式在 Design System 統一定義
- ✅ 只需修改一處即可全域生效
- ✅ 支援主題切換（藍/綠/紅/橙/紫）

### 4. 響應式設計

- ✅ 自動適配手機版
- ✅ 手機版字體自動縮小為 `0.75rem`
- ✅ 手機版 padding 自動縮小為 `10px`

---

## 🎯 設計規範

### 使用場景

| 場景               | 使用 Class                | 顏色主題 |
| ------------------ | ------------------------- | -------- |
| 一般內容、分析觀點 | `section-content`         | 藍色     |
| 策略建議、成功案例 | `section-content success` | 綠色     |
| 風險警示、注意事項 | `section-content danger`  | 紅色     |
| 執行計劃、提醒事項 | `section-content warning` | 橙色     |
| AI 分析、特殊內容  | `section-content purple`  | 紫色     |

### 搭配使用

```html
<!-- 標準結構 -->
<div class="section">
  <div class="section-header">
    <span class="section-icon">🎯</span>
    <h2 class="section-title">標題</h2>
  </div>
  <div class="section-content [主題]">內容...</div>
</div>
```

---

## 📐 CSS 變數對照

| CSS 變數               | 值                         | 說明           |
| ---------------------- | -------------------------- | -------------- |
| `--space-xl`           | 24px                       | 桌面版 padding |
| `--space-lg-mobile`    | 10px                       | 手機版 padding |
| `--radius-sm`          | 8px                        | 圓角大小       |
| `--border-width-thick` | 4px                        | 左側邊框寬度   |
| `--shadow-md`          | 0 4px 12px rgba(0,0,0,0.1) | 陰影           |

---

## 🔧 後續應用建議

### 可套用的地方

1. **結算日 AI 預測 Tab**

   - 結算展望
   - 策略建議的各個區塊

2. **盤後檢討 Tab**

   - 自我反思
   - 學到的教訓
   - 改進方向

3. **單日報告模板 (report.html)**

   - AI 交易建議
   - 風險提示
   - 策略內容

4. **其他需要統一樣式的內容區塊**

### 使用範例

```html
<!-- AI 預測展望 -->
<div class="section">
  <div class="section-header">
    <span class="section-icon">💡</span>
    <h2 class="section-title">我的結算展望</h2>
  </div>
  <div class="section-content">{{ ai_settlement_prediction.outlook }}</div>
</div>

<!-- 風險控制 -->
<div class="section">
  <div class="section-header">
    <span class="section-icon">🛡️</span>
    <h2 class="section-title">風險控制</h2>
  </div>
  <div class="section-content danger">{{ risk_control_content }}</div>
</div>
```

---

## 📊 Before/After 對比

### 程式碼行數

- **Before**: 10 行 (含 inline style)
- **After**: 3 行 (使用 class)
- **減少**: 70%

### 維護成本

- **Before**: 需要在每個檔案修改相同的樣式
- **After**: 只需修改 Design System 一處

### 一致性

- **Before**: 各處可能有微小差異 (0.85rem vs 0.8rem)
- **After**: 100% 一致

---

## ✨ 總結

### 更新檔案

1. `templates/design_system.html`

   - 新增 `.section-content` 及其主題變化
   - 新增響應式樣式

2. `templates/settlement_report.html`
   - 交易員視角 4 個區塊改用 `section-content`

### 關鍵特性

- ✅ 字體大小: `0.8rem` (桌面) / `0.75rem` (手機)
- ✅ 5 種主題色: 藍/綠/紅/橙/紫
- ✅ 完整響應式支援
- ✅ 統一 Design System 管理
- ✅ 大幅簡化程式碼

### 下一步

可以將此 class 應用到其他需要類似樣式的區塊，實現全專案統一管理！

---

**更新完成！** 🎉
