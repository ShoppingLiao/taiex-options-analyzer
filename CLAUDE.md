# CLAUDE.md — 給 Claude Code 的工作說明

## 專案概述

台指選擇權分析工具，自動解析台灣期貨交易所盤後日報 PDF，產生每日報告與結算日預測報告。
預測系統具備自動校準機制，從歷史結算審核資料持續學習，動態調整預測區間與情境機率。

## 環境設定

```bash
source venv/bin/activate   # 必須先啟動虛擬環境
pip install -r requirements.txt
```

## 常用指令

```bash
# 每日報告
python3 main.py                        # 生成當日報告
python3 main.py --date 20260120        # 指定日期

# 結算日報告
python3 generate_settlement_report.py \
    --dates 20260120,20260121 \
    --settlement 2026/01/22 \
    --weekday wednesday

# 校準預測系統（從 settlement_reviews 重新計算）
python3 analyze_settlement_history.py

# 首頁索引
python3 generate_index_with_weekday.py
```

## 重要目錄結構

```
data/ai_learning/
├── calibration.json        # 自動校準參數（週三/週五區間、情境機率）
├── settlement_reviews/     # 結算日事後審核（真實績效來源）
├── reviews/                # 每日預測事後審核
├── analysis_records.json   # 分析記錄
└── learned_insights.json   # 學習洞察（由 settlement_reviews 統計產出）

src/
├── ai_settlement_prediction.py  # 結算區間預測（讀 calibration.json）
├── ai_settlement_trader.py      # AI 操盤手分析
├── ai_learning_system.py        # 學習閉環管理
└── settlement_predictor.py      # 結算預測器（PC Ratio 逆向修正）
```

## 自定義 Skills

| 指令 | 說明 |
|------|------|
| `/daily-report` | 生成每日報告並部署 |
| `/settlement-report` | 生成結算日預測報告 |
| `/ai-train` | 執行 AI 學習訓練（更新 learned_insights） |
| `/ai-performance` | 查看 AI 預測績效統計 |

## 注意事項

- **交易日判斷**：週三結算用週一二資料；週五結算用週三四資料
- **校準資料**：`calibration.json` 由 `analyze_settlement_history.py` 產生，GitHub Actions 每次執行前自動重新校準
- **PC Ratio 解讀**：PC Ratio > 1.8 具逆向性（歷史 57% 機率上漲），不可直接視為看空訊號
- **樣本數警告**：目前校準資料約 15 筆，統計意義有限，解讀時須保留適度不確定性
- **GitHub Pages 部署**：報告輸出至 `docs/`，由 GitHub Actions 自動部署
