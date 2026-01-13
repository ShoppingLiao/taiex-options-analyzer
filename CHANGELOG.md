# 變更日誌 (Changelog)

本文件記錄所有重要變更。遵循 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.0.0/) 格式。

專案遵循 [語義化版本](https://semver.org/lang/zh-TW/)。

## [1.0.0] - 2026-01-13

### 🎉 第一版正式發布

這是台指選擇權分析系統的第一個正式版本，標誌著設計系統、報告模板和樣式規範已經穩定。

### 新增 (Added)

#### 專案結構

- 新增 `maintenance/` 資料夾用於整理歷史工具和記錄
- 新增 `maintenance/scripts/` 存放一次性更新腳本
- 新增 `maintenance/reports/` 存放開發過程記錄

#### 文檔系統

- 新增 `VERSION_HISTORY.md` - 版本歷史與未來規劃
- 新增 `RELEASE_v1.0.0.md` - 版本 1.0.0 發布說明
- 新增 `PROJECT_STRUCTURE.md` - 專案結構總覽
- 新增 `CHANGELOG.md` - 本文件
- 新增 `maintenance/README.md` - 維護工具說明

#### 設計系統

- 新增 Section-Content Class 系統（5 種主題變體）
- 新增統一的視覺規範（border-radius: 2px）
- 新增自定義滾動條樣式（3px 細滾動條）

#### 報告功能

- 新增 AI 預測績效總覽（橫排單行布局）
- 新增 Header 資訊區水平滾動功能
- 新增完整的響應式設計支援

### 變更 (Changed)

#### README

- 更新版本徽章為 v1.0.0
- 添加第一版發布公告
- 更新專案結構說明（包含 maintenance/）
- 新增文檔索引區塊

#### 字體優化

- 桌面版字體: 0.8rem → 0.95rem
- 手機版字體: 0.75rem → 0.85rem
- 行高: 1.8 → 1.9

#### 布局優化

- AI 預測績效總覽: Grid 4 列布局 → 橫排單行布局
- Settlement-info: 添加 `overflow-x: auto` 支援水平滾動
- Info-item: `flex: 1` → `flex: 0 0 auto` 防止壓縮

#### 視覺優化

- 統一所有元素的 border-radius 為 2px
- 統一左側彩色邊框為 4px
- 統一結算日報告分頁字體樣式

### 修復 (Fixed)

#### 樣式問題

- 修復段落消失問題（字體太小導致內容合併）
- 修復「我最擔心的風險」區塊未套用 danger 樣式
- 修復已生成報告缺少 section-content CSS 定義
- 修復 AI 績效總覽使用舊版 grid 布局
- 修復手機版寬度不滿版問題

#### 響應式問題

- 修復 settlement-info 在手機版無法滾動
- 修復滾動條樣式不一致
- 修復 flex 項目被壓縮問題

### 移動 (Moved)

#### 維護工具腳本

從根目錄移至 `maintenance/scripts/`:

- `update_section_content.py`
- `add_section_content_css.py`
- `update_ai_performance_layout.py`
- `update_border_radius.py`

#### 開發記錄文檔

從根目錄移至 `maintenance/reports/`:

- `SETTLEMENT_REPORT_STYLE_FIX.md`
- `SECTION_CONTENT_ALL_REPORTS_UPDATE.md`
- `SECTION_CONTENT_CLASS_UPDATE.md`
- `SECTION_CONTENT_CSS_FIX.md`
- `SECTION_CONTENT_FONT_SIZE_ADJUSTMENT.md`
- `SECTION_CONTENT_MIGRATION_SUMMARY.md`
- `BORDER_RADIUS_UPDATE_REPORT.md`
- `SETTLEMENT_TABS_TYPOGRAPHY_UPDATE.md`

### 移除 (Removed)

無

### 安全性 (Security)

無

### 已棄用 (Deprecated)

#### 批量更新腳本

`maintenance/scripts/` 中的腳本已不應再使用：

- ⚠️ 這些腳本僅用於修復第一版開發過程中的歷史文件
- ⚠️ 未來的報告會自動使用正確的模板，無需手動修復
- ✅ 正確做法：修改 `templates/` 中的模板，重新執行生成腳本

---

## [未發布] - 開發中

### 計畫中 (Planned)

#### 版本 1.1.0

- [ ] 新增圖表互動功能
- [ ] 新增報告匯出 PDF 功能
- [ ] 新增歷史報告搜尋功能

#### 版本 1.2.0

- [ ] AI 預測模型優化
- [ ] 新增更多技術指標分析
- [ ] 自動化部署流程

#### 版本 2.0.0

- [ ] 建立 Web Dashboard
- [ ] 支援即時數據更新
- [ ] 使用者自訂設定功能

---

## 版本歷史

### [1.0.0] - 2026-01-13

第一版正式發布

---

## 變更類型說明

- **新增 (Added)**: 新功能
- **變更 (Changed)**: 既有功能的變更
- **移除 (Removed)**: 移除的功能
- **修復 (Fixed)**: 錯誤修正
- **安全性 (Security)**: 安全性相關的變更
- **已棄用 (Deprecated)**: 即將移除的功能
- **移動 (Moved)**: 檔案或目錄的移動

---

**維護者**: Shopping Liao  
**專案**: 台指選擇權分析系統  
**版本格式**: [主版本.次版本.修訂版本]
