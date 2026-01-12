# 台指選擇權分析工具

自動化分析台灣期貨交易所的選擇權盤後日報，產生視覺化分析報告。

## 🌟 功能特色

### 📅 單日報告
- 📊 **自動解析 PDF**：從期交所盤後日報提取選擇權資料
- 🎯 **Max Pain 分析**：計算最大痛點價位
- 📈 **OI 分布視覺化**：表格化呈現未平倉量分布
- 🤖 **AI 深度分析**：結算情境智能分析
- 📱 **RWD 響應式設計**：支援手機、平板、桌面裝置
- 🎨 **亞洲市場風格**：紅漲綠跌配色方案

### 🎯 結算日報告（新功能！）
- 📊 **趨勢分析**：整合 OI、P/C Ratio、價格動能等多項指標
- 🎬 **劇本情境**：提供強勢上攻、震盪整理、回檔修正等多種劇本
- ⭐ **強度評級**：1-5 星評估趨勢強度
- 🎲 **機率預測**：各劇本發生機率量化分析
- ⚠️ **風險提示**：市場風險因素智能評估
- 📈 **結算預測**：週三/週五結算區間預測

## 🚀 快速開始

### 安裝相依套件

```bash
pip install -r requirements.txt
```

### 單日報告生成

生成當日報告：

```bash
python3 main.py
```

生成指定日期報告：

```bash
python3 main.py --date 20260109
```

### 批量單日報告生成

生成 0105-0109 的報告：

```bash
python3 generate_batch_reports.py
```

生成指定日期範圍：

```bash
python3 generate_batch_reports.py 20260110 20260111
```

### 結算日報告生成

預測週三結算（使用週一二數據）：

```bash
python3 generate_settlement_report.py \
    --dates 20260105,20260106 \
    --settlement 2026/01/08 \
    --weekday wednesday
```

預測週五結算（使用週三四數據）：

```bash
python3 generate_settlement_report.py \
    --dates 20260107,20260108 \
    --settlement 2026/01/10 \
    --weekday friday
```

### 更新首頁索引

自動掃描並列出所有報告：

```bash
python3 generate_index_with_weekday.py
```

## 📁 專案結構

```
taiex-options-analyzer/
├── data/pdf/              # PDF 檔案存放位置
├── docs/                  # GitHub Pages 部署目錄
│   ├── index.html        # 報告總覽頁面
│   ├── report_*.html     # 單日報告
│   └── settlement_*.html # 結算日報告
├── reports/              # 生成的報告檔案
├── src/                  # 原始程式碼
│   ├── analyzer.py       # 選擇權分析邏輯
│   ├── fetcher.py        # PDF 下載器
│   ├── parser.py         # PDF 解析器
│   ├── reporter.py       # HTML 報告生成器
│   ├── settlement_analyzer.py      # 結算情境分析
│   ├── settlement_predictor.py     # 結算日預測器
│   └── settlement_report_generator.py  # 結算報告生成器
├── templates/            # HTML 模板
│   ├── report.html       # 單日報告模板
│   └── settlement_report.html  # 結算日報告模板
├── main.py              # 單日報告主程式
├── generate_batch_reports.py      # 批量生成腳本
├── generate_settlement_report.py  # 結算報告生成工具
└── generate_index_with_weekday.py # 首頁生成器
```

## 📊 報告內容

### 📅 單日報告

每份單日報告包含以下分析：

1. **基本資料**
   - 台指期貨 OHLC 價格
   - 成交量與結算價

2. **標準分析**
   - Max Pain 價位
   - P/C Ratio（Put/Call Ratio）
   - 未平倉量分布表格
   - OI 變化表格

3. **結算情境分析**
   - AI 智能判斷莊家位置
   - 多種結算情境預測
   - 關鍵價位標記

4. **詳細資料表**
   - 完整履約價數據
   - Call/Put OI 與變化

### 🎯 結算日報告

每份結算日報告包含以下分析：

