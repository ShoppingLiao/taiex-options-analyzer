# PDF 解析失敗問題記錄

**日期**: 2026 年 1 月 13 日  
**問題報告**: 20260112 (週一) 的 PDF 無法解析

---

## 🐛 問題描述

嘗試生成 2026/01/12（週一）的單日報告時，PDF 解析失敗。

### 錯誤訊息

```
無法從 PDF 中解析出選擇權資料
可能原因:
  1. PDF 格式與預期不符
  2. PDF 內容為掃描圖片而非文字
```

### 警告訊息

大量的 pdfplumber 警告：

```
Cannot set gray non-stroke color because /'P48' is an invalid float value
Cannot set gray non-stroke color because /'P50' is an invalid float value
...
```

---

## 📊 測試結果

### 比較測試

```python
# 20260109 (成功的)
✅ 20260109: 成功解析 1 個月份的數據

# 20260112 (失敗的)
✅ 20260112: 成功解析 0 個月份的數據  ← PDF 能開啟，但沒找到數據
```

### 內容檢查

```python
總頁數: 11
第 1 頁: 履約價=False, OI=False, 選擇權=False
第 2 頁: 履約價=False, OI=False, 選擇權=False
第 3 頁: 履約價=False, OI=False, 選擇權=False
第 4 頁: 履約價=False, OI=False, 選擇權=False
第 5 頁: 履約價=False, OI=False, 選擇權=True  ← 只有"選擇權"關鍵字，沒有數據
```

**判斷**: PDF 文字提取失敗，可能是：

1. PDF 格式變更（證券公司改版）
2. 使用了不同的編碼方式
3. 表格採用圖片而非文字

---

## 🔍 已嘗試的解決方案

### 1. 重新下載 PDF

```bash
# 備份舊檔
mv data/pdf/期貨選擇權盤後日報_20260112.pdf data/pdf/期貨選擇權盤後日報_20260112_broken.pdf

# 重新下載
python3 main.py --date 20260112 --download-only
✅ 下載成功

# 測試解析
python3 main.py --date 20260112
❌ 仍然失敗
```

### 2. 測試不同參數

```bash
python3 main.py --local data/pdf/期貨選擇權盤後日報_20260112.pdf
❌ 仍然失敗
```

### 3. 比較文件大小

```bash
$ ls -lh data/pdf/*.pdf | grep "2026011"
1.5M  期貨選擇權盤後日報_20260105.pdf
1.5M  期貨選擇權盤後日報_20260106.pdf
1.5M  期貨選擇權盤後日報_20260107.pdf
1.5M  期貨選擇權盤後日報_20260108.pdf
1.5M  期貨選擇權盤後日報_20260109.pdf
1.4M  期貨選擇權盤後日報_20260112.pdf  ← 略小，但差異不大
```

---

## 💡 可能的原因分析

### 1. PDF 格式變更

- 期交所或證券公司可能在 01/12 改版了報告格式
- 新格式可能使用不同的表格結構
- 文字可能變成圖片嵌入

### 2. 週一特殊性

- 01/12 是週一，可能週一報告格式不同
- 之前測試的都是週二到週五的報告
- 需要檢查其他週一的報告是否也有問題

### 3. 編碼問題

- PDF 可能使用了新的字型或編碼
- pdfplumber 無法正確提取文字

---

## 🛠️ 建議解決方案

### 短期方案（手動）

1. **手動開啟 PDF 查看**：

   - 檢查 PDF 是否為正常的表格格式
   - 確認是否可以複製文字
   - 如果是圖片，則無法自動解析

2. **跳過此日期**：
   - 暫時跳過 01/12 的報告
   - 等待更多樣本來判斷是否為固定問題

### 中期方案（測試）

1. **測試下一個週一**：

   - 等到 01/19 (下週一) 測試是否相同問題
   - 如果只有 01/12 有問題，可能是單次異常
   - 如果所有週一都有問題，需要針對週一改寫解析器

2. **更新 pdfplumber 版本**：
   ```bash
   pip install --upgrade pdfplumber
   ```

### 長期方案（開發）

1. **增強 PDF 解析器**：

   - 添加更多容錯機制
   - 支援多種 PDF 格式
   - 添加 OCR 支援（使用 tesseract）

2. **多數據源支援**：

   - 不只依賴 PDF
   - 可以從期交所 API 抓取數據
   - 提供手動輸入數據的介面

3. **錯誤處理改進**：

   ```python
   # 在 parser.py 中添加
   def _parse_options_page_v2(self, text, trade_date):
       """支援新版 PDF 格式的解析"""
       pass

   def parse(self, pdf_path):
       # 嘗試舊格式
       data = self._parse_options_page(text, date)
       if not data:
           # 嘗試新格式
           data = self._parse_options_page_v2(text, date)
       return data
   ```

---

## 📋 下一步行動

### 立即行動

- [ ] 手動開啟 `data/pdf/期貨選擇權盤後日報_20260112.pdf` 確認內容
- [ ] 檢查 PDF 中的文字是否可複製
- [ ] 截圖 PDF 中的選擇權表格樣式

### 待觀察

- [ ] 等待 01/13 (週二) 的報告，測試是否正常
- [ ] 等待 01/19 (下週一) 的報告，測試週一是否固定有問題

### 未來開發

- [ ] 研究 pdfplumber 的替代方案
- [ ] 評估 OCR 解決方案的可行性
- [ ] 考慮使用期交所 API 作為備用數據源

---

## 🔗 相關資源

- PDF 來源: https://ft.entrust.com.tw/upload/entrust/researchReport/
- pdfplumber 文檔: https://github.com/jsvine/pdfplumber
- 可能需要的 OCR 工具: pytesseract

---

**狀態**: ⏸️ 暫時無解，等待更多樣本  
**影響範圍**: 僅 20260112 單日  
**優先級**: 中等（可手動處理）  
**記錄者**: Shopping Liao  
**記錄時間**: 2026 年 1 月 13 日

💡 **建議**: 先使用系統生成其他日期的報告，此問題不影響整體功能。
