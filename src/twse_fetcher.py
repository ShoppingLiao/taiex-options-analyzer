"""
台灣證券交易所資料獲取模組
從證交所官方 API 獲取加權指數的開高低收資料
"""

import requests
from typing import Optional, Dict
from datetime import datetime


class TWSEDataFetcher:
    """台灣證券交易所資料獲取器"""
    
    BASE_URL = "https://www.twse.com.tw/rwd/zh/TAIEX/MI_5MINS_INDEX"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def fetch_ohlc(self, date: str) -> Optional[Dict[str, float]]:
        """
        獲取指定日期的加權指數 OHLC 資料
        
        Args:
            date: 日期字串，格式為 YYYYMMDD，例如 "20260112"
        
        Returns:
            包含 open, high, low, close 的字典，失敗則返回 None
            
        Example:
            >>> fetcher = TWSEDataFetcher()
            >>> data = fetcher.fetch_ohlc("20260112")
            >>> print(data)
            {'open': 30472.70, 'high': 30681.99, 'low': 30472.70, 'close': 30567.29}
        """
        try:
            # 驗證日期格式
            if len(date) != 8 or not date.isdigit():
                raise ValueError(f"日期格式錯誤: {date}，應為 YYYYMMDD")
            
            # 呼叫 API
            params = {
                "date": date,
                "response": "json"
            }
            
            response = self.session.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # 檢查回應狀態
            if data.get('stat') != 'OK':
                print(f"⚠️  證交所 API 回應異常: {data.get('stat')}")
                return None
            
            # 檢查是否有資料
            records = data.get('data', [])
            if not records:
                print(f"⚠️  {date} 無交易資料（可能是假日或尚未交易）")
                return None
            
            # 提取發行量加權股價指數（第二欄，index=1）
            index_values = []
            times = []
            
            for record in records:
                time_str = record[0]
                index_str = record[1].replace(',', '')
                
                try:
                    index_val = float(index_str)
                    index_values.append(index_val)
                    times.append(time_str)
                except ValueError:
                    continue
            
            if not index_values:
                print(f"⚠️  無法解析指數資料")
                return None
            
            # 計算 OHLC
            # 注意：第一筆（09:00:00）通常是前一日收盤價，真正開盤從第二筆開始
            if len(index_values) < 2:
                print(f"⚠️  資料筆數不足")
                return None
            
            # 找到第一個交易時間（通常是 09:00:05 或附近）
            trading_start_idx = 1  # 跳過 09:00:00（前日收盤）
            
            # 如果第一筆時間確實是 09:00:00，則從第二筆開始
            if times[0] == "09:00:00":
                trading_values = index_values[trading_start_idx:]
            else:
                # 如果第一筆就不是 09:00:00，表示全部都是交易資料
                trading_values = index_values
            
            ohlc = {
                'open': trading_values[0],      # 開盤：第一筆交易價格
                'high': max(trading_values),     # 最高
                'low': min(trading_values),      # 最低
                'close': trading_values[-1],     # 收盤：最後一筆
            }
            
            return ohlc
            
        except requests.RequestException as e:
            print(f"❌ 網路請求失敗: {e}")
            return None
        except Exception as e:
            print(f"❌ 資料處理錯誤: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def fetch_ohlc_pretty(self, date: str) -> Optional[Dict[str, float]]:
        """
        獲取 OHLC 並顯示友善訊息
        
        Args:
            date: 日期字串，格式為 YYYYMMDD
            
        Returns:
            OHLC 字典或 None
        """
        print(f"\n📡 從證交所獲取 {date} 的加權指數資料...")
        
        ohlc = self.fetch_ohlc(date)
        
        if ohlc:
            print(f"✅ 成功獲取資料:")
            print(f"   開盤: {ohlc['open']:>10,.2f}")
            print(f"   最高: {ohlc['high']:>10,.2f}")
            print(f"   最低: {ohlc['low']:>10,.2f}")
            print(f"   收盤: {ohlc['close']:>10,.2f}")
            print(f"   振幅: {ohlc['high'] - ohlc['low']:>10,.2f} ({(ohlc['high'] - ohlc['low']) / ohlc['open'] * 100:.2f}%)")
        else:
            print(f"❌ 無法獲取資料")
        
        return ohlc


def test_fetcher():
    """測試資料獲取器"""
    fetcher = TWSEDataFetcher()
    
    # 測試已知日期
    test_dates = [
        "20260112",  # 週一
        "20260109",  # 週五
    ]
    
    for date in test_dates:
        print("=" * 60)
        ohlc = fetcher.fetch_ohlc_pretty(date)
        
        if ohlc:
            # 驗證資料合理性
            assert ohlc['low'] <= ohlc['open'] <= ohlc['high'], "開盤價應在高低之間"
            assert ohlc['low'] <= ohlc['close'] <= ohlc['high'], "收盤價應在高低之間"
            assert ohlc['high'] >= ohlc['low'], "最高價應大於等於最低價"
            print("✅ 資料驗證通過")
        
        print()


if __name__ == '__main__':
    test_fetcher()
