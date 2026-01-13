# /daily-report - 生成每日報告

生成台指選擇權每日分析報告，更新首頁索引，並推送到 Git。

## 使用方式

```
/daily-report              # 生成今日報告（下載最新 PDF）
/daily-report 20260113     # 生成指定日期報告
/daily-report batch 20260110 20260111 20260112  # 批量生成多日報告
```

## 完整執行流程

### 單日報告
當用戶執行 `/daily-report` 或 `/daily-report YYYYMMDD` 時：

**步驟 1：生成報告**
```bash
# 有指定日期
python3 main.py --date {日期}

# 沒有指定日期（下載最新）
python3 main.py
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
git commit -m "feat: 新增 {日期} 每日報告"
git push
```

**步驟 5：回報結果**
- 告知報告位置：`docs/report_{日期}_{契約月份}.html`
- 告知首頁已更新
- 告知已推送到 Git

### 批量報告
當用戶執行 `/daily-report batch 日期1 日期2 ...` 時：

**步驟 1：批量生成報告**
```bash
python3 generate_batch_reports.py {日期1} {日期2} ...
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
git commit -m "feat: 批量新增每日報告 ({日期1}, {日期2}, ...)"
git push
```

**步驟 5：回報結果**
- 列出所有生成的報告
- 告知首頁已更新
- 告知已推送到 Git

## 參數說明

- `日期`: YYYYMMDD 格式，例如 20260113
- `batch`: 批量模式關鍵字，後接多個日期（空格分隔）

## 注意事項

- 需要對應日期的 PDF 檔案存在於 `data/pdf/` 目錄
- 如果 PDF 不存在，系統會自動嘗試從期交所下載
- 生成的報告會自動同步到 `docs/` 目錄
- 首頁 `index.html` 會自動更新報告連結
- 所有變更會自動提交並推送到 GitHub
