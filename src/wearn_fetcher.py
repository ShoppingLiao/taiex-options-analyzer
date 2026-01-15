"""
從聚財網 (wearn.com) 抓取選擇權數據
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class WearnFetcher:
    """從聚財網抓取選擇權數據"""
    
    BASE_URL = "https://stock.wearn.com/option_analy.asp"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def fetch_contract_data(self, contract_code: str) -> Optional[Dict]:
        """
        抓取指定契約的選擇權數據
        
        Args:
            contract_code: 契約代碼，如 '202601f3', '202601w4', '202602'
        
        Returns:
            包含選擇權數據的字典，或 None（如果失敗）
        """
        try:
            url = f"{self.BASE_URL}?w={contract_code}"
            logger.info(f"抓取契約 {contract_code} 的數據: {url}")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 驗證契約是否正確
            selected = soup.find('option', {'selected': True})
            if not selected or selected.get('value') != contract_code:
                logger.warning(f"契約代碼不匹配: 期望 {contract_code}, 實際 {selected.get('value') if selected else 'None'}")
            
            # 解析數據
            data = self._parse_data(soup, contract_code)
            
            return data
            
        except Exception as e:
            logger.error(f"抓取契約 {contract_code} 數據失敗: {e}")
            return None
    
    def _parse_data(self, soup: BeautifulSoup, contract_code: str) -> Dict:
        """解析網頁數據"""
        
        # 找到主要數據表格
        tables = soup.find_all('table')
        data_table = None
        
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) > 10:  # 主要數據表格應該有很多行
                data_table = table
                break
        
        if not data_table:
            raise ValueError("找不到數據表格")
        
        rows = data_table.find_all('tr')
        
        # 解析表頭（第二行）
        header_row = rows[1]
        headers = [td.text.strip() for td in header_row.find_all('td')]
        
        # 解析數據行（從第3行開始）
        options_data = []
        
        for row in rows[2:]:
            cols = row.find_all('td')
            if len(cols) < 16:
                continue
            
            try:
                # 提取數據
                # 欄位順序: [0-7]買權數據, [8]履約價, [9-15]賣權數據
                strike_price = int(cols[8].text.strip())
                
                # Call (買權) 數據
                call_oi = int(cols[6].text.strip().replace(',', ''))
                call_change_text = cols[7].text.strip().replace(',', '')
                call_oi_change = int(call_change_text) if call_change_text and call_change_text != '─' else 0
                
                # Put (賣權) 數據
                put_oi = int(cols[14].text.strip().replace(',', ''))
                put_change_text = cols[15].text.strip().replace(',', '') if len(cols) > 15 else '0'
                put_oi_change = int(put_change_text) if put_change_text and put_change_text != '─' else 0
                
                options_data.append({
                    'strike_price': strike_price,
                    'call_oi': call_oi,
                    'call_oi_change': call_oi_change,
                    'put_oi': put_oi,
                    'put_oi_change': put_oi_change
                })
                
            except (ValueError, IndexError) as e:
                logger.debug(f"跳過無效數據行: {e}")
                continue
        
        logger.info(f"成功解析 {len(options_data)} 行數據")
        
        return {
            'contract_code': contract_code,
            'data': options_data,
            'fetch_time': datetime.now().isoformat()
        }
    
    def get_available_contracts(self) -> List[str]:
        """
        從聚財網取得所有可用的契約代碼
        
        Returns:
            契約代碼列表
        """
        try:
            response = self.session.get(self.BASE_URL, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            select = soup.find('select', class_='select_location')
            
            if not select:
                logger.error("找不到契約選單")
                return []
            
            contracts = []
            for option in select.find_all('option'):
                value = option.get('value')
                if value:
                    contracts.append(value)
            
            logger.info(f"找到 {len(contracts)} 個可用契約: {contracts}")
            return contracts
            
        except Exception as e:
            logger.error(f"取得契約列表失敗: {e}")
            return []
    
    def find_nearest_weekly_contracts(self, target_date: Optional[datetime] = None) -> Dict[str, str]:
        """
        找出最接近目標日期的週選契約（週三 + 週五）
        
        Args:
            target_date: 目標日期（預設為今天）
        
        Returns:
            字典，鍵為契約類型，值為契約代碼
        """
        if target_date is None:
            target_date = datetime.now()
        
        available_contracts = self.get_available_contracts()
        
        result = {}
        year_month = target_date.strftime('%Y%m')
        
        # 找當月週五契約中數字最小的（最近的）
        fri_contracts = [c for c in available_contracts if c.startswith(year_month) and 'f' in c.lower()]
        if fri_contracts:
            fri_contracts.sort()  # 排序，數字小的在前
            result['weekly_fri'] = fri_contracts[0]
        
        # 找當月週三契約中數字最小的（最近的）
        wed_contracts = [c for c in available_contracts if c.startswith(year_month) and 'w' in c.lower()]
        if wed_contracts:
            wed_contracts.sort()  # 排序，數字小的在前
            result['weekly_wed'] = wed_contracts[0]
        
        # 找近月契約（下個月）
        next_month = (target_date.replace(day=1) + timedelta(days=32)).replace(day=1)
        next_month_code = next_month.strftime('%Y%m')
        monthly_contracts = [c for c in available_contracts if c == next_month_code]
        if monthly_contracts:
            result['monthly'] = monthly_contracts[0]
        
        logger.info(f"找到的契約: {result}")
        return result
    
    def fetch_all_weekly_contracts(self, target_date: Optional[datetime] = None) -> Dict[str, Dict]:
        """
        抓取所有週選契約數據（週三 + 週五 + 近月）
        
        Args:
            target_date: 目標日期（預設為今天）
        
        Returns:
            字典，鍵為契約類型（'weekly_wed', 'weekly_fri', 'monthly'），值為數據
        """
        if target_date is None:
            target_date = datetime.now()
        
        # 自動找出可用的契約
        contracts = self.find_nearest_weekly_contracts(target_date)
        
        result = {}
        for contract_type, contract_code in contracts.items():
            logger.info(f"抓取 {contract_type} ({contract_code}) 的數據...")
            data = self.fetch_contract_data(contract_code)
            if data:
                result[contract_type] = data
        
        return result
    
    def _get_next_month_code(self, current_date: datetime) -> str:
        """計算近月選擇權的契約代碼"""
        # 近月通常是下個月
        next_month = current_date + timedelta(days=30)
        return next_month.strftime('%Y%m')


if __name__ == '__main__':
    # 測試
    logging.basicConfig(level=logging.INFO)
    
    fetcher = WearnFetcher()
    
    # 測試1: 取得可用契約列表
    print("=== 測試1: 取得可用契約列表 ===")
    contracts = fetcher.get_available_contracts()
    print(f"可用契約: {contracts}")
    
    # 測試2: 找出最近的週選契約
    print("\n=== 測試2: 找出最近的週選契約 ===")
    nearest = fetcher.find_nearest_weekly_contracts()
    for contract_type, contract_code in nearest.items():
        print(f"{contract_type}: {contract_code}")
    
    # 測試3: 抓取所有週選契約數據
    print("\n=== 測試3: 抓取所有週選契約數據 ===")
    all_data = fetcher.fetch_all_weekly_contracts()
    for contract_type, data in all_data.items():
        print(f"\n{contract_type} ({data['contract_code']}):")
        print(f"  數據筆數: {len(data['data'])}")
        print(f"  前3筆:")
        for item in data['data'][:3]:
            print(f"    履約價 {item['strike_price']}: Call OI={item['call_oi']} ({item['call_oi_change']:+d}), "
                  f"Put OI={item['put_oi']} ({item['put_oi_change']:+d})")
