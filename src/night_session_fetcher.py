"""
台指期貨夜盤資料抓取器

夜盤交易時間：15:00 ~ 次日 05:00（台灣時間）

由於期交所公開 API 不提供夜盤分段資料，
本模組嘗試從多個來源獲取夜盤資料：
1. 期交所 MIS 行情系統
2. Yahoo Finance
3. 估算方式（備用）
"""

import requests
from datetime import datetime, timedelta
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class NightSessionFetcher:
    """台指期貨夜盤資料抓取器"""

    # 期交所 MIS 行情系統 URL
    TAIFEX_MIS_URL = "https://mis.taifex.com.tw/futures/api/getQuoteList"

    # Yahoo Finance API（台指期貨）
    YAHOO_API_URL = "https://query1.finance.yahoo.com/v8/finance/chart"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def fetch_night_session(self, date: str) -> Optional[Dict]:
        """
        獲取指定日期的夜盤資料

        Args:
            date: 日期字串，格式為 YYYYMMDD（夜盤所屬的日期，
                  例如週四夜盤輸入週四的日期）

        Returns:
            {
                'date': str,           # 日期
                'open': float,         # 夜盤開盤
                'high': float,         # 夜盤最高
                'low': float,          # 夜盤最低
                'close': float,        # 夜盤收盤
                'amplitude': float,    # 震幅 (high - low)
                'amplitude_pct': float,# 震幅百分比
                'change': float,       # 漲跌點
                'change_pct': float,   # 漲跌百分比
                'source': str          # 資料來源
            }
            失敗則返回 None
        """
        logger.info(f"嘗試獲取 {date} 的夜盤資料...")

        # 方法 1: 嘗試從期交所 MIS 獲取
        data = self._fetch_from_taifex_mis(date)
        if data:
            return data

        # 方法 2: 嘗試從 Yahoo Finance 獲取
        data = self._fetch_from_yahoo(date)
        if data:
            return data

        # 方法 3: 使用估算方式
        logger.warning(f"無法從外部獲取 {date} 夜盤資料，使用估算方式")
        data = self._estimate_night_session(date)
        return data

    def _fetch_from_taifex_mis(self, date: str) -> Optional[Dict]:
        """從期交所 MIS 行情系統獲取夜盤資料"""
        try:
            # 期交所 MIS 系統的 API 請求格式
            # 這是即時行情系統，可能需要在交易時間內才能獲取
            response = self.session.get(
                self.TAIFEX_MIS_URL,
                params={
                    'MarketType': '0',      # 期貨
                    'SymbolType': 'F',      # 期貨
                    'KindID': 'TX',         # 台指期貨
                    'CID': 'TXF',           # 契約代碼
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                # 解析 MIS 回傳格式（需要根據實際回傳調整）
                if data and 'RtData' in data:
                    # 這裡需要根據實際 API 回傳格式解析
                    logger.info("從期交所 MIS 獲取資料成功")
                    # TODO: 解析實際資料格式
                    pass

        except Exception as e:
            logger.debug(f"期交所 MIS 獲取失敗: {e}")

        return None

    def _fetch_from_yahoo(self, date: str) -> Optional[Dict]:
        """從 Yahoo Finance 獲取夜盤資料"""
        try:
            # 台指期貨在 Yahoo Finance 的代碼
            # 可能的代碼: ^TWII (加權指數), TWF=F (台指期), 等
            symbols = ['TWF=F', 'FTWN.TW']

            for symbol in symbols:
                try:
                    # 計算時間範圍（夜盤時段：前一天 15:00 ~ 當天 05:00）
                    date_obj = datetime.strptime(date, '%Y%m%d')
                    start_time = int((date_obj - timedelta(days=1)).timestamp())
                    end_time = int(date_obj.timestamp())

                    response = self.session.get(
                        f"{self.YAHOO_API_URL}/{symbol}",
                        params={
                            'period1': start_time,
                            'period2': end_time,
                            'interval': '1h',
                            'includePrePost': 'true'
                        },
                        timeout=10
                    )

                    if response.status_code == 200:
                        data = response.json()
                        result = self._parse_yahoo_data(data, date)
                        if result:
                            result['source'] = f'Yahoo Finance ({symbol})'
                            logger.info(f"從 Yahoo Finance ({symbol}) 獲取資料成功")
                            return result

                except Exception as e:
                    logger.debug(f"Yahoo Finance ({symbol}) 獲取失敗: {e}")
                    continue

        except Exception as e:
            logger.debug(f"Yahoo Finance 獲取失敗: {e}")

        return None

    def _parse_yahoo_data(self, data: dict, date: str) -> Optional[Dict]:
        """解析 Yahoo Finance 回傳資料"""
        try:
            chart = data.get('chart', {}).get('result', [{}])[0]
            indicators = chart.get('indicators', {}).get('quote', [{}])[0]

            opens = indicators.get('open', [])
            highs = indicators.get('high', [])
            lows = indicators.get('low', [])
            closes = indicators.get('close', [])

            if not all([opens, highs, lows, closes]):
                return None

            # 過濾掉 None 值
            opens = [x for x in opens if x is not None]
            highs = [x for x in highs if x is not None]
            lows = [x for x in lows if x is not None]
            closes = [x for x in closes if x is not None]

            if not all([opens, highs, lows, closes]):
                return None

            open_price = opens[0]
            high_price = max(highs)
            low_price = min(lows)
            close_price = closes[-1]
            amplitude = high_price - low_price
            change = close_price - open_price

            return {
                'date': date,
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'amplitude': round(amplitude, 2),
                'amplitude_pct': round(amplitude / open_price * 100, 2) if open_price else 0,
                'change': round(change, 2),
                'change_pct': round(change / open_price * 100, 2) if open_price else 0,
            }

        except Exception as e:
            logger.debug(f"解析 Yahoo 資料失敗: {e}")
            return None

    def _estimate_night_session(self, date: str) -> Optional[Dict]:
        """
        估算夜盤資料（備用方案）

        基於歷史統計：
        - 夜盤震幅平均約 80-120 點
        - 夜盤通常跟隨國際盤走勢
        """
        try:
            base_price = 30000  # 預設值
            date_obj = datetime.strptime(date, '%Y%m%d')

            # 嘗試從本地的日報數據推算
            try:
                import sys
                from pathlib import Path
                # 確保能找到 src 模組
                project_root = Path(__file__).parent.parent
                if str(project_root) not in sys.path:
                    sys.path.insert(0, str(project_root))

                from src.twse_fetcher import TWSEDataFetcher

                fetcher = TWSEDataFetcher()

                # 獲取當天日盤收盤價作為基準
                day_data = fetcher.fetch_ohlc(date)
                if not day_data:
                    # 如果當天沒資料，使用前一天
                    prev_date = (date_obj - timedelta(days=1)).strftime('%Y%m%d')
                    day_data = fetcher.fetch_ohlc(prev_date)

                if day_data:
                    base_price = day_data.get('close', 30000)

            except ImportError as e:
                logger.debug(f"無法導入 TWSE fetcher: {e}")

            # 根據歷史統計估算夜盤波動
            # 夜盤平均震幅約 100 點（約 0.33%）
            estimated_amplitude = 100
            estimated_change = 0  # 保守估計無大幅變動

            return {
                'date': date,
                'open': base_price,
                'high': base_price + estimated_amplitude / 2,
                'low': base_price - estimated_amplitude / 2,
                'close': base_price + estimated_change,
                'amplitude': estimated_amplitude,
                'amplitude_pct': round(estimated_amplitude / base_price * 100, 2),
                'change': estimated_change,
                'change_pct': 0,
                'source': '估算值（基於日盤收盤）',
                'is_estimated': True
            }

        except Exception as e:
            logger.error(f"估算夜盤資料失敗: {e}")
            return None

    def fetch_realtime_night_session(self) -> Optional[Dict]:
        """
        獲取即時夜盤資料（用於盤中）

        Returns:
            即時夜盤資料或 None
        """
        try:
            # 嘗試從期交所 MIS 獲取即時報價
            response = self.session.get(
                self.TAIFEX_MIS_URL,
                params={
                    'MarketType': '0',
                    'SymbolType': 'F',
                    'KindID': 'TX',
                    'CID': 'TXF'
                },
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                # TODO: 解析即時報價
                pass

        except Exception as e:
            logger.debug(f"即時夜盤資料獲取失敗: {e}")

        return None


def test_fetcher():
    """測試夜盤資料抓取器"""
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("測試台指期貨夜盤資料抓取器")
    print("=" * 60)

    fetcher = NightSessionFetcher()

    # 測試日期
    test_dates = ['20260115', '20260114', '20260113']

    for date in test_dates:
        print(f"\n--- 測試日期: {date} ---")
        data = fetcher.fetch_night_session(date)

        if data:
            print(f"  資料來源: {data.get('source', 'N/A')}")
            print(f"  開盤: {data['open']:,.0f}")
            print(f"  最高: {data['high']:,.0f}")
            print(f"  最低: {data['low']:,.0f}")
            print(f"  收盤: {data['close']:,.0f}")
            print(f"  震幅: {data['amplitude']:,.0f} 點 ({data['amplitude_pct']:.2f}%)")
            print(f"  漲跌: {data['change']:+,.0f} 點 ({data['change_pct']:+.2f}%)")
            if data.get('is_estimated'):
                print("  ⚠️  此為估算值")
        else:
            print("  ❌ 無法獲取資料")


if __name__ == '__main__':
    test_fetcher()
