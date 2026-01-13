# /settlement-report - 生成結算日報告

生成台指選擇權結算日預測報告。

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

## 執行流程

1. 解析用戶輸入的參數

2. 執行結算日報告生成：
   ```bash
   python3 generate_settlement_report.py \
       --dates {分析日期} \
       --settlement {結算日} \
       --weekday {weekday}
   ```

3. 報告生成後，執行同步：
   ```bash
   python3 sync_to_docs.py
   ```

4. 告知用戶報告位置：`docs/settlement_{日期}_{weekday}.html`

## 範例

### 週三結算（週選）
```
/settlement-report wed 2026/01/15 20260113,20260114
```
使用 1/13 和 1/14 的數據預測 1/15 的週三結算

### 週五結算（月選）
```
/settlement-report fri 2026/01/17 20260115,20260116
```
使用 1/15 和 1/16 的數據預測 1/17 的週五結算

## 注意事項

- 分析日期的 PDF 必須存在於 `data/pdf/` 目錄
- 結算日必須符合指定的星期（週三或週五）
- 報告包含：趨勢分析、情境預測、策略建議、風險評估
