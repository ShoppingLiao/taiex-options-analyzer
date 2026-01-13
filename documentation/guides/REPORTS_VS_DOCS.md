# reports/ vs docs/ 資料夾差異說明

## 📊 概述

專案中有兩個存放 HTML 報告的資料夾：`reports/` 和 `docs/`，它們有不同的用途和生命週期。

## 📁 資料夾對比

| 項目         | reports/                | docs/                               |
| ------------ | ----------------------- | ----------------------------------- |
| **用途**     | 本地開發與測試          | GitHub Pages 部署                   |
| **更新方式** | Python 腳本直接生成     | 手動複製或 CI/CD 部署               |
| **內容同步** | ❌ 不會自動同步到 docs/ | ❌ 不會自動同步到 reports/          |
| **檔案狀態** | 最新版本                | 可能較舊                            |
| **額外檔案** | 無                      | index.html, rwd_demo.html, .md 文檔 |
| **Git 追蹤** | ✅ 是                   | ✅ 是                               |
| **線上訪問** | ❌ 否                   | ✅ 是 (GitHub Pages)                |

## 🔍 詳細分析

### 📂 reports/ - 本地開發目錄

**目的**:

- 本地生成和測試報告
- 開發時的主要工作目錄
- Python 腳本的預設輸出位置

**特點**:

```python
# main.py 預設輸出到 reports/
reporter = ReportGenerator(
    output_dir=project_root / "reports"
)
```

**內容** (2026-01-13 11:05 最新):

```
reports/
├── report_20260105_202601.html      # 單日報告
├── report_20260105_202601W1.html
├── report_20260106_202601.html
├── report_20260106_202601W1.html
├── report_20260107_202601.html
├── report_20260108_202501.html
├── report_20260108_202601.html
├── report_20260109_202601.html
├── report_20260112_202601W2.html
├── settlement_20260107_wed.html     # 結算日報告
├── settlement_20260109_fri.html
└── summary_20260112.html            # 摘要報告
```

**更新時機**:

- 執行 `main.py` 時
- 執行 `generate_batch_reports.py` 時
- 執行 `generate_settlement_report.py` 時
- 執行 `generate_settlement_predictions.py` 時

### 📂 docs/ - GitHub Pages 部署目錄

**目的**:

- 透過 GitHub Pages 提供線上訪問
- 公開展示專案成果
- 提供永久性的報告連結

**特點**:

```yaml
# .github/workflows/deploy.yml
- name: Upload artifact
  uses: actions/upload-pages-artifact@v3
  with:
    path: "./docs" # 部署 docs/ 目錄
```

**內容** (2026-01-13 09:03 較舊):

```
docs/
├── index.html                       # 📌 首頁索引 (reports/ 沒有)
├── report_20260105_202601.html      # 單日報告
├── report_20260105_202601W1.html
├── report_20260106_202601.html
├── report_20260106_202601W1.html
├── report_20260107_202601.html
├── report_20260108_202501.html
├── report_20260108_202601.html
├── report_20260109_202601.html      # ⚠️ 較舊版本 (09:03)
├── report_20260109_old.html         # 📌 舊版備份 (reports/ 沒有)
├── report_20260112_202601W2.html
├── rwd_demo.html                    # 📌 RWD 示範頁 (reports/ 沒有)
├── settlement_20260107_wed.html
├── settlement_20260109_fri.html
├── summary_20260112.html
├── AI_LEARNING_SYSTEM.md            # 📌 文檔 (reports/ 沒有)
└── SETTLEMENT_TRADER_VIEW.md        # 📌 文檔 (reports/ 沒有)
```

**線上訪問**:

- 首頁: https://shoppingliao.github.io/taiex-options-analyzer/
- 單日報告: https://shoppingliao.github.io/taiex-options-analyzer/report_20260109_202601.html

## ⚠️ 發現的問題

### 1. **內容不同步**

檢測結果:

```bash
# 檔案大小不同
reports/report_20260109_202601.html  233K  (11:05 最新)
docs/report_20260109_202601.html     229K  (09:03 較舊)

# MD5 雜湊值不同
reports: 102418e96f0ec27537114f0ef9aeb9e
docs:    65366ee0c74630c8b449cfdf7a21f937
```

**原因**:

- `reports/` 在 11:05 重新生成（多契約 OI 分布表格更新後）
- `docs/` 停留在 09:03 的舊版本
- 沒有自動同步機制

### 2. **手動複製風險**

目前的工作流程:

