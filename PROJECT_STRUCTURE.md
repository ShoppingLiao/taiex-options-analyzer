# 專案結構總覽 - v1.0.0

## 📁 完整目錄結構

```
taiex-options-analyzer/
│
├── 📊 核心程式
│   ├── main.py                          # 單日報告生成主程式
│   ├── generate_batch_reports.py       # 批量生成單日報告
│   ├── generate_settlement_report.py   # 結算日報告生成器
│   ├── generate_settlement_review.py   # 結算日複盤報告
│   ├── generate_settlement_predictions.py  # 結算預測生成器
│   ├── generate_index_with_weekday.py  # 首頁生成器
│   ├── process_all_predictions.py      # 批量處理預測
│   └── requirements.txt                 # Python 依賴套件
│
├── 📝 原始碼 (src/)
│   ├── __init__.py
│   ├── analyzer.py                      # 選擇權分析邏輯
│   ├── fetcher.py                       # PDF 下載器
│   ├── parser.py                        # PDF 解析器
│   └── reporter.py                      # HTML 報告生成器
│
├── 🎨 模板系統 (templates/)
│   ├── report.html                      # 單日報告模板 ✅
│   ├── settlement_report.html           # 結算日報告模板 ✅
│   ├── design_system.html               # 設計系統文檔
│   └── components_preview.html          # 組件預覽
│
├── 📄 生成報告 (reports/)
│   ├── report_20260105_202601.html      # 單日報告
│   ├── report_20260106_202601.html
│   ├── report_20260107_202601.html
│   ├── report_20260108_202601.html
│   ├── report_20260109_202601.html
│   ├── settlement_20260107_wed.html     # 週三結算報告 ✅
│   ├── settlement_20260109_fri.html     # 週五結算報告 ✅
│   └── settlement_20260110_fri.html     # 週五結算報告 ✅
│
├── 🌐 公開頁面 (docs/)
│   ├── index.html                       # 報告總覽首頁
│   ├── report_*.html                    # 單日報告（公開版）
│   ├── settlement_*.html                # 結算報告（公開版）
│   └── rwd_demo.html                    # RWD 示範頁面
│
├── 📦 資料來源 (data/)
│   └── pdf/
│       └── 期貨選擇權盤後日報_*.pdf      # 原始 PDF 文件
│
├── 🔧 維護工具 (maintenance/)
│   ├── README.md                        # 維護工具說明文檔
│   ├── scripts/                         # 一次性更新腳本（已不使用）
│   │   ├── update_section_content.py
│   │   ├── add_section_content_css.py
│   │   ├── update_ai_performance_layout.py
│   │   └── update_border_radius.py
│   └── reports/                         # 歷史更新記錄
│       ├── SETTLEMENT_REPORT_STYLE_FIX.md
│       ├── SECTION_CONTENT_ALL_REPORTS_UPDATE.md
│       ├── SECTION_CONTENT_CLASS_UPDATE.md
│       ├── SECTION_CONTENT_CSS_FIX.md
│       ├── SECTION_CONTENT_FONT_SIZE_ADJUSTMENT.md
│       ├── SECTION_CONTENT_MIGRATION_SUMMARY.md
│       ├── BORDER_RADIUS_UPDATE_REPORT.md
│       └── SETTLEMENT_TABS_TYPOGRAPHY_UPDATE.md
│
└── 📚 專案文檔
    ├── README.md                        # 專案說明（主文檔）✨
    ├── VERSION_HISTORY.md               # 版本歷史與未來規劃 ✨
    ├── RELEASE_v1.0.0.md               # v1.0.0 發布說明 ✨
    ├── PROJECT_STRUCTURE.md            # 本文件 ✨
    │
    ├── 🎨 設計系統文檔
    │   ├── DESIGN_SYSTEM_README.md      # 設計系統完整說明
    │   ├── DESIGN_GUIDELINE.md          # 設計指南
    │   ├── DESIGN_QUICK_REFERENCE.md    # 快速參考
    │   ├── DESIGN_MIGRATION_GUIDE.md    # 遷移指南
    │   └── DESIGN_SYSTEM_SUMMARY.md     # 設計系統總結
    │
    ├── 📊 報告系統文檔
    │   ├── SETTLEMENT_REPORT_SYSTEM.md  # 結算報告系統說明
    │   ├── SETTLEMENT_QUICK_START.md    # 結算報告快速開始
    │   ├── AI_ANALYSIS_TAB.md          # AI 分析分頁說明
    │   ├── AI_PREDICTION_SYSTEM_REPORT.md  # AI 預測系統報告
    │   └── HOMEPAGE_REPORT_CATEGORIES.md   # 首頁分類說明
    │
    ├── 🎯 功能文檔
    │   ├── WEEKDAY_FEATURE.md          # 星期顯示功能
    │   ├── NAVIGATION.md               # 導航系統
    │   ├── QUICK_ACCESS.md             # 快速訪問
    │   └── FIX_SETTLEMENT_ANALYSIS.md  # 結算分析修復
    │
    ├── 📱 響應式設計文檔
    │   ├── PRICE_CHART_RWD.md          # 價格圖表 RWD
    │   ├── MOBILE_PADDING_OPTIMIZATION.md  # 手機版內距優化
    │   └── RWD_SETTLEMENT_SCENARIOS.md     # 結算情境 RWD
    │
    ├── 🚀 部署相關
    │   ├── DEPLOYMENT.md               # 部署指南
    │   ├── PHASE1_COMPLETE.md          # Phase 1 完成記錄
    │   └── PHASE2_PROGRESS.md          # Phase 2 進度記錄
    │
    └── 🔍 其他
        └── DESIGN_SYSTEM_FILES.txt     # 設計系統文件清單
```

