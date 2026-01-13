# 專案結構 - 台指選擇權分析工具# 專案結構總覽 - v1.0.0

## 📁 目錄結構## 📁 完整目錄結構

`````

taiex-options-analyzer/taiex-options-analyzer/

├── 📄 README.md                          # 專案說明文檔│

├── 📄 requirements.txt                   # Python 依賴套件├── 📊 核心程式

├── 📄 .gitignore                        # Git 忽略檔案設定│   ├── main.py                          # 單日報告生成主程式

││   ├── generate_batch_reports.py       # 批量生成單日報告

├── 🐍 main.py                           # 主程式：生成單日報告│   ├── generate_settlement_report.py   # 結算日報告生成器

├── 🐍 generate_batch_reports.py         # 批量生成單日報告│   ├── generate_settlement_review.py   # 結算日複盤報告

├── 🐍 generate_settlement_report.py     # 生成結算日預測報告│   ├── generate_settlement_predictions.py  # 結算預測生成器

├── 🐍 generate_settlement_predictions.py # 生成結算日預測數據│   ├── generate_index_with_weekday.py  # 首頁生成器

├── 🐍 generate_settlement_review.py     # 生成結算日回顧│   ├── process_all_predictions.py      # 批量處理預測

├── 🐍 generate_index_with_weekday.py    # 生成首頁索引│   └── requirements.txt                 # Python 依賴套件

├── 🐍 process_all_predictions.py        # 批次處理預測│

│├── 📝 原始碼 (src/)

├── 📂 src/                              # 核心原始碼│   ├── __init__.py

│   ├── __init__.py│   ├── analyzer.py                      # 選擇權分析邏輯

│   ├── fetcher.py                       # PDF 下載│   ├── fetcher.py                       # PDF 下載器

│   ├── parser.py                        # PDF 解析│   ├── parser.py                        # PDF 解析器

│   ├── analyzer.py                      # 數據分析│   └── reporter.py                      # HTML 報告生成器

│   └── reporter.py                      # 報告生成│

│├── 🎨 模板系統 (templates/)

├── 📂 templates/                        # Jinja2 模板│   ├── report.html                      # 單日報告模板 ✅

│   ├── report.html                      # 單日報告模板│   ├── settlement_report.html           # 結算日報告模板 ✅

│   ├── settlement_report.html           # 結算日報告模板│   ├── design_system.html               # 設計系統文檔

│   ├── settlement_review.html           # 結算日回顧模板│   └── components_preview.html          # 組件預覽

│   └── index.html                       # 首頁索引模板│

│├── 📄 生成報告 (reports/)

├── 📂 data/                             # 數據目錄│   ├── report_20260105_202601.html      # 單日報告

│   ├── pdf/                            # PDF 原始檔案│   ├── report_20260106_202601.html

│   │   └── 期貨選擇權盤後日報_YYYYMMDD.pdf│   ├── report_20260107_202601.html

│   ├── ai_learning/                    # AI 學習數據│   ├── report_20260108_202601.html

│   │   ├── analysis_records.json       # 分析記錄│   ├── report_20260109_202601.html

│   │   └── learned_insights.json       # 學習洞見│   ├── settlement_20260107_wed.html     # 週三結算報告 ✅

│   └── settlement_predictions/         # 結算預測數據│   ├── settlement_20260109_fri.html     # 週五結算報告 ✅

│       └── YYYYMMDD_settlement.json│   └── settlement_20260110_fri.html     # 週五結算報告 ✅

││

├── 📂 reports/                          # 生成的 HTML 報告├── 🌐 公開頁面 (docs/)

│   ├── report_YYYYMMDD_契約.html        # 單日報告│   ├── index.html                       # 報告總覽首頁

│   ├── settlement_YYYYMMDD_wed.html    # 週三結算報告│   ├── report_*.html                    # 單日報告（公開版）

│   └── settlement_YYYYMMDD_fri.html    # 週五結算報告│   ├── settlement_*.html                # 結算報告（公開版）

││   └── rwd_demo.html                    # RWD 示範頁面

├── 📂 docs/                             # GitHub Pages 部署目錄│

│   └── (同 reports/ 結構)├── 📦 資料來源 (data/)

││   └── pdf/

├── 📂 documentation/                    # 📚 文檔中心│       └── 期貨選擇權盤後日報_*.pdf      # 原始 PDF 文件

│   ├── README.md                        # 文檔索引│

│   ├── CHANGELOG.md                     # 變更日誌├── 🔧 維護工具 (maintenance/)

│   ││   ├── README.md                        # 維護工具說明文檔

│   ├── 📂 guides/                       # 使用指南│   ├── scripts/                         # 一次性更新腳本（已不使用）

│   │   ├── DEPLOYMENT.md                # 部署指南│   │   ├── update_section_content.py

│   │   ├── QUICK_ACCESS.md              # 快速訪問│   │   ├── add_section_content_css.py

│   │   ├── NAVIGATION.md                # 導航說明│   │   ├── update_ai_performance_layout.py

│   │   ├── PROJECT_STRUCTURE.md         # 專案結構（本文件）│   │   └── update_border_radius.py

│   │   ├── PHASE1_COMPLETE.md           # 第一階段完成│   └── reports/                         # 歷史更新記錄

│   │   ├── PHASE2_PROGRESS.md           # 第二階段進度│       ├── SETTLEMENT_REPORT_STYLE_FIX.md

│   │   ├── REPORTS_REGENERATION_SUMMARY.md  # 報告重生摘要│       ├── SECTION_CONTENT_ALL_REPORTS_UPDATE.md

│   │   └── UPGRADE_TWSE_API_INTEGRATION.md  # TWSE API 升級│       ├── SECTION_CONTENT_CLASS_UPDATE.md

│   ││       ├── SECTION_CONTENT_CSS_FIX.md

│   ├── 📂 design/                       # 設計系統│       ├── SECTION_CONTENT_FONT_SIZE_ADJUSTMENT.md

│   │   ├── DESIGN_GUIDELINE.md          # 設計指南│       ├── SECTION_CONTENT_MIGRATION_SUMMARY.md

│   │   ├── DESIGN_MIGRATION_GUIDE.md    # 設計遷移指南│       ├── BORDER_RADIUS_UPDATE_REPORT.md

│   │   ├── DESIGN_QUICK_REFERENCE.md    # 設計快速參考│       └── SETTLEMENT_TABS_TYPOGRAPHY_UPDATE.md

│   │   ├── DESIGN_SYSTEM_FILES.txt      # 設計系統文件列表│

│   │   ├── DESIGN_SYSTEM_README.md      # 設計系統說明└── 📚 專案文檔

│   │   └── DESIGN_SYSTEM_SUMMARY.md     # 設計系統摘要    ├── README.md                        # 專案說明（主文檔）✨

│   │    ├── VERSION_HISTORY.md               # 版本歷史與未來規劃 ✨

│   ├── 📂 issues/                       # 問題修復記錄    ├── RELEASE_v1.0.0.md               # v1.0.0 發布說明 ✨

│   │   ├── BUGFIX_SETTLEMENT_DATE_VALIDATION.md    ├── PROJECT_STRUCTURE.md            # 本文件 ✨

│   │   ├── FIX_SETTLEMENT_ANALYSIS.md    │

│   │   ├── ISSUE_CONTRACT_TYPE_PARSING.md    ├── 🎨 設計系統文檔

│   │   └── ISSUE_PDF_PARSING_20260112.md    │   ├── DESIGN_SYSTEM_README.md      # 設計系統完整說明

│   │    │   ├── DESIGN_GUIDELINE.md          # 設計指南

│   ├── 📂 releases/                     # 版本發布    │   ├── DESIGN_QUICK_REFERENCE.md    # 快速參考

│   │   ├── RELEASE_v1.0.0.md            # v1.0.0 發布說明    │   ├── DESIGN_MIGRATION_GUIDE.md    # 遷移指南

│   │   ├── V1.0.0_RELEASE_SUMMARY.md    # 發布摘要    │   └── DESIGN_SYSTEM_SUMMARY.md     # 設計系統總結

│   │   └── VERSION_HISTORY.md           # 版本歷史    │

│   │    ├── 📊 報告系統文檔

│   └── 📂 features/                     # 功能開發文檔    │   ├── SETTLEMENT_REPORT_SYSTEM.md  # 結算報告系統說明

│       ├── AI_ANALYSIS_TAB.md           # AI 分析標籤    │   ├── SETTLEMENT_QUICK_START.md    # 結算報告快速開始

│       ├── AI_PREDICTION_SYSTEM_REPORT.md  # AI 預測系統    │   ├── AI_ANALYSIS_TAB.md          # AI 分析分頁說明

│       ├── AI_TRADER_STRATEGY_UPDATE.md    # AI 交易策略    │   ├── AI_PREDICTION_SYSTEM_REPORT.md  # AI 預測系統報告

│       ├── WEEKDAY_FEATURE.md           # 星期功能    │   └── HOMEPAGE_REPORT_CATEGORIES.md   # 首頁分類說明

│       ├── SETTLEMENT_QUICK_START.md    # 結算快速入門    │

│       ├── SETTLEMENT_REPORT_SYSTEM.md  # 結算報告系統    ├── 🎯 功能文檔

│       ├── MOBILE_PADDING_OPTIMIZATION.md  # 手機版優化    │   ├── WEEKDAY_FEATURE.md          # 星期顯示功能

│       ├── PRICE_CHART_RWD.md           # 價格圖表 RWD    │   ├── NAVIGATION.md               # 導航系統

│       ├── RWD_SETTLEMENT_SCENARIOS.md  # RWD 結算場景    │   ├── QUICK_ACCESS.md             # 快速訪問

│       └── HOMEPAGE_REPORT_CATEGORIES.md   # 首頁報告分類    │   └── FIX_SETTLEMENT_ANALYSIS.md  # 結算分析修復

│    │

├── 📂 maintenance/                      # 維護工具（第一版開發歷史）    ├── 📱 響應式設計文檔

│   ├── README.md                        # 維護工具說明    │   ├── PRICE_CHART_RWD.md          # 價格圖表 RWD

│   └── (舊版開發腳本)    │   ├── MOBILE_PADDING_OPTIMIZATION.md  # 手機版內距優化

│    │   └── RWD_SETTLEMENT_SCENARIOS.md     # 結算情境 RWD

└── 📂 .github/                          # GitHub 設定    │

    └── workflows/                       # GitHub Actions    ├── 🚀 部署相關

        └── deploy.yml                   # 自動部署設定    │   ├── DEPLOYMENT.md               # 部署指南

```    │   ├── PHASE1_COMPLETE.md          # Phase 1 完成記錄

    │   └── PHASE2_PROGRESS.md          # Phase 2 進度記錄

