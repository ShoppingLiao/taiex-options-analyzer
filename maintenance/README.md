# 維護工具與歷史記錄

此資料夾包含專案開發過程中的一次性更新腳本和歷史更新報告。

## 📁 資料夾結構

```
maintenance/
├── README.md           # 本文件
├── scripts/            # 一次性更新腳本
│   ├── update_section_content.py
│   ├── add_section_content_css.py
│   ├── update_ai_performance_layout.py
│   └── update_border_radius.py
└── reports/            # 更新記錄與報告
    ├── SETTLEMENT_REPORT_STYLE_FIX.md
    ├── SECTION_CONTENT_ALL_REPORTS_UPDATE.md
    ├── SECTION_CONTENT_CLASS_UPDATE.md
    ├── SECTION_CONTENT_CSS_FIX.md
    ├── SECTION_CONTENT_FONT_SIZE_ADJUSTMENT.md
    ├── SECTION_CONTENT_MIGRATION_SUMMARY.md
    ├── BORDER_RADIUS_UPDATE_REPORT.md
    └── SETTLEMENT_TABS_TYPOGRAPHY_UPDATE.md
```

## 🔧 scripts/ - 一次性更新腳本

這些腳本用於批量更新已生成的報告文件，**僅在需要修復歷史文件時使用**。

### update_section_content.py

**用途**: 批量替換內聯樣式為 `section-content` class  
**執行時機**: 當需要將舊版報告更新為使用 section-content class 時  
**影響範圍**: reports/ 和 docs/ 中的所有 HTML 文件

```bash
python3 maintenance/scripts/update_section_content.py
```

### add_section_content_css.py

**用途**: 為已生成的報告添加 section-content CSS 定義  
**執行時機**: 當已生成的報告缺少 section-content 樣式定義時  
**影響範圍**: 指定的 HTML 文件

```bash
python3 maintenance/scripts/add_section_content_css.py
```

### update_ai_performance_layout.py

**用途**: 將 AI 預測績效總覽從 grid 布局更新為橫排單行布局  
**執行時機**: 當需要修復舊版結算日報告的 AI 績效總覽樣式時  
**影響範圍**: 結算日報告文件

```bash
python3 maintenance/scripts/update_ai_performance_layout.py
```

### update_border_radius.py

**用途**: 統一更新所有元素的 border-radius 為 2px  
**執行時機**: 當需要調整圓角風格時  
**影響範圍**: templates/ 中的所有模板文件

```bash
python3 maintenance/scripts/update_border_radius.py
```

## 📝 reports/ - 更新記錄與報告

這些文檔記錄了專案第一版開發過程中的重要更新和調整。

### 樣式系統更新

- **SECTION_CONTENT_MIGRATION_SUMMARY.md**  
  Section-content class 系統的完整遷移總結

- **SECTION_CONTENT_ALL_REPORTS_UPDATE.md**  
  應用 section-content 到所有報告的記錄

- **SECTION_CONTENT_CLASS_UPDATE.md**  
  Section-content class 建立過程

- **SECTION_CONTENT_CSS_FIX.md**  
  修復 CSS 定義缺失的問題

- **SECTION_CONTENT_FONT_SIZE_ADJUSTMENT.md**  
  字體大小和行高的調整記錄

### 結算日報告更新

- **SETTLEMENT_REPORT_STYLE_FIX.md**  
  修復結算日報告的寬度和 AI 績效總覽樣式問題

- **SETTLEMENT_TABS_TYPOGRAPHY_UPDATE.md**  
  統一結算日報告分頁的字體樣式

### 設計系統更新

- **BORDER_RADIUS_UPDATE_REPORT.md**  
  全專案 border-radius 統一為 2px 的更新記錄

## ⚠️ 重要提醒

### 這些腳本不應再被執行

這些腳本是為了修復 **第一版開發過程中** 已生成的報告文件。

**未來生成的報告會自動使用正確的模板**，因為：

1. ✅ `templates/report.html` 已包含所有正確樣式
2. ✅ `templates/settlement_report.html` 已包含所有正確樣式
3. ✅ `templates/design_system.html` 已定義完整的設計系統

### 如果需要更新樣式

**正確做法**:

1. 修改 `templates/` 中的模板文件
2. 重新執行生成腳本（如 `generate_settlement_report.py`）
3. 新生成的報告會自動使用更新後的樣式

**錯誤做法**:

1. ❌ 執行 maintenance/scripts/ 中的腳本
2. ❌ 手動修改已生成的報告文件

## 📚 歷史意義

這些文件記錄了專案從初期到第一版正式發布的演進過程：

- **2026/01/09**: 建立 section-content class 系統
- **2026/01/10**: 應用到所有報告並調整字體大小
- **2026/01/11**: 修復 CSS 缺失問題
- **2026/01/12**: 統一 border-radius 和結算日報告字體
- **2026/01/13**: 修復 AI 績效總覽和寬度問題，完成第一版

## 🎯 第一版完成標誌

當所有文件移動到此資料夾後，代表：

1. ✅ 設計系統已穩定
2. ✅ 模板文件已包含所有必要樣式
3. ✅ 未來生成的報告會自動保持一致性
4. ✅ 不再需要批量更新已生成的文件

---

**第一版發布日期**: 2026 年 1 月 13 日  
**維護者**: Shopping Liao
