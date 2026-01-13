# /ai-performance - AI 績效統計

查看 AI 預測系統的績效統計與學習進度。

## 使用方式

```
/ai-performance              # 顯示完整績效報告
/ai-performance summary      # 簡要統計摘要
/ai-performance export       # 匯出績效數據為 JSON
```

## 執行流程

### 完整績效報告 (`/ai-performance`)

1. 執行績效追蹤器：
   ```bash
   python3 src/ai_performance_tracker.py
   ```

2. 顯示以下統計：
   - 總預測次數
   - 平均準確度
   - 方向正確率
   - 區間命中率
   - 平均價格誤差
   - 評分等級分佈

3. 讀取學習系統狀態：
   - 經驗等級
   - 累積記錄數
   - 學習洞察摘要

### 簡要摘要 (`/ai-performance summary`)

快速顯示關鍵指標：
- 總預測數
- 平均準確度
- 方向正確率
- 當前經驗等級

### 匯出數據 (`/ai-performance export`)

將績效數據匯出為 JSON：

```bash
python3 -c "
from src.ai_performance_tracker import AIPerformanceTracker
tracker = AIPerformanceTracker()
tracker.export_to_json('data/ai_learning/performance_export.json')
print('已匯出至 data/ai_learning/performance_export.json')
"
```

## 統計指標說明

### 準確度指標

| 指標 | 說明 |
|------|------|
| 平均準確度 | 綜合評分（0-100%） |
| 方向正確率 | 漲跌方向預測正確比例 |
| 區間命中率 | 實際價格落在預測區間的比例 |
| 平均價格誤差 | 預測價與實際價的平均差距（點） |

### 評分等級

| 等級 | 準確度範圍 |
|------|-----------|
| A+ | ≥90% |
| A | 80-89% |
| B+ | 70-79% |
| B | 60-69% |
| C+ | 50-59% |
| C | 40-49% |
| D | <40% |

### 經驗等級

| 等級 | 記錄數 | 圖示 |
|------|-------|------|
| 新手 | <5 | 🌱 |
| 學習中 | 5-14 | 📚 |
| 進階 | 15-29 | 🎯 |
| 專家 | 30-49 | ⭐ |
| 大師 | ≥50 | 👑 |

## 數據來源

績效統計基於以下數據：
- `data/ai_learning/reviews/` - 每日檢討記錄
- `data/ai_learning/settlement_reviews/` - 結算日檢討記錄
- `data/ai_learning/analysis_records.json` - 分析記錄

## 改進建議

根據績效統計，系統會提供改進建議：
- 方向預測偏差時：調整情緒分析權重
- 區間過窄時：增加波動率考量
- 系統性偏差時：重新校準模型參數