## 🎯 核心模組說明    │

    └── 🔍 其他

### 📄 主程式        └── DESIGN_SYSTEM_FILES.txt     # 設計系統文件清單

```

- **main.py**: 單日報告生成主程式

  - 下載 PDF## 📊 檔案分類統計

  - 解析數據

  - 生成 HTML 報告### 核心程式碼



- **generate_settlement_report.py**: 結算日報告生成- Python 檔案: 12 個

  - 讀取單日報告數據- 核心模組: 4 個（src/）

  - AI 智能分析

  - 生成雙頁籤結算報告### 模板系統



### 📦 src/ 核心模組- HTML 模板: 4 個

- ✅ 已優化完成，包含所有樣式定義

- **fetcher.py**: PDF 下載器

  - 從期交所下載盤後日報### 生成報告

  - 快取機制避免重複下載

- 單日報告: 5 個（2026/01/05-09）

- **parser.py**: PDF 解析器- 結算報告: 3 個（週三、週五）

  - 提取選擇權 OI 數據- ✅ 所有報告使用統一樣式

  - 識別契約類型（週選/月選）

  - 整合台指期貨價格數據### 文檔系統



- **analyzer.py**: 數據分析器- 總文檔數: 30+ 個

  - 計算 Max Pain- 核心文檔: 5 個（✨ 標記）

  - 計算 P/C Ratio- 設計系統: 5 個

  - 生成 OI 分布統計- 報告系統: 5 個

- 功能說明: 4 個

- **reporter.py**: 報告生成器- 響應式: 3 個

  - 使用 Jinja2 模板- 維護記錄: 8 個（已移至 maintenance/）

  - 生成單日/結算報告 HTML

  - 支援多契約報告## 🎯 關鍵檔案說明



### 🎨 templates/ 模板### 必讀文檔（依優先順序）



- **report.html**: 單日報告模板1. **README.md** - 從這裡開始！

  - 支援多契約顯示（週三/週五/近月）

  - RWD 響應式設計   - 專案概述

  - 亞洲市場風格（紅漲綠跌）   - 快速開始指南

   - 功能特色說明

- **settlement_report.html**: 結算日報告模板

  - 雙頁籤設計（技術分析/AI 分析）2. **VERSION_HISTORY.md** - 版本演進

  - 趨勢訊號卡片

  - 劇本情境分析   - 開發歷程

   - 版本更新記錄

- **index.html**: 首頁索引模板   - 未來規劃

  - 報告分類展示

  - 日期/星期資訊3. **DESIGN_SYSTEM_README.md** - 設計規範

  - 快速導航連結

   - Section-content 系統

## 📂 數據流程   - 主題變體使用

   - 響應式設計

```

