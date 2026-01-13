"""
台指期貨數據獲取器 (TAIFEX Fetcher)

從台灣期貨交易所獲取台指期貨的完整資訊，包括：
- 開盤價、最高價、最低價、收盤價
- 成交量
- 結算價
"""

import requests
import re
from typing import Optional, Dict
from datetime import datetime


class TAIFEXDataFetcher:
    """台指期貨數據獲取器 - 從期交所獲取數據"""
    
    # 期交所每日交易行情下載 API
    BASE_URL = "https://www.taifex.com.tw/cht/3/dlFutDataDown"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def fetch_futures_data(self, date: str) -> Optional[Dict]:
        """
        獲取台指期貨數據
        
        Args:
            date: 日期字串，格式為 YYYYMMDD
            
        Returns:
            包含期貨數據的字典:
            {
                'open': float,      # 開盤價
                'high': float,      # 最高價
                'low': float,       # 最低價
                'close': float,     # 收盤價
                'volume': int,      # 成交量（口）
                'settlement': float # 結算價
            }
            失敗則返回 None
        """
        try:
            # 將日期從 YYYYMMDD 轉換為 YYYY/MM/DD
            year = date[:4]
            month = date[4:6]
            day = date[6:8]
            date_formatted = f"{year}/{month}/{day}"
            
            # POST 參數 - 期交所需要的格式
            data = {
                'queryStartDate': date_formatted,
                'queryEndDate': date_formatted,
                'commodity_id': 'TX'  # TX = 台指期貨
            }
            
            print(f"📡 從期交所獲取 {date_formatted} 台指期貨數據...")
            
            response = self.session.post(
                self.BASE_URL, 
                data=data,
                timeout=15
            )
            response.raise_for_status()
            
            # 解析 CSV 數據
            result = self._parse_csv_data(response.text, date)
            
            if result:
                print(f"✅ 從期交所獲取台指期貨數據: "
                      f"開 {result['open']:.0f}, "
                      f"高 {result['high']:.0f}, "
                      f"低 {result['low']:.0f}, "
                      f"收 {result['close']:.0f}, "
                      f"量 {result['volume']:,}口, "
                      f"結算 {result.get('settlement', 0):.0f}")
                return result
            else:
                print(f"⚠️  無法從期交所解析 {date} 的台指期貨數據")
                print(f"   可能原因: (1) 該日期無交易 (假日/週末)")
                print(f"            (2) 數據格式改變")
                print(f"            (3) API 回應異常")
                return None
                
        except requests.RequestException as e:
            print(f"❌ 網路請求失敗: {e}")
            return None
        except Exception as e:
            print(f"❌ 資料處理錯誤: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _parse_csv_data(self, csv_text: str, date: str) -> Optional[Dict]:
        """
        解析期交所返回的 CSV 格式數據
        
        Args:
            csv_text: CSV 格式的文字
            date: 查詢日期 YYYYMMDD
            
        Returns:
            期貨數據字典或 None
        """
        try:
            if not csv_text or len(csv_text) < 10:
                return None
            
            # CSV 格式範例（期交所格式）:
            # 交易日期,契約,到期月份(週別),開盤價,最高價,最低價,收盤價,漲跌價,漲跌%,成交量,結算價,...
            
            lines = csv_text.strip().split('\n')
            
            # 尋找包含 "台指" 或 "TX" 的行
            for line in lines:
                # 跳過標題行
                if '交易日期' in line or '契約' in line:
                    continue
                
                # 解析數據行
                # 期交所的 CSV 通常以逗號分隔
                fields = line.split(',')
                
                # 檢查是否是台指期貨數據
                # 通常第二個欄位是商品代碼（TX）
                if len(fields) >= 10:
                    # 嘗試匹配台指期貨
                    if 'TX' in line or '台指' in line or 'TXF' in line:
                        try:
                            # 提取數據（索引可能需要根據實際格式調整）
                            # 這是一個通用解析邏輯，需要根據實際回應調整
                            data = {
                                'open': float(fields[3].replace(',', '')),
                                'high': float(fields[4].replace(',', '')),
                                'low': float(fields[5].replace(',', '')),
                                'close': float(fields[6].replace(',', '')),
                                'volume': int(fields[9].replace(',', '')),
                                'settlement': float(fields[10].replace(',', '')) if len(fields) > 10 else 0.0
                            }
                            return data
                        except (ValueError, IndexError) as e:
                            # 解析失敗，繼續嘗試下一行
                            continue
            
            # 如果沒有找到數據，嘗試其他解析方式
            # 使用正則表達式匹配數字
            return None
            
        except Exception as e:
            print(f"❌ CSV 解析失敗: {e}")
            return None


def test_fetcher():
    """測試台指期貨數據獲取器"""
    print("=" * 80)
    print("測試台指期貨數據獲取器 - 期交所 API")
    print("=" * 80)
    
    fetcher = TAIFEXDataFetcher()
    
    # 測試日期
    test_dates = [
        "20260109",  # 週五
        "20260112",  # 週一
        "20260107",  # 週二
    ]
    
    for date in test_dates:
        print(f"\n{'='*80}")
        print(f"測試日期: {date}")
        print('='*80)
        
        data = fetcher.fetch_futures_data(date)
        
        if data:
            print("\n✅ 獲取成功:")
            print(f"   開盤價: {data['open']:>12,.0f}")
            print(f"   最高價: {data['high']:>12,.0f}")
            print(f"   最低價: {data['low']:>12,.0f}")
            print(f"   收盤價: {data['close']:>12,.0f}")
            print(f"   成交量: {data['volume']:>12,} 口")
            print(f"   結算價: {data.get('settlement', 0):>12,.0f}")
        else:
            print("\n❌ 獲取失敗")
        
        print()
    
    print("=" * 80)


if __name__ == '__main__':
    test_fetcher()
