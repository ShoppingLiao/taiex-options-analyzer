# 每日自動化工作流設定指南

## 快速開始

### 手動執行

```bash
# 執行今日工作流
python3 daily_workflow.py

# 執行指定日期
python3 daily_workflow.py --date 20260115

# 跳過 Git 推送（本地測試用）
python3 daily_workflow.py --skip-git

# 強制重新下載 PDF
python3 daily_workflow.py --force
```

### 查看記錄

```bash
# 查看最近 50 行日誌
python3 daily_workflow.py --logs

# 查看最近 100 行日誌
python3 daily_workflow.py --logs --logs-lines 100

# 查看執行歷史
python3 daily_workflow.py --history

# 查看最近一次執行詳情
python3 daily_workflow.py --detail

# 查看倒數第二次執行詳情
python3 daily_workflow.py --detail -2
```

## 自動排程設定 (Cron)

### macOS / Linux

1. 開啟 crontab 編輯器：
```bash
crontab -e
```

2. 添加以下排程（每日下午 3:30 執行）：
```cron
# 台指選擇權每日報告 - 每日 15:30 執行
30 15 * * 1-5 cd /Users/shopping.liao/Documents/code/taiex-options-analyzer && /usr/bin/python3 daily_workflow.py >> logs/cron.log 2>&1
```

### 排程說明

| 時間欄位 | 說明 |
|---------|------|
| `30 15 * * 1-5` | 每週一到週五的 15:30 |
| `0 16 * * 1-5` | 每週一到週五的 16:00 |
| `*/30 15-17 * * 1-5` | 每週一到週五 15:00-17:00 每 30 分鐘 |

### 建議排程時間

- **15:30** - 盤後資料通常在 15:00 後更新
- 如果下載失敗，腳本會自動重試（預設 30 分鐘間隔，最多 5 次）

## 工作流程說明

```
daily_workflow.py
├── 步驟 1: 確認/下載 PDF
│   ├── 檢查 PDF 是否存在
│   ├── 不存在則嘗試下載
│   └── 失敗則 30 分鐘後重試（最多 5 次）
│
├── 步驟 2: 產生每日報告
│   └── 執行 main.py --date YYYYMMDD
│
├── 步驟 3: 檢查結算預報需求
│   ├── 週二 → 產生週三結算預報
│   ├── 週四 → 產生週五結算預報
│   └── 其他日 → 跳過
│
├── 步驟 4: 同步到 docs/
│   └── 執行 sync_to_docs.py
│
├── 步驟 5: 更新首頁
│   └── 執行 generate_index_with_weekday.py
│
└── 步驟 6: Git 推送
    └── git add + commit + push
```

## 日誌檔案位置

| 檔案 | 說明 |
|-----|------|
| `logs/workflow.log` | 完整日誌記錄 |
| `logs/workflow_history.json` | 執行歷史（最近 100 次）|
| `logs/cron.log` | Cron 執行輸出（如有設定）|

## 參數說明

| 參數 | 預設值 | 說明 |
|-----|-------|------|
| `--date` | 今天 | 目標日期 (YYYYMMDD) |
| `--max-retries` | 5 | PDF 下載最大重試次數 |
| `--retry-interval` | 1800 | 重試間隔（秒）= 30 分鐘 |
| `--skip-git` | False | 跳過 Git 推送 |
| `--force` | False | 強制重新下載 PDF |

## 故障排除

### PDF 下載失敗

1. 檢查網路連線
2. 確認期交所網站是否正常
3. 嘗試手動下載確認

### Git 推送失敗

1. 確認 Git 認證設定
2. 檢查遠端倉庫權限
3. 使用 `--skip-git` 跳過推送，手動處理

### 查看錯誤詳情

```bash
# 查看最近日誌
python3 daily_workflow.py --logs

# 查看最近一次執行詳情
python3 daily_workflow.py --detail
```