1. 下載 PDF4. **SETTLEMENT_REPORT_SYSTEM.md** - 結算報告

   fetcher.py → data/pdf/

   - 四大分頁說明

2. 解析數據   - 預測邏輯

   parser.py → 提取 OI 數據 + 台指價格   - 使用指南



3. 數據分析5. **maintenance/README.md** - 維護須知

   analyzer.py → Max Pain, P/C Ratio, 統計   - 歷史工具說明

   - 為什麼不應再執行這些腳本

4. 生成報告   - 正確的更新方式

   reporter.py + templates/ → HTML 報告

### 模板檔案（未來修改樣式時使用）

5. 部署

   reports/ → docs/ → GitHub Pages1. **templates/report.html**

```

   - 單日報告的 HTML 模板

## 🔧 配置文件   - 包含所有 CSS 定義

   - 修改後重新執行 `main.py`

- **requirements.txt**: Python 依賴

  ```2. **templates/settlement_report.html**

  PyMuPDF>=1.23.0

  Jinja2>=3.1.0   - 結算日報告的 HTML 模板

  requests>=2.31.0   - 包含四個分頁的完整樣式

  beautifulsoup4>=4.12.0   - 修改後重新執行 `generate_settlement_report.py`

  lxml>=5.0.0

  ```3. **templates/design_system.html**

   - 設計系統文檔和組件展示

- **.gitignore**: 忽略檔案設定   - 可視化預覽所有樣式

  - Python 快取 (`__pycache__/`, `*.pyc`)

  - 系統檔案 (`.DS_Store`)## 🔄 工作流程

  - IDE 設定 (`.vscode/`, `.idea/`)

### 每日報告生成流程

## 📚 文檔組織

```

