# /settlement-report - 生成結算日報告

生成台指選擇權結算日預測報告，更新首頁索引，並推送到 Git。

## 使用方式

```
/settlement-report wed 2026/01/15 20260113,20260114
/settlement-report fri 2026/01/17 20260115,20260116
```

格式：`/settlement-report {weekday} {結算日} {分析日期}`

## 參數說明

- `weekday`: 結算日是星期幾
  - `wed` 或 `wednesday`: 週三結算（週選）
  - `fri` 或 `friday`: 週五結算（月選）

- `結算日`: YYYY/MM/DD 格式，例如 2026/01/15

- `分析日期`: 用於分析的前兩日數據，逗號分隔
  - 格式：YYYYMMDD,YYYYMMDD
  - 例如：20260113,20260114

## 完整執行流程

**步驟 1：生成結算日報告**
```bash
python3 generate_settlement_report.py \
    --dates {分析日期} \
    --settlement {結算日} \
    --weekday {weekday}
```

**步驟 2：同步到 docs/**
```bash
python3 sync_to_docs.py
```

**步驟 3：更新首頁索引**
```bash
python3 generate_index_with_weekday.py
```

**步驟 4：提交並推送到 Git**
```bash
git add docs/
git commit -m "feat: 新增 {結算日} 結算日報告"
git push
```

**步驟 5：回報結果**
- 告知報告位置：`docs/settlement_{日期}_{weekday}.html`
- 告知首頁已更新
- 告知已推送到 Git

## 範例

### 週三結算（週選）
```
/settlement-report wed 2026/01/15 20260113,20260114
```
使用 1/13 和 1/14 的數據預測 1/15 的週三結算

執行命令：
```bash
python3 generate_settlement_report.py --dates 20260113,20260114 --settlement 2026/01/15 --weekday wednesday
```

### 週五結算（月選）
```
/settlement-report fri 2026/01/17 20260115,20260116
```
使用 1/15 和 1/16 的數據預測 1/17 的週五結算

執行命令：
```bash
python3 generate_settlement_report.py --dates 20260115,20260116 --settlement 2026/01/17 --weekday friday
```

## 注意事項

- 分析日期的 PDF 必須存在於 `data/pdf/` 目錄
- 結算日必須符合指定的星期（週三或週五）
- 報告包含：趨勢分析、情境預測、策略建議、風險評估
- 首頁 `index.html` 會自動更新報告連結
- 所有變更會自動提交並推送到 GitHub
