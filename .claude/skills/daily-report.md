# /daily-report - 生成每日報告

生成台指選擇權每日分析報告。

## 使用方式

```
/daily-report              # 生成今日報告（下載最新 PDF）
/daily-report 20260113     # 生成指定日期報告
/daily-report batch 20260110 20260111 20260112  # 批量生成多日報告
```

## 執行流程

### 單日報告
當用戶執行 `/daily-report` 或 `/daily-report YYYYMMDD` 時：

1. 如果有指定日期，執行：
   ```bash
   python3 main.py --date {日期}
   ```

2. 如果沒有指定日期，執行：
   ```bash
   python3 main.py
   ```

3. 報告生成後，執行同步：
   ```bash
   python3 sync_to_docs.py
   ```

4. 告知用戶報告位置：`docs/report_{日期}_{契約月份}.html`

### 批量報告
當用戶執行 `/daily-report batch 日期1 日期2 ...` 時：

1. 執行批量生成：
   ```bash
   python3 generate_batch_reports.py {日期1} {日期2} ...
   ```

2. 報告生成後，執行同步：
   ```bash
   python3 sync_to_docs.py
   ```

3. 列出所有生成的報告檔案

## 參數說明

- `日期`: YYYYMMDD 格式，例如 20260113
- `batch`: 批量模式關鍵字，後接多個日期

## 注意事項

- 需要對應日期的 PDF 檔案存在於 `data/pdf/` 目錄
- 如果 PDF 不存在，系統會自動嘗試從期交所下載
- 生成的報告會自動同步到 `docs/` 目錄供 GitHub Pages 使用