所有專案文檔已整理至 `documentation/` 目錄：1. PDF 下載

   ↓

- **guides/**: 使用指南與操作文檔2. 解析 PDF 數據

- **design/**: 設計系統與 UI/UX 規範   ↓

- **issues/**: 問題修復與 Bug 追蹤3. 計算分析指標

- **releases/**: 版本發布與更新日誌   ↓

- **features/**: 功能開發文檔4. 套用 templates/report.html

   ↓

詳見 [documentation/README.md](../README.md)5. 生成 reports/report_*.html

   ↓

## 🚀 開發工作流6. 複製到 docs/ 供 GitHub Pages 使用

```

1. **修改程式碼**: 編輯 `src/` 中的模組

2. **更新模板**: 修改 `templates/` 中的 HTML### 結算日報告生成流程

3. **測試生成**: 運行 `main.py` 測試報告

4. **批量生成**: 使用 `generate_batch_reports.py````

5. **提交代碼**: Git commit & push1. 讀取已生成的單日報告

6. **自動部署**: GitHub Actions 自動部署到 Pages   ↓

2. 分析多日數據趨勢

## 📊 報告類型   ↓

3. AI 預測結算區間

### 單日報告   ↓

- 檔名: `report_YYYYMMDD_契約代號.html`4. 套用 templates/settlement_report.html

- 內容: OI 分布、Max Pain、P/C Ratio   ↓

- 支援: 週三/週五/近月選擇權多契約顯示5. 生成 reports/settlement_*.html

   ↓

### 結算日報告6. 複製到 docs/

- 檔名: `settlement_YYYYMMDD_wed/fri.html````

- 內容: 技術分析 + AI 智能分析

- 功能: 趨勢預測、劇本分析、交易策略### 首頁更新流程



### 結算回顧```

- 檔名: `settlement_review_YYYYMMDD_wed/fri.html`1. 掃描 docs/ 中的所有報告

- 內容: 預測準確度分析   ↓

- 功能: AI 學習反饋機制2. 按日期分組（單日、週三、週五）

   ↓

## 🎯 最佳實踐3. 添加星期標記

   ↓

1. **模組化開發**: 功能分離到不同模組4. 生成 docs/index.html

2. **模板化設計**: HTML 使用 Jinja2 模板```

3. **數據驅動**: 所有分析基於數據計算

4. **文檔完整**: 保持 documentation/ 目錄更新## 📝 未來新增報告時

5. **版本控制**: 重要更新記錄在 CHANGELOG.md

### 單日報告

## 🔗 相關連結

```bash

- [專案首頁](https://shoppingliao.github.io/taiex-options-analyzer/)# 1. 如需新日期，先在 src/parser.py 添加台指資料

- [GitHub Repository](https://github.com/ShoppingLiao/taiex-options-analyzer)tx_data_map['20260113'] = {

- [完整文檔中心](../README.md)    'open': 30500,

- [版本歷史](../releases/VERSION_HISTORY.md)    'high': 30600,

    'low': 30400,

---    'close': 30550,

    'volume': 115000,

**最後更新**: 2026-01-13      'settlement': 30550,

**文檔版本**: 2.0 (架構重組後)}


# 2. 將 PDF 放入 data/pdf/

# 3. 生成報告
python3 main.py --date 20260113

# 4. 更新首頁
python3 generate_index_with_weekday.py
```

### 結算日報告

```bash
# 週三結算（使用週一、週二數據）
python3 generate_settlement_report.py wed

# 週五結算（使用週三、週四數據）
python3 generate_settlement_report.py fri

# 更新首頁
python3 generate_index_with_weekday.py
```

## ⚠️ 重要提醒

### ✅ 正確做法

1. 修改 `templates/` 中的模板
2. 重新執行生成腳本
3. 新報告自動使用更新後的樣式

### ❌ 錯誤做法

1. ~~執行 `maintenance/scripts/` 中的腳本~~
2. ~~手動修改已生成的 HTML 報告~~
3. ~~複製舊報告並修改內容~~

## 🎉 第一版完成標誌

- ✅ 所有模板已優化
- ✅ 設計系統已穩定
- ✅ 文檔系統完整
- ✅ 維護工具已整理
- ✅ 版本歷史已建立
- ✅ 推送到 GitHub

---

**專案版本**: 1.0.0
**最後更新**: 2026-01-13
**維護者**: Shopping Liao

📚 完整文檔請參見各文檔檔案
`````