```bash
# 1. 生成報告到 reports/
python main.py --date 20260109 --output reports

# 2. 需要手動複製到 docs/
cp reports/report_*.html docs/

# 3. Git commit & push
git add docs/
git commit -m "Update reports"
git push
```

**風險**:

- ❌ 容易忘記複製
- ❌ 可能複製錯檔案
- ❌ 版本不一致

### 3. **docs/ 獨有檔案**

這些檔案只存在於 `docs/`:

- `index.html` - 首頁索引
- `rwd_demo.html` - RWD 示範
- `report_20260109_old.html` - 舊版備份
- `AI_LEARNING_SYSTEM.md` - 文檔
- `SETTLEMENT_TRADER_VIEW.md` - 文檔

**問題**: 這些檔案的來源和用途不明確

## 🎯 建議改進方案

### 方案 A: 統一輸出到 docs/

**優點**:

- ✅ 消除雙重目錄
- ✅ 自動保持同步
- ✅ 生成即部署

**實作**:

```python
# 修改 main.py
reporter = ReportGenerator(
    output_dir=project_root / "docs"  # 直接輸出到 docs/
)
```

**缺點**:

- ❌ 開發測試時會污染部署目錄
- ❌ Git 歷史會有大量測試檔案

### 方案 B: 增加同步腳本

**優點**:

- ✅ 保持 reports/ 作為開發目錄
- ✅ 明確的同步流程
- ✅ 可選擇性複製

**實作**:

```python
# sync_to_docs.py
import shutil
from pathlib import Path

def sync_reports():
    """同步 reports/ 到 docs/"""
    reports_dir = Path('reports')
    docs_dir = Path('docs')

    # 只複製 HTML 報告
    for html_file in reports_dir.glob('*.html'):
        shutil.copy2(html_file, docs_dir / html_file.name)
        print(f"✅ 已同步: {html_file.name}")

if __name__ == "__main__":
    sync_reports()
```

使用:

```bash
# 1. 生成報告
python main.py --date 20260109

# 2. 同步到 docs
python sync_to_docs.py

# 3. 提交
git add docs/
git commit -m "sync: 更新報告到 docs/"
git push
```

### 方案 C: GitHub Actions 自動同步

**優點**:

- ✅ 全自動化
- ✅ 推送即部署
- ✅ 減少人為錯誤

**實作**:

```yaml
# .github/workflows/sync-reports.yml
name: Sync Reports to Docs

on:
  push:
    paths:
      - "reports/*.html"

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Sync reports to docs
        run: |
          cp -r reports/*.html docs/

      - name: Commit changes
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add docs/
          git commit -m "auto: 同步 reports 到 docs" || exit 0
          git push
```

## 📋 目前狀態檢查清單

- [x] `reports/` 存在並包含最新報告
- [x] `docs/` 存在並可透過 GitHub Pages 訪問
- [ ] `reports/` 和 `docs/` 內容同步 ⚠️ **不同步**
- [x] GitHub Pages 正常運作
- [ ] 有明確的同步機制 ⚠️ **缺少**
- [ ] docs/ 獨有檔案有文檔說明 ⚠️ **缺少**

## 🔧 立即行動建議

### 1. 同步現有報告

```bash
# 將 reports/ 的最新報告同步到 docs/
cd /Users/shopping.liao/Documents/code/taiex-options-analyzer
cp -v reports/*.html docs/

# 檢查差異
ls -lh reports/*.html docs/*.html | grep "Jan 13"

# 提交更新
git add docs/
git commit -m "sync: 更新所有報告到 docs/ (含多契約 OI 分布表格)"
git push
```

### 2. 建立同步腳本

創建 `sync_to_docs.py` 腳本（方案 B）

### 3. 清理 docs/ 獨有檔案

- 移動 `.md` 文檔到 `documentation/` 目錄
- 為 `rwd_demo.html` 和 `report_20260109_old.html` 添加說明
- 確保 `index.html` 有正確的生成腳本

## 🎓 最佳實踐建議

1. **明確職責**:

   - `reports/` = 開發測試
   - `docs/` = 生產部署

2. **自動化同步**:

   - 使用腳本或 CI/CD
   - 減少手動操作

3. **版本控制**:

   - 提交時註明是否已同步
   - Commit message 格式: `sync: 描述`

4. **文檔記錄**:
   - 在 README 說明兩個目錄的用途
   - 提供同步指令說明

---

**建立日期**: 2026-01-13  
**最後檢查**: 2026-01-13 11:30  
**狀態**: ⚠️ 需要同步
