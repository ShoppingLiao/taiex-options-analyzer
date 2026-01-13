# 選擇權契約類型解析改進

## 問題描述

目前系統將 PDF 中的三個選擇權 OI 變化區塊都識別為同一個契約月份 (271800)，導致：

1. **報告結構不符 PDF**：PDF 有三個區塊，但報告只顯示一個
2. **契約類型混淆**：無法區分週三選擇權、週五選擇權、近月選擇權
3. **收盤價反黃錯誤**：第三個區塊反黃了 30,000 和 31,000，但實際收盤價是 30,567.29

## PDF 結構分析 (以 20260112 為例)

### 第 6 頁：週三選擇權 OI 變化

- **標題**: 週三選擇權 OI 變化
- **結算日**: 2026/01/14 (週三)
- **契約代號**: 202601W2
- **反黃履約價**: 30,000
- **收盤價**: 30,567.29

### 第 7 頁：週五選擇權 OI 變化

- **標題**: 週五選擇權 OI 變化
- **結算日**: 2026/01/16 (週五)
- **契約代號**: 202601F3
- **反黃履約價**: 28,500
- **收盤價**: 30,567.29

### 第 8 頁：近月選擇權 OI 變化

- **標題**: (空白或很短)
- **結算日**: 2026/01/21 (第三個週三 - 月選)
- **契約代號**: 202601
- **反黃履約價**: 30,000, 31,000 (可能是最大 OI，不是收盤價)
- **收盤價**: 30,567.29

## 解決方案

### 1. 改進 OptionsData 資料結構

添加字段：

- `contract_type`: 契約類型 ('weekly_wed', 'weekly_fri', 'monthly')
- `contract_code`: 契約代號 ('202601W2', '202601F3', '202601')
- `settlement_date`: 結算日期 ('2026/01/14')
- `page_title`: 頁面標題 ('週三選擇權 OI 變化')

### 2. 改進 PDF 解析邏輯

```python
def _parse_options_page(self, text: str, trade_date: str) -> Optional[OptionsData]:
    # 1. 提取結算日期
    settlement_date = self._extract_settlement_date(text)

    # 2. 提取頁面標題
    page_title = self._extract_page_title(text)

    # 3. 根據結算日期和標題推斷契約類型
    contract_info = self._determine_contract_type(settlement_date, page_title, trade_date)

    # 4. 解析 OI 數據
    # ... 現有邏輯 ...

    return OptionsData(
        date=trade_date,
        contract_month=contract_info['code'],  # '202601W2'
        contract_type=contract_info['type'],    # 'weekly_wed'
        settlement_date=settlement_date,         # '2026/01/14'
        page_title=page_title,                  # '週三選擇權OI變化'
        # ... 其他字段 ...
    )
```

### 3. 契約類型判斷邏輯

```python
def _determine_contract_type(self, settlement_date_str, page_title, trade_date):
    """
    根據結算日期和標題判斷契約類型

    規則：
    - 週三選擇權：最近的週三結算日，標題包含"週三"
    - 週五選擇權：最近的週五結算日，標題包含"週五"
    - 近月選擇權：當月第三個週三，標題不包含"週三"或"週五"
    """
    import datetime

    settlement_date = datetime.datetime.strptime(settlement_date_str, '%Y/%m/%d')
    weekday = settlement_date.weekday()  # 0=Monday, 2=Wednesday, 4=Friday

    # 從標題判斷
    if '週三' in page_title and weekday == 2:
        return {
            'type': 'weekly_wed',
            'code': f'{settlement_date.strftime("%Y%m")}W{self._get_week_number(settlement_date)}',
            'name': '週三選擇權'
        }
    elif '週五' in page_title and weekday == 4:
        return {
            'type': 'weekly_fri',
            'code': f'{settlement_date.strftime("%Y%m")}F{self._get_week_number(settlement_date)}',
            'name': '週五選擇權'
        }
    else:
        return {
            'type': 'monthly',
            'code': settlement_date.strftime("%Y%m"),
            'name': '近月選擇權'
        }
```

### 4. 報告格式調整

在 HTML 報告中：

```html
<div class="standard-analysis">
  <h2>📊 當日報告-標準分析</h2>

  <!-- 週三選擇權區塊 -->
  <div class="contract-section">
    <h3>📅 週三選擇權OI變化 (202601W2)</h3>
    <p class="settlement-info">結算日: 2026/01/14 (週三)</p>
    <table>
      <!-- OI 數據表格 -->
    </table>
  </div>

  <!-- 週五選擇權區塊 -->
  <div class="contract-section">
    <h3>📅 週五選擇權OI變化 (202601F3)</h3>
    <p class="settlement-info">結算日: 2026/01/16 (週五)</p>
    <table>
      <!-- OI 數據表格 -->
    </table>
  </div>

  <!-- 近月選擇權區塊 -->
  <div class="contract-section">
    <h3>📅 近月選擇權OI變化 (202601)</h3>
    <p class="settlement-info">結算日: 2026/01/21 (週三)</p>
    <table>
      <!-- OI 數據表格 -->
    </table>
  </div>
</div>
```

### 5. 收盤價反黃邏輯

對於每個契約區塊：

```python
def find_closest_strike(close_price, strike_prices):
    """找出最接近收盤價的履約價"""
    closest = min(strike_prices, key=lambda x: abs(x - close_price))
    return closest
```

在報告中標記最接近收盤價的履約價（不依賴 PDF 的 ▼ 標記）。

## 實施步驟

1. ✅ 分析問題，記錄 PDF 結構
2. ⏳ 修改 `OptionsData` dataclass
3. ⏳ 改進 `_parse_options_page()` 方法
4. ⏳ 更新 `reporter.py` 模板
5. ⏳ 測試 20260112 報告
6. ⏳ 重新生成並驗證

## 預期結果

✅ 報告中顯示三個獨立的選擇權 OI 變化表格
✅ 每個表格有正確的契約類型標示
✅ 收盤價反黃位置基於實際收盤價計算，而非 PDF 標記
✅ 報告結構與 PDF 完全對應