1. **趨勢分析總覽**
   - 整體趨勢判斷（多頭/空頭/震盪）
   - 趨勢強度評級（1-5 星）
   - 預測結算區間
   - 當前價格參考

2. **趨勢訊號分析**
   - OI 變化訊號
   - P/C Ratio 訊號
   - 價格動能訊號
   - Max Pain 磁吸訊號
   - 每個訊號含方向、強度、說明

3. **結算劇本分析**
   - 🚀 強勢上攻劇本
   - ⚖️ 震盪整理劇本
   - 📉 回檔修正劇本
   - 🧲 Max Pain 磁吸劇本
   - 每個劇本含機率、區間、條件、策略

4. **關鍵指標儀表板**
   - Max Pain 價位
   - P/C Ratio（含變化）
   - 買權/賣權 OI（含變化）
   - 當前價格

5. **風險提示**
   - 市場風險因素
   - 數據異常警示
   - 投資注意事項

## 🎨 視覺化特色

### 📅 單日報告
- **表格化設計**：參考 PDF 原始格式的蝴蝶圖樣式
- **漸層背景**：視覺化 OI 強度
- **特殊標記**：
  - 🟡 收盤價位置（黃底）
  - 🟠 Max Pain 位置（橘底）
  - 🔴 最大 Call OI（紅底）
  - 🟢 最大 Put OI（綠底）
- **RWD 卡片布局**：
  - 手機版：單欄垂直排列
  - 電腦版：雙欄並排顯示
  - 卡片最大寬度：600px

### 🎯 結算日報告
- **趨勢指示器**：大型視覺化趨勢方向與強度
- **訊號卡片**：多頭📈/空頭📉/中性➖ 顏色區分
- **劇本卡片**：
  - 機率百分比顯示
  - 預測區間範圍
  - 關鍵價位標籤
  - 成立條件列表
  - 操作建議提示
- **響應式設計**：
  - 桌面版：多欄網格佈局
  - 手機版：單欄堆疊
  - 觸控友善的卡片互動

## 📅 資料來源

### 單日報告
- **台指期貨基本資料**：寫死在 `src/parser.py` 的 `tx_data_map`
- **選擇權資料**：自動從 PDF 解析
- **PDF 來源**：台灣期貨交易所盤後日報

### 結算日報告
- **數據來源**：已生成的單日報告 HTML
- **分析邏輯**：
  - 週一二數據 → 預測週三結算
  - 週三四數據 → 預測週五結算
- **關鍵指標**：OI 變化、P/C Ratio、Max Pain、價格動能

目前支援日期：

- 2026/01/05 - 2026/01/09（單日報告）
- 2026/01/08（週三結算預測）
- 2026/01/10（週五結算預測）

## 🌐 線上檢視

報告已自動部署到 GitHub Pages：
👉 [https://shoppingliao.github.io/taiex-options-analyzer/](https://shoppingliao.github.io/taiex-options-analyzer/)

### 報告類型

- **📅 單日報告**：每日選擇權市場分析
- **🎯 結算日報告**：週三/週五結算預測分析

### 查看範例

- [單日報告範例](https://shoppingliao.github.io/taiex-options-analyzer/report_20260109_202601.html)
- [週三結算報告](https://shoppingliao.github.io/taiex-options-analyzer/settlement_20260108_wed.html)
- [週五結算報告](https://shoppingliao.github.io/taiex-options-analyzer/settlement_20260110_fri.html)

## 🔧 新增日期資料

如需新增其他日期的台指期貨資料，請編輯 `src/parser.py`：

```python
tx_data_map = {
    '20260110': {  # 新增日期
        'open': 30500,
        'high': 30600,
        'low': 30400,
        'close': 30550,
        'volume': 115000,
        'settlement': 30550,
    }
}
```

## 📝 License

MIT

## 👤 Author

ShoppingLiao

---

⭐️ 如果這個專案對你有幫助，請給個星星！