## 📊 檔案分類統計

### 核心程式碼

- Python 檔案: 12 個
- 核心模組: 4 個（src/）

### 模板系統

- HTML 模板: 4 個
- ✅ 已優化完成，包含所有樣式定義

### 生成報告

- 單日報告: 5 個（2026/01/05-09）
- 結算報告: 3 個（週三、週五）
- ✅ 所有報告使用統一樣式

### 文檔系統

- 總文檔數: 30+ 個
- 核心文檔: 5 個（✨ 標記）
- 設計系統: 5 個
- 報告系統: 5 個
- 功能說明: 4 個
- 響應式: 3 個
- 維護記錄: 8 個（已移至 maintenance/）

## 🎯 關鍵檔案說明

### 必讀文檔（依優先順序）

1. **README.md** - 從這裡開始！

   - 專案概述
   - 快速開始指南
   - 功能特色說明

2. **VERSION_HISTORY.md** - 版本演進

   - 開發歷程
   - 版本更新記錄
   - 未來規劃

3. **DESIGN_SYSTEM_README.md** - 設計規範

   - Section-content 系統
   - 主題變體使用
   - 響應式設計

4. **SETTLEMENT_REPORT_SYSTEM.md** - 結算報告

   - 四大分頁說明
   - 預測邏輯
   - 使用指南

5. **maintenance/README.md** - 維護須知
   - 歷史工具說明
   - 為什麼不應再執行這些腳本
   - 正確的更新方式

### 模板檔案（未來修改樣式時使用）

1. **templates/report.html**

   - 單日報告的 HTML 模板
   - 包含所有 CSS 定義
   - 修改後重新執行 `main.py`

2. **templates/settlement_report.html**

   - 結算日報告的 HTML 模板
   - 包含四個分頁的完整樣式
   - 修改後重新執行 `generate_settlement_report.py`

3. **templates/design_system.html**
   - 設計系統文檔和組件展示
   - 可視化預覽所有樣式

## 🔄 工作流程

### 每日報告生成流程

```
1. PDF 下載
   ↓
2. 解析 PDF 數據
   ↓
3. 計算分析指標
   ↓
4. 套用 templates/report.html
   ↓
5. 生成 reports/report_*.html
   ↓
6. 複製到 docs/ 供 GitHub Pages 使用
```

### 結算日報告生成流程

```
1. 讀取已生成的單日報告
   ↓
2. 分析多日數據趨勢
   ↓
3. AI 預測結算區間
   ↓
4. 套用 templates/settlement_report.html
   ↓
5. 生成 reports/settlement_*.html
   ↓
6. 複製到 docs/
```

### 首頁更新流程

```
1. 掃描 docs/ 中的所有報告
   ↓
2. 按日期分組（單日、週三、週五）
   ↓
3. 添加星期標記
   ↓
4. 生成 docs/index.html
```

## 📝 未來新增報告時

### 單日報告

```bash
# 1. 如需新日期，先在 src/parser.py 添加台指資料
tx_data_map['20260113'] = {
    'open': 30500,
    'high': 30600,
    'low': 30400,
    'close': 30550,
    'volume': 115000,
    'settlement': 30550,
}

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
