"""
PDF 解析模組
解析期貨選擇權盤後日報 PDF，擷取台指選擇權 (IO) 資料
"""

import re
import pdfplumber
import pandas as pd
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List, Dict
from src.twse_fetcher import TWSEDataFetcher


@dataclass
class OptionsData:
    """選擇權資料結構"""
    date: str  # 交易日期
    contract_month: str  # 契約月份
    strike_prices: List[int]  # 履約價清單
    call_volume: List[int]  # 買權成交量
    call_oi: List[int]  # 買權未平倉量
    call_oi_change: List[int]  # 買權未平倉量變化
    put_volume: List[int]  # 賣權成交量
    put_oi: List[int]  # 賣權未平倉量
    put_oi_change: List[int]  # 賣權未平倉量變化
    settlement_price: Optional[float] = None  # 結算價
    spot_price: Optional[float] = None  # 現貨價格
    
    # 台指期貨基本資料
    tx_open: Optional[float] = None  # 開盤價
    tx_high: Optional[float] = None  # 最高價
    tx_low: Optional[float] = None  # 最低價
    tx_close: Optional[float] = None  # 收盤價
    tx_volume: Optional[int] = None  # 成交量
    tx_settlement: Optional[float] = None  # 結算價
    
    # 契約類型相關資訊
    contract_type: Optional[str] = None  # 契約類型: 'weekly_wed', 'weekly_fri', 'monthly'
    contract_code: Optional[str] = None  # 契約代號: '202601W2', '202601F3', '202601'
    settlement_date: Optional[str] = None  # 結算日期: '2026/01/14'
    page_title: Optional[str] = None  # 頁面標題: '週三選擇權OI變化'

    def to_dataframe(self) -> pd.DataFrame:
        """轉換為 DataFrame"""
        return pd.DataFrame({
            '履約價': self.strike_prices,
            '買權成交量': self.call_volume,
            '買權未平倉': self.call_oi,
            '買權OI變化': self.call_oi_change,
            '賣權成交量': self.put_volume,
            '賣權未平倉': self.put_oi,
            '賣權OI變化': self.put_oi_change,
        })


