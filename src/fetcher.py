"""
PDF 下載模組
從統一期貨網站下載期貨選擇權盤後日報
"""

import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict


class PDFFetcher:
    """期貨選擇權盤後日報 PDF 下載器"""

    BASE_URL = "https://ft.entrust.com.tw"
    REPORT_LIST_URL = f"{BASE_URL}/entrustFutures/researchReport/inner.do"
    CATEGORY_ID = "603a0e313a00000059d8b24d1c7f8ded"

    def __init__(self, data_dir: str = None):
        """
        初始化下載器

        Args:
            data_dir: PDF 儲存目錄，預設為專案的 data/pdf 目錄
        """
        if data_dir is None:
            project_root = Path(__file__).parent.parent
            data_dir = project_root / "data" / "pdf"

        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
        })

    def get_available_reports(self) -> List[Dict]:
        """
        取得可下載的報告清單

        Returns:
            報告清單，每個報告包含 filename, date, download_url
        """
        params = {'category_id': self.CATEGORY_ID}

        try:
            response = self.session.get(self.REPORT_LIST_URL, params=params)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"無法取得報告清單: {e}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        reports = []

        # 從 data-pdf 屬性中提取 PDF 連結
        for link in soup.find_all('a', {'data-pdf': True}):
            pdf_url = link.get('data-pdf', '')
            if pdf_url and '期貨選擇權盤後日報' in pdf_url:
                date_match = re.search(r'(\d{8})', pdf_url)
                if date_match:
                    date_str = date_match.group(1)
                    reports.append({
                        'filename': f"期貨選擇權盤後日報_{date_str}.pdf",
                        'date': date_str,
                        'download_url': pdf_url,
                    })

        return reports

    def _parse_table_reports(self, soup: BeautifulSoup) -> List[Dict]:
        """
        從表格中解析報告清單
        """
        reports = []

        # 尋找表格中的資料
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                for cell in cells:
                    text = cell.get_text(strip=True)
                    if '期貨選擇權盤後日報' in text:
                        date_match = re.search(r'(\d{8})', text)
                        if date_match:
                            date_str = date_match.group(1)
                            # 嘗試在同一行找到下載連結
                            link = row.find('a', href=True)
                            if link:
                                href = link.get('href', '')
                                if href.startswith('http'):
                                    download_url = href
                                elif href.startswith('/'):
                                    download_url = self.BASE_URL + href
                                else:
                                    download_url = self.BASE_URL + '/' + href

                                reports.append({
                                    'filename': f"期貨選擇權盤後日報_{date_str}.pdf",
                                    'date': date_str,
                                    'download_url': download_url,
                                })

        return reports

    def download_report(self, date: str = None) -> Optional[str]:
        """
        下載指定日期的報告

        Args:
            date: 日期字串 (YYYYMMDD 格式)，預設為今天

        Returns:
            下載的檔案路徑，若失敗則返回 None
        """
        if date is None:
            date = datetime.now().strftime('%Y%m%d')

        filename = f"期貨選擇權盤後日報_{date}.pdf"
        filepath = self.data_dir / filename

        # 檢查是否已經下載過
        if filepath.exists():
            print(f"檔案已存在: {filepath}")
            return str(filepath)

        # 取得報告清單
        reports = self.get_available_reports()

        # 尋找指定日期的報告
        target_report = None
        for report in reports:
            if report['date'] == date:
                target_report = report
                break

        if target_report is None:
            print(f"找不到日期 {date} 的報告")
            # 嘗試直接構造下載 URL (備用方案)
            return self._try_direct_download(date)

        # 下載 PDF
        try:
            print(f"正在下載: {target_report['download_url']}")
            response = self.session.get(target_report['download_url'], stream=True)
            response.raise_for_status()

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"下載完成: {filepath}")
            return str(filepath)

        except requests.RequestException as e:
            print(f"下載失敗: {e}")
            return None

    def _try_direct_download(self, date: str) -> Optional[str]:
        """
        嘗試直接構造 URL 下載 (備用方案)
        """
        # 常見的 PDF URL 格式
        possible_urls = [
            f"{self.BASE_URL}/entrustFutures/researchReport/download.do?filename=期貨選擇權盤後日報_{date}.pdf",
            f"{self.BASE_URL}/entrustFutures/pdf/期貨選擇權盤後日報_{date}.pdf",
            f"{self.BASE_URL}/pdf/期貨選擇權盤後日報_{date}.pdf",
        ]

        filename = f"期貨選擇權盤後日報_{date}.pdf"
        filepath = self.data_dir / filename

        for url in possible_urls:
            try:
                response = self.session.get(url, stream=True)
                if response.status_code == 200 and 'pdf' in response.headers.get('Content-Type', '').lower():
                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"下載完成 (備用方案): {filepath}")
                    return str(filepath)
            except requests.RequestException:
                continue

        print(f"無法透過備用方案下載日期 {date} 的報告")
        return None

    def download_latest(self) -> Optional[str]:
        """
        下載最新的報告

        Returns:
            下載的檔案路徑，若失敗則返回 None
        """
        reports = self.get_available_reports()

        if not reports:
            print("無法取得報告清單，嘗試下載今天的報告")
            return self.download_report()

        # 取得最新的報告 (假設清單已按日期排序)
        latest = max(reports, key=lambda x: x['date'])
        print(f"最新報告日期: {latest['date']}")

        return self.download_report(latest['date'])

    def get_local_reports(self) -> List[str]:
        """
        取得本地已下載的報告檔案清單

        Returns:
            檔案路徑清單
        """
        return sorted(self.data_dir.glob("期貨選擇權盤後日報_*.pdf"), reverse=True)


if __name__ == "__main__":
    # 測試下載功能
    fetcher = PDFFetcher()

    print("=== 取得可用報告清單 ===")
    reports = fetcher.get_available_reports()
    for r in reports[:5]:
        print(f"  {r['filename']} - {r['date']}")

    print("\n=== 下載最新報告 ===")
    filepath = fetcher.download_latest()
    if filepath:
        print(f"已下載: {filepath}")
    else:
        print("下載失敗")
