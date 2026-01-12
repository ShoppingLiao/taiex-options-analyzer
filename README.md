# 台指選擇權分析工具

自動化分析台灣期貨交易所的選擇權盤後日報，產生視覺化分析報告。

## 🌟 功能特色

- 📊 **自動解析 PDF**：從期交所盤後日報提取選擇權資料
- 🎯 **Max Pain 分析**：計算最大痛點價位
- 📈 **OI 分布視覺化**：表格化呈現未平倉量分布
- 🤖 **AI 深度分析**：結算情境智能分析
- 📱 **RWD 響應式設計**：支援手機、平板、桌面裝置
- 🎨 **亞洲市場風格**：紅漲綠跌配色方案

## 🚀 快速開始

### 安裝相依套件

```bash
pip install -r requirements.txt
```

### 單一報告生成

```bash
python3 main.py
```

### 批量報告生成

生成 0105-0108 的報告：

```bash
python3 generate_batch_reports.py
```

生成指定日期的報告：

```bash
python3 generate_batch_reports.py 20260110 20260111
```

## 📁 專案結構

```
taiex-options-analyzer/
├── data/pdf/              # PDF 檔案存放位置
├── docs/                  # GitHub Pages 部署目錄
│   └── index.html        # 報告總覽頁面
├── reports/              # 生成的報告檔案
├── src/                  # 原始程式碼
│   ├── analyzer.py       # 選擇權分析邏輯
│   ├── fetcher.py        # PDF 下載器
│   ├── parser.py         # PDF 解析器
│   └── reporter.py       # HTML 報告生成器
├── templates/            # HTML 模板
│   └── report.html       # 報告模板
├── main.py              # 主程式
└── generate_batch_reports.py  # 批量生成腳本
```

## 📊 報告內容

每份報告包含以下分析：

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

## 🎨 視覺化特色

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

## 📅 資料來源

- **台指期貨基本資料**：寫死在 `src/parser.py` 的 `tx_data_map`
- **選擇權資料**：自動從 PDF 解析
- **PDF 來源**：台灣期貨交易所盤後日報

目前支援日期：

- 2026/01/05
- 2026/01/06
- 2026/01/07
- 2026/01/08
- 2026/01/09

## 🌐 線上檢視

報告已自動部署到 GitHub Pages：
👉 [https://shoppingliao.github.io/taiex-options-analyzer/](https://shoppingliao.github.io/taiex-options-analyzer/)

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