class PDFParser:
    """期貨選擇權盤後日報 PDF 解析器"""

    def __init__(self):
        self.current_file = None

    # 固定頁面對應關係 (0-indexed)
    PAGE_CONFIG = {
        5: {'type': 'weekly_wed', 'name': '週三選擇權'},  # Page 6
        6: {'type': 'weekly_fri', 'name': '週五選擇權'},  # Page 7
        7: {'type': 'monthly', 'name': '近月選擇權'},     # Page 8
    }

    # X 座標範圍定義（用於座標解析模式）
    # 根據 PDF 結構：call_oi_change | call_oi | strike | put_oi | put_oi_change
    X_RANGES = {
        'call_oi_change': (50, 100),   # 左側第一欄
        'call_oi': (100, 200),          # 左側第二欄
        'strike': (230, 300),           # 中間履約價
        'put_oi': (420, 490),           # 右側第一欄
        'put_oi_change': (490, 550),    # 右側第二欄
    }

    def parse(self, pdf_path: str) -> List[OptionsData]:
        """
        解析 PDF 檔案，擷取所有月份的選擇權資料

        Args:
            pdf_path: PDF 檔案路徑

        Returns:
            各月份的選擇權資料清單 (週三、週五、近月)
        """
        self.current_file = Path(pdf_path)

        if not self.current_file.exists():
            raise FileNotFoundError(f"找不到檔案: {pdf_path}")

        # 從檔名提取日期
        date_match = re.search(r'(\d{8})', self.current_file.name)
        trade_date = date_match.group(1) if date_match else "unknown"

        all_options_data = []

        with pdfplumber.open(pdf_path) as pdf:
            # 從證交所 API 獲取加權指數 OHLC 資料
            tx_data = self._fetch_twse_ohlc_data(trade_date)

            # 固定解析 Page 6, 7, 8 (週三、週五、近月選擇權)
            for page_idx, config in self.PAGE_CONFIG.items():
                if page_idx >= len(pdf.pages):
                    continue

                page = pdf.pages[page_idx]
                text = page.extract_text() or ""

                # 先嘗試文字解析
                options_data = self._parse_options_page(text, trade_date, config)

                # 如果文字解析失敗或數據不足，嘗試座標解析
                if not options_data or len(options_data.strike_prices) < 5:
                    print(f"⚠️  Page {page_idx + 1} ({config['name']}) 文字解析失敗，嘗試座標解析...")
                    options_data = self._parse_options_page_by_coords(page, trade_date, config)

                if options_data:
                    print(f"✅ Page {page_idx + 1} ({config['name']}): 找到 {len(options_data.strike_prices)} 筆數據")
                    # 將加權指數資料加入選擇權資料
                    if tx_data:
                        options_data.tx_open = tx_data.get('open')
                        options_data.tx_high = tx_data.get('high')
                        options_data.tx_low = tx_data.get('low')
                        options_data.tx_close = tx_data.get('close')
                    all_options_data.append(options_data)
                else:
                    print(f"❌ Page {page_idx + 1} ({config['name']}): 解析失敗")

        return all_options_data
    
    def _fetch_twse_ohlc_data(self, trade_date: str) -> Optional[Dict]:
        """
        從台灣證券交易所 API 獲取加權指數 OHLC 資料
        
        Args:
            trade_date: 交易日期 (格式: YYYYMMDD)
            
        Returns:
            包含 open, high, low, close 的字典，失敗則返回 None
        """
        try:
            fetcher = TWSEDataFetcher()
            ohlc = fetcher.fetch_ohlc(trade_date)
            
            if ohlc:
                print(f"✅ 從證交所獲取 {trade_date} 加權指數: "
                      f"開 {ohlc['open']:.2f}, "
                      f"高 {ohlc['high']:.2f}, "
                      f"低 {ohlc['low']:.2f}, "
                      f"收 {ohlc['close']:.2f}")
                return ohlc
            else:
                print(f"⚠️  無法從證交所獲取 {trade_date} 的資料")
                return None
                
        except Exception as e:
            print(f"⚠️  證交所 API 錯誤: {e}")
            return None
    
    def _extract_settlement_date(self, text: str) -> Optional[str]:
        """
        從頁面文字中提取結算日期
        
        Returns:
            結算日期字串 '2026/01/14' 或 None
        """
        lines = text.split('\n')
        for line in lines[:30]:  # 只看前30行
            if '結算日' in line:
                # 找 YYYY/MM/DD 格式的日期
                date_match = re.search(r'(\d{4})/(\d{2})/(\d{2})', line)
                if date_match:
                    return f"{date_match.group(1)}/{date_match.group(2)}/{date_match.group(3)}"
        return None
    
    def _extract_page_title(self, text: str) -> str:
        """
        從頁面文字中提取標題
        
        Returns:
            頁面標題，如 '週三選擇權OI變化'
        """
        lines = text.split('\n')
        for line in lines[:15]:  # 只看前15行
            if 'OI變化' in line:
                return line.strip()
        return ""
    
    def _get_week_number(self, date) -> int:
        """
        獲取日期在當月的第幾週
        
        Returns:
            週數 (1-5)
        """
        from datetime import datetime, timedelta
        # 計算是當月第幾個該weekday
        first_day = date.replace(day=1)
        same_weekday_count = 0
        current = first_day
        while current <= date:
            if current.weekday() == date.weekday():
                same_weekday_count += 1
            current = current + timedelta(days=1)
        return same_weekday_count
    
    def _determine_contract_type(self, settlement_date_str: Optional[str], 
                                  page_title: str, trade_date: str) -> Dict:
        """
        根據結算日期和標題判斷契約類型
        
        Args:
            settlement_date_str: 結算日期字串 '2026/01/14'
            page_title: 頁面標題
            trade_date: 交易日期 'YYYYMMDD'
        
        Returns:
            契約資訊字典 {'type', 'code', 'name'}
        """
        from datetime import datetime
        
        if not settlement_date_str:
            # 無法判斷，使用預設值
            year_month = trade_date[:6]  # YYYYMM
            return {
                'type': 'unknown',
                'code': year_month,
                'name': '選擇權'
            }
        
        try:
            settlement_date = datetime.strptime(settlement_date_str, '%Y/%m/%d')
            weekday = settlement_date.weekday()  # 0=Monday, 2=Wednesday, 4=Friday
            year_month = settlement_date.strftime("%Y%m")
            
            # 計算週數
            week_num = self._get_week_number(settlement_date)
            
            # 優先從標題判斷
            if '週三' in page_title and weekday == 2:
                return {
                    'type': 'weekly_wed',
                    'code': f'{year_month}W{week_num}',
                    'name': '週三選擇權'
                }
            elif '週五' in page_title and weekday == 4:
                return {
                    'type': 'weekly_fri',
                    'code': f'{year_month}F{week_num}',
                    'name': '週五選擇權'
                }
            # 如果標題沒有明確指出，根據結算日的星期判斷
            elif weekday == 2:  # 週三
                return {
                    'type': 'weekly_wed',
                    'code': f'{year_month}W{week_num}',
                    'name': '週三選擇權'
                }
            elif weekday == 4:  # 週五
                return {
                    'type': 'weekly_fri',
                    'code': f'{year_month}F{week_num}',
                    'name': '週五選擇權'
                }
            else:
                # 近月選擇權（月選）- 結算日不是週三或週五
                return {
                    'type': 'monthly',
                    'code': year_month,
                    'name': '近月選擇權'
                }
        except Exception as e:
            print(f"⚠️  契約類型判斷錯誤: {e}")
            year_month = trade_date[:6]
            return {
                'type': 'unknown',
                'code': year_month,
                'name': '選擇權'
            }

    def _parse_options_page_by_coords(self, page, trade_date: str, config: Dict) -> Optional[OptionsData]:
        """
        使用座標方式解析選擇權頁面（用於處理特殊格式的 PDF）

        Args:
            page: pdfplumber 頁面物件
            trade_date: 交易日期
            config: 契約類型配置
        """
        try:
            words = page.extract_words()
            text = page.extract_text() or ""

            # 提取結算日期
            settlement_date_str = self._extract_settlement_date(text)

            # 設定契約資訊
            contract_type = config['type']
            contract_name = config['name']
            if settlement_date_str:
                from datetime import datetime
                try:
                    settlement_date = datetime.strptime(settlement_date_str, '%Y/%m/%d')
                    year_month = settlement_date.strftime("%Y%m")
                    week_num = self._get_week_number(settlement_date)
                    if contract_type == 'weekly_wed':
                        contract_code = f'{year_month}W{week_num}'
                    elif contract_type == 'weekly_fri':
                        contract_code = f'{year_month}F{week_num}'
                    else:
                        contract_code = year_month
                except:
                    contract_code = trade_date[:6]
            else:
                contract_code = trade_date[:6]

            # 按 Y 座標分組 words（每3像素一組，允許輕微偏差）
            rows = {}
            for word in words:
                y = round(word['top'] / 3) * 3
                if y not in rows:
                    rows[y] = []
                rows[y].append((word['x0'], word['text']))

            strike_prices = []
            call_oi = []
            call_oi_change = []
            put_oi = []
            put_oi_change = []

            # 解析每一行
            for y, words_in_row in sorted(rows.items()):
                # 按 X 座標分組
                col_data = {
                    'call_oi_change': [],
                    'call_oi': [],
                    'strike': [],
                    'put_oi': [],
                    'put_oi_change': [],
                }

                for x, text in words_in_row:
                    # 根據 X 座標判斷欄位
                    for col_name, (x_min, x_max) in self.X_RANGES.items():
                        if x_min <= x < x_max:
                            col_data[col_name].append(text)
                            break

                # 合併每個欄位的數字
                def merge_numbers(texts):
                    combined = ''.join(texts).replace(',', '').replace(' ', '')
                    numbers = re.findall(r'-?\d+', combined)
                    if numbers:
                        return int(numbers[0])
                    return None

                strike = merge_numbers(col_data['strike'])

                # 只處理有效的履約價行（20000-35000）
                if strike and 20000 <= strike <= 35000:
                    c_oi_chg = merge_numbers(col_data['call_oi_change']) or 0
                    c_oi = merge_numbers(col_data['call_oi']) or 0
                    p_oi = merge_numbers(col_data['put_oi']) or 0
                    p_oi_chg = merge_numbers(col_data['put_oi_change']) or 0

                    strike_prices.append(strike)
                    call_oi_change.append(c_oi_chg)
                    call_oi.append(c_oi)
                    put_oi.append(p_oi)
                    put_oi_change.append(p_oi_chg)

            if not strike_prices:
                return None

            # 按履約價排序
            sorted_data = sorted(zip(strike_prices, call_oi, call_oi_change, put_oi, put_oi_change))
            strike_prices, call_oi, call_oi_change, put_oi, put_oi_change = zip(*sorted_data)

            return OptionsData(
                date=trade_date,
                contract_month=contract_code,
                strike_prices=list(strike_prices),
                call_volume=[0] * len(strike_prices),
                call_oi=list(call_oi),
                call_oi_change=list(call_oi_change),
                put_volume=[0] * len(strike_prices),
                put_oi=list(put_oi),
                put_oi_change=list(put_oi_change),
                contract_type=contract_type,
                contract_code=contract_code,
                settlement_date=settlement_date_str,
                page_title=contract_name
            )

        except Exception as e:
            print(f"座標解析錯誤: {e}")
            return None

    def _parse_options_page(self, text: str, trade_date: str, config: Dict = None) -> Optional[OptionsData]:
        """
        解析選擇權頁面文字

        格式：
        Call                    202601              Put
        OI增減 OI              履約價              OI OI增減
        -22    423             28,500              2,868 -192

        Args:
            text: 頁面文字
            trade_date: 交易日期
            config: 契約類型配置 {'type': 'weekly_wed', 'name': '週三選擇權'}
        """
        try:
            lines = text.split('\n')

            # 提取結算日期
            settlement_date_str = self._extract_settlement_date(text)

            # 如果有傳入 config，直接使用；否則自動判斷
            if config:
                contract_type = config['type']
                contract_name = config['name']
                # 根據結算日期生成契約代碼
                if settlement_date_str:
                    from datetime import datetime
                    try:
                        settlement_date = datetime.strptime(settlement_date_str, '%Y/%m/%d')
                        year_month = settlement_date.strftime("%Y%m")
                        week_num = self._get_week_number(settlement_date)
                        if contract_type == 'weekly_wed':
                            contract_code = f'{year_month}W{week_num}'
                        elif contract_type == 'weekly_fri':
                            contract_code = f'{year_month}F{week_num}'
                        else:
                            contract_code = year_month
                    except:
                        contract_code = trade_date[:6]
                else:
                    contract_code = trade_date[:6]
            else:
                page_title = self._extract_page_title(text)
                contract_info = self._determine_contract_type(settlement_date_str, page_title, trade_date)
                contract_type = contract_info['type']
                contract_name = contract_info['name']
                contract_code = contract_info['code']

            # 向下相容：保留舊的 contract_month 欄位
            contract_month = contract_code

            strike_prices = []
            call_oi = []
            call_oi_change = []
            put_oi = []
            put_oi_change = []

            # 解析每一行數據
            for line in lines:
                # 跳過標題行和空行
                if not line.strip() or '履約價' in line or 'Call' in line or 'Put' in line:
                    continue
                if 'OI增減' in line or '合計' in line or 'P/C Ratio' in line:
                    continue
                if '華南' in line or '期貨' in line or '交易' in line:
                    continue

                # 清理行內容
                line = line.replace('▶', '').replace('◀', '').replace('▽', '').replace('▼', '').replace(',', '')

                # 嘗試匹配數據行: call_oi_change call_oi strike put_oi put_oi_change
                # 格式可能是: -22 423 28500 2868 -192
                numbers = re.findall(r'-?\d+', line)

                if len(numbers) >= 4:
                    # 尋找履約價 (通常是最大的數字，介於 20000-35000)
                    strike = None
                    strike_idx = -1

                    for i, num_str in enumerate(numbers):
                        num = int(num_str)
                        if 20000 <= num <= 35000:
                            strike = num
                            strike_idx = i
                            break

                    if strike is not None and strike_idx >= 2:
                        # 履約價前面是 call 數據，後面是 put 數據
                        try:
                            c_oi_chg = int(numbers[strike_idx - 2])
                            c_oi = int(numbers[strike_idx - 1])

                            # put 數據在履約價後面
                            p_oi = int(numbers[strike_idx + 1]) if strike_idx + 1 < len(numbers) else 0
                            p_oi_chg = int(numbers[strike_idx + 2]) if strike_idx + 2 < len(numbers) else 0

                            strike_prices.append(strike)
                            call_oi.append(c_oi)
                            call_oi_change.append(c_oi_chg)
                            put_oi.append(p_oi)
                            put_oi_change.append(p_oi_chg)
                        except (IndexError, ValueError):
                            continue

            if not strike_prices:
                return None

            # 按履約價排序
            sorted_data = sorted(zip(strike_prices, call_oi, call_oi_change, put_oi, put_oi_change))
            strike_prices, call_oi, call_oi_change, put_oi, put_oi_change = zip(*sorted_data)

            return OptionsData(
                date=trade_date,
                contract_month=contract_month,
                strike_prices=list(strike_prices),
                call_volume=[0] * len(strike_prices),  # 此 PDF 無成交量數據
                call_oi=list(call_oi),
                call_oi_change=list(call_oi_change),
                put_volume=[0] * len(strike_prices),
                put_oi=list(put_oi),
                put_oi_change=list(put_oi_change),
                # 新增契約類型相關資訊
                contract_type=contract_type,
                contract_code=contract_code,
                settlement_date=settlement_date_str,
                page_title=contract_name
            )

        except Exception as e:
            print(f"解析選擇權頁面時發生錯誤: {e}")
            return None

    def parse_to_dataframe(self, pdf_path: str) -> pd.DataFrame:
        """
        解析 PDF 並返回整合的 DataFrame

        Args:
            pdf_path: PDF 檔案路徑

        Returns:
            包含所有月份資料的 DataFrame
        """
        all_options = self.parse(pdf_path)

        if not all_options:
            return pd.DataFrame()

        # 合併所有月份的資料
        dfs = []
        for opt in all_options:
            df = opt.to_dataframe()
            df['交易日期'] = opt.date
            df['契約月份'] = opt.contract_month
            dfs.append(df)

        return pd.concat(dfs, ignore_index=True)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        # 尋找本地 PDF 檔案
        project_root = Path(__file__).parent.parent
        pdf_dir = project_root / "data" / "pdf"
        pdf_files = list(pdf_dir.glob("*.pdf"))

        if pdf_files:
            pdf_path = str(pdf_files[0])
        else:
            print("請提供 PDF 檔案路徑")
            sys.exit(1)

    print(f"解析檔案: {pdf_path}")
    parser = PDFParser()

    try:
        options_list = parser.parse(pdf_path)
        for opt in options_list:
            print(f"\n=== {opt.contract_month} 月份 ===")
            df = opt.to_dataframe()
            print(df.to_string())
    except Exception as e:
        print(f"解析失敗: {e}")
        import traceback
        traceback.print_exc()
