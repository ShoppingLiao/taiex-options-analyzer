#!/usr/bin/env python3
"""
台指選擇權每日自動化工作流
- 自動下載 PDF 並產生日報
- 週二/四自動產生結算預報（預測週三/五結算）
- 自動更新首頁並推送到 Git
- 完整日誌記錄
- 支援交易日判斷（排除國定假日和週末）
"""

import os
import sys
import time
import subprocess
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import json


# 台灣股市國定假日（需每年更新）
# 格式: 'MMDD': '假日名稱'
TAIWAN_HOLIDAYS_2026 = {
    '0101': '元旦',
    '0102': '元旦補假',
    '0126': '農曆除夕前一日',
    '0127': '農曆除夕',
    '0128': '春節',
    '0129': '春節',
    '0130': '春節',
    '0202': '補假',
    '0228': '和平紀念日',
    '0403': '兒童節補假',
    '0404': '兒童節/清明節',
    '0405': '清明節',
    '0406': '清明節補假',
    '0501': '勞動節',
    '0531': '端午節',
    '0601': '端午節補假',
    '1009': '國慶日補假',
    '1010': '國慶日',
    '1025': '重陽節',
    '1026': '重陽節補假',
}

# 可擴展其他年份
TAIWAN_HOLIDAYS = {
    '2026': TAIWAN_HOLIDAYS_2026,
}


def is_trading_day(date_obj: datetime) -> tuple[bool, str]:
    """
    判斷是否為台灣股市交易日

    Args:
        date_obj: datetime 物件

    Returns:
        tuple: (是否為交易日, 原因說明)
    """
    # 檢查是否為週末
    if date_obj.weekday() >= 5:  # 5=週六, 6=週日
        weekday_name = '週六' if date_obj.weekday() == 5 else '週日'
        return False, f'{weekday_name}休市'

    # 檢查是否為國定假日
    year = date_obj.strftime('%Y')
    mmdd = date_obj.strftime('%m%d')

    if year in TAIWAN_HOLIDAYS:
        holidays = TAIWAN_HOLIDAYS[year]
        if mmdd in holidays:
            return False, f'{holidays[mmdd]}休市'

    return True, '交易日'


def get_next_trading_day(date_obj: datetime) -> datetime:
    """取得下一個交易日"""
    next_day = date_obj + timedelta(days=1)
    while not is_trading_day(next_day)[0]:
        next_day += timedelta(days=1)
    return next_day


def get_previous_trading_day(date_obj: datetime) -> datetime:
    """取得上一個交易日"""
    prev_day = date_obj - timedelta(days=1)
    while not is_trading_day(prev_day)[0]:
        prev_day -= timedelta(days=1)
    return prev_day


class WorkflowLogger:
    """工作流日誌記錄器"""

    def __init__(self, log_dir: str = 'logs'):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / 'workflow.log'
        self.history_file = self.log_dir / 'workflow_history.json'
        self.current_run = {
            'start_time': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y%m%d'),
            'steps': [],
            'status': 'running'
        }

    def log(self, message: str, level: str = 'INFO'):
        """記錄日誌"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"

        # 輸出到終端
        print(log_entry)

        # 寫入日誌檔
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + '\n')

        # 記錄步驟
        self.current_run['steps'].append({
            'time': timestamp,
            'level': level,
            'message': message
        })

    def info(self, message: str):
        self.log(message, 'INFO')

    def success(self, message: str):
        self.log(message, 'SUCCESS')

    def warning(self, message: str):
        self.log(message, 'WARNING')

    def error(self, message: str):
        self.log(message, 'ERROR')

    def save_run(self, status: str = 'completed'):
        """保存本次執行記錄"""
        self.current_run['end_time'] = datetime.now().isoformat()
        self.current_run['status'] = status

        # 讀取歷史記錄
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except:
                history = []

        # 添加本次記錄
        history.append(self.current_run)

        # 只保留最近 100 筆
        history = history[-100:]

        # 寫入歷史記錄
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)


class DailyWorkflow:
    """每日工作流"""

    def __init__(self, date: str = None, max_retries: int = 5, retry_interval: int = 1800):
        """
        初始化工作流

        Args:
            date: 目標日期 (YYYYMMDD)，預設為今天
            max_retries: 最大重試次數
            retry_interval: 重試間隔（秒），預設 1800 = 30 分鐘
        """
        self.date = date or datetime.now().strftime('%Y%m%d')
        self.max_retries = max_retries
        self.retry_interval = retry_interval
        self.logger = WorkflowLogger()

        # 路徑設定
        self.project_dir = Path(__file__).parent
        self.pdf_dir = self.project_dir / 'data' / 'pdf'
        self.pdf_filename = f'期貨選擇權盤後日報_{self.date}.pdf'
        self.pdf_path = self.pdf_dir / self.pdf_filename

        # 日期資訊
        self.date_obj = datetime.strptime(self.date, '%Y%m%d')
        self.weekday = self.date_obj.weekday()  # 0=週一, 4=週五
        self.weekday_names = ['一', '二', '三', '四', '五', '六', '日']

        # 交易日判斷
        self.is_trading, self.trading_reason = is_trading_day(self.date_obj)

    def run(self, skip_git: bool = False, force: bool = False):
        """執行完整工作流"""
        self.logger.info("=" * 60)
        self.logger.info(f"開始執行每日工作流")
        self.logger.info(f"目標日期: {self.date} (週{self.weekday_names[self.weekday]})")
        self.logger.info(f"交易日狀態: {self.trading_reason}")
        self.logger.info("=" * 60)

        try:
            # 非交易日處理流程
            if not self.is_trading:
                self.logger.warning(f"今天 ({self.date}) 非交易日: {self.trading_reason}")
                self.logger.info("跳過新報告生成，僅執行結算檢討")

                # 執行結算檢討（如果有需要）
                self._check_and_review_settlement()

                # 同步和更新首頁（保持網站最新狀態）
                if not self._sync_to_docs():
                    self.logger.warning("同步到 docs 失敗，繼續執行")
                if not self._update_index():
                    self.logger.warning("更新首頁失敗，繼續執行")

                # Git 推送
                if not skip_git:
                    if not self._git_push():
                        self.logger.warning("Git 推送失敗")

                self.logger.success("=" * 60)
                self.logger.success("非交易日工作流執行完成！")
                self.logger.success("=" * 60)
                self.logger.save_run('completed')
                return True

            # 交易日正常處理流程
            # 步驟 1: 確認/下載 PDF
            if not self._ensure_pdf(force):
                self.logger.error("無法取得 PDF，工作流終止")
                self.logger.save_run('failed')
                return False

            # 步驟 2: 產生每日報告
            if not self._generate_daily_report():
                self.logger.error("產生每日報告失敗")
                self.logger.save_run('failed')
                return False

            # 步驟 3: 檢查是否需要產生結算預報
            self._check_and_generate_settlement_report()

            # 步驟 4: 同步到 docs
            if not self._sync_to_docs():
                self.logger.warning("同步到 docs 失敗，繼續執行")

            # 步驟 5: 更新首頁
            if not self._update_index():
                self.logger.warning("更新首頁失敗，繼續執行")

            # 步驟 6: Git 推送
            if not skip_git:
                if not self._git_push():
                    self.logger.warning("Git 推送失敗")
            else:
                self.logger.info("跳過 Git 推送")

            self.logger.success("=" * 60)
            self.logger.success("每日工作流執行完成！")
            self.logger.success("=" * 60)
            self.logger.save_run('completed')
            return True

        except Exception as e:
            self.logger.error(f"工作流執行失敗: {str(e)}")
            self.logger.save_run('failed')
            return False

    def _ensure_pdf(self, force: bool = False) -> bool:
        """確保 PDF 存在，不存在則下載"""
        self.logger.info("-" * 40)
        self.logger.info("步驟 1: 確認 PDF 檔案")

        # 檢查是否已存在
        if self.pdf_path.exists() and not force:
            self.logger.success(f"PDF 已存在: {self.pdf_filename}")
            return True

        # 嘗試下載
        for attempt in range(1, self.max_retries + 1):
            self.logger.info(f"嘗試下載 PDF (第 {attempt}/{self.max_retries} 次)...")

            if self._download_pdf():
                self.logger.success(f"PDF 下載成功: {self.pdf_filename}")
                return True

            if attempt < self.max_retries:
                wait_minutes = self.retry_interval // 60
                self.logger.warning(f"下載失敗，{wait_minutes} 分鐘後重試...")
                self.logger.info(f"下次嘗試時間: {(datetime.now() + timedelta(seconds=self.retry_interval)).strftime('%H:%M:%S')}")
                time.sleep(self.retry_interval)

        self.logger.error(f"已達最大重試次數 ({self.max_retries})，放棄下載")
        return False

    def _download_pdf(self) -> bool:
        """下載 PDF"""
        try:
            # 使用 main.py 的下載功能
            result = subprocess.run(
                ['python3', 'main.py', '--date', self.date, '--download-only'],
                capture_output=True,
                text=True,
                cwd=self.project_dir
            )

            # 檢查 PDF 是否存在
            if self.pdf_path.exists():
                return True

            # 如果沒有 --download-only 選項，嘗試直接執行看看會不會下載
            result = subprocess.run(
                ['python3', 'main.py', '--date', self.date],
                capture_output=True,
                text=True,
                cwd=self.project_dir,
                timeout=120
            )

            return self.pdf_path.exists()

        except subprocess.TimeoutExpired:
            self.logger.warning("下載超時")
            return False
        except Exception as e:
            self.logger.warning(f"下載過程發生錯誤: {str(e)}")
            return False

    def _generate_daily_report(self) -> bool:
        """產生每日報告"""
        self.logger.info("-" * 40)
        self.logger.info("步驟 2: 產生每日報告")

        try:
            result = subprocess.run(
                ['python3', 'main.py', '--date', self.date],
                capture_output=True,
                text=True,
                cwd=self.project_dir,
                timeout=180
            )

            if result.returncode == 0:
                self.logger.success("每日報告產生成功")
                return True
            else:
                self.logger.error(f"產生報告失敗: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.logger.error("產生報告超時")
            return False
        except Exception as e:
            self.logger.error(f"產生報告失敗: {str(e)}")
            return False

    def _check_and_generate_settlement_report(self):
        """檢查並產生結算預報或執行結算檢討"""
        self.logger.info("-" * 40)
        self.logger.info("步驟 3: 檢查結算預報/檢討需求")

        current_weekday_name = self.weekday_names[self.weekday]
        self.logger.info(f"今天是週{current_weekday_name} (weekday={self.weekday})")

        # 週二 (1) -> 產生週三結算預報
        # 週三 (2) -> 執行週三結算檢討
        # 週四 (3) -> 產生週五結算預報
        # 週五 (4) -> 執行週五結算檢討

        if self.weekday == 1:  # 週二
            self.logger.info(f"週{current_weekday_name}：產生週三結算預報")
            self._generate_settlement_report('wednesday')
        elif self.weekday == 2:  # 週三
            self.logger.info(f"週{current_weekday_name}：執行週三結算檢討")
            self._run_settlement_review('wednesday')
        elif self.weekday == 3:  # 週四
            self.logger.info(f"週{current_weekday_name}：產生週五結算預報")
            self._generate_settlement_report('friday')
        elif self.weekday == 4:  # 週五
            self.logger.info(f"週{current_weekday_name}：執行週五結算檢討")
            self._run_settlement_review('friday')
        else:
            self.logger.info(f"週{current_weekday_name}不需要產生結算預報或檢討")

    def _check_and_review_settlement(self):
        """非交易日執行結算檢討"""
        self.logger.info("-" * 40)
        self.logger.info("檢查是否有結算報告需要檢討")

        # 取得最近的交易日
        last_trading_day = get_previous_trading_day(self.date_obj)
        self.logger.info(f"最近交易日: {last_trading_day.strftime('%Y%m%d')}")

        # 這裡可以加入結算檢討的邏輯
        # 例如：檢查上一個結算日的預報準確度
        self.logger.info("結算檢討功能（待實作）")

    def _generate_settlement_report(self, weekday: str):
        """產生結算預報"""
        try:
            # 計算結算日
            if weekday == 'wednesday':
                days_ahead = 1  # 週二到週三
                settlement_date = self.date_obj + timedelta(days=days_ahead)
                # 分析日期：前兩個交易日
                analysis_dates = self._get_previous_trading_days(2)
            else:  # friday
                days_ahead = 1  # 週四到週五
                settlement_date = self.date_obj + timedelta(days=days_ahead)
                analysis_dates = self._get_previous_trading_days(2)

            settlement_str = settlement_date.strftime('%Y/%m/%d')
            dates_str = ','.join(analysis_dates)

            self.logger.info(f"結算日: {settlement_str}")
            self.logger.info(f"分析日期: {dates_str}")

            result = subprocess.run(
                [
                    'python3', 'generate_settlement_report.py',
                    '--dates', dates_str,
                    '--settlement', settlement_str,
                    '--weekday', weekday
                ],
                capture_output=True,
                text=True,
                cwd=self.project_dir,
                timeout=180
            )

            if result.returncode == 0:
                self.logger.success(f"{weekday} 結算預報產生成功")
            else:
                self.logger.warning(f"結算預報產生可能有問題: {result.stderr}")

        except Exception as e:
            self.logger.warning(f"產生結算預報失敗: {str(e)}")

    def _run_settlement_review(self, weekday: str):
        """執行結算日檢討並更新報告"""
        try:
            # 結算日就是今天
            settlement_date = self.date
            settlement_str = self.date_obj.strftime('%Y/%m/%d')
            pdf_path = f"data/pdf/期貨選擇權盤後日報_{settlement_date}.pdf"

            self.logger.info(f"結算日: {settlement_str}")
            self.logger.info(f"PDF 路徑: {pdf_path}")

            # 步驟 1: 執行結算檢討腳本
            self.logger.info("執行結算檢討...")
            result = subprocess.run(
                [
                    'python3', 'generate_settlement_review.py',
                    '--settlement-date', settlement_date,
                    '--pdf-path', pdf_path
                ],
                capture_output=True,
                text=True,
                cwd=self.project_dir,
                timeout=180
            )

            if result.returncode == 0:
                self.logger.success("結算檢討完成")
            else:
                self.logger.warning(f"結算檢討可能有問題: {result.stderr}")
                # 如果找不到預測記錄，先重新生成結算預報
                if '找不到' in result.stderr or '找不到' in result.stdout:
                    self.logger.info("嘗試重新生成結算預報後再執行檢討...")
                    self._regenerate_settlement_report_with_prediction(weekday)
                    # 再次執行檢討
                    result = subprocess.run(
                        [
                            'python3', 'generate_settlement_review.py',
                            '--settlement-date', settlement_date,
                            '--pdf-path', pdf_path
                        ],
                        capture_output=True,
                        text=True,
                        cwd=self.project_dir,
                        timeout=180
                    )
                    if result.returncode == 0:
                        self.logger.success("結算檢討完成（重試後）")

            # 步驟 2: 重新生成結算報告（讓檢討內容更新到 HTML）
            self.logger.info("更新結算報告...")
            self._regenerate_settlement_report_with_prediction(weekday)

        except Exception as e:
            self.logger.warning(f"執行結算檢討失敗: {str(e)}")

    def _regenerate_settlement_report_with_prediction(self, weekday: str):
        """重新生成結算報告（包含 AI 預測記錄）"""
        try:
            settlement_str = self.date_obj.strftime('%Y/%m/%d')
            # 取得前兩個交易日
            analysis_dates = self._get_previous_trading_days_before_today(2)
            dates_str = ','.join(analysis_dates)

            self.logger.info(f"分析日期: {dates_str}")

            result = subprocess.run(
                [
                    'python3', 'generate_settlement_report.py',
                    '--dates', dates_str,
                    '--settlement', settlement_str,
                    '--weekday', weekday
                ],
                capture_output=True,
                text=True,
                cwd=self.project_dir,
                timeout=180
            )

            if result.returncode == 0:
                self.logger.success(f"結算報告更新成功")
            else:
                self.logger.warning(f"結算報告更新可能有問題: {result.stderr}")

        except Exception as e:
            self.logger.warning(f"重新生成結算報告失敗: {str(e)}")

    def _generate_premarket_prediction(self, weekday: str):
        """結算日早上生成盤前預測"""
        try:
            settlement_date = self.date

            self.logger.info(f"結算日: {settlement_date}")
            self.logger.info(f"星期: {'週三' if weekday == 'wednesday' else '週五'}")

            result = subprocess.run(
                [
                    'python3', 'generate_premarket_prediction.py',
                    '--settlement-date', settlement_date,
                    '--weekday', weekday
                ],
                capture_output=True,
                text=True,
                cwd=self.project_dir,
                timeout=180
            )

            if result.returncode == 0:
                self.logger.success(f"盤前預測生成成功")
                # 顯示部分輸出
                if result.stdout:
                    for line in result.stdout.split('\n')[-10:]:
                        if line.strip():
                            self.logger.info(f"  {line}")
            else:
                self.logger.warning(f"盤前預測生成可能有問題: {result.stderr}")

        except Exception as e:
            self.logger.warning(f"生成盤前預測失敗: {str(e)}")

    def run_premarket(self, skip_git: bool = False):
        """執行盤前預測工作流（結算日早上 08:00）"""
        self.logger.info("=" * 60)
        self.logger.info(f"開始執行盤前預測工作流")
        self.logger.info(f"目標日期: {self.date} (週{self.weekday_names[self.weekday]})")
        self.logger.info(f"交易日狀態: {self.trading_reason}")
        self.logger.info("=" * 60)

        try:
            # 非交易日不執行
            if not self.is_trading:
                self.logger.warning(f"今天 ({self.date}) 非交易日: {self.trading_reason}")
                self.logger.info("跳過盤前預測生成")
                self.logger.save_run('skipped')
                return True

            # 只在週三(2)或週五(4)執行
            if self.weekday == 2:  # 週三
                weekday = 'wednesday'
            elif self.weekday == 4:  # 週五
                weekday = 'friday'
            else:
                self.logger.info(f"今天不是結算日，跳過盤前預測")
                self.logger.save_run('skipped')
                return True

            # 步驟 1: 生成盤前預測
            self.logger.info("-" * 40)
            self.logger.info("步驟 1: 生成盤前預測")
            self._generate_premarket_prediction(weekday)

            # 步驟 2: 同步到 docs
            if not self._sync_to_docs():
                self.logger.warning("同步到 docs 失敗，繼續執行")

            # 步驟 3: 更新首頁
            if not self._update_index():
                self.logger.warning("更新首頁失敗，繼續執行")

            # 步驟 4: Git 推送
            if not skip_git:
                if not self._git_push_premarket():
                    self.logger.warning("Git 推送失敗")
            else:
                self.logger.info("跳過 Git 推送")

            self.logger.success("=" * 60)
            self.logger.success("盤前預測工作流執行完成！")
            self.logger.success("=" * 60)
            self.logger.save_run('completed')
            return True

        except Exception as e:
            self.logger.error(f"盤前預測工作流執行失敗: {str(e)}")
            self.logger.save_run('failed')
            return False

    def _git_push_premarket(self) -> bool:
        """Git 推送（盤前預測專用）"""
        self.logger.info("-" * 40)
        self.logger.info("步驟 4: Git 推送")

        try:
            # Git add
            subprocess.run(
                ['git', 'add', 'docs/', 'data/ai_learning/'],
                cwd=self.project_dir,
                capture_output=True
            )

            # Git commit
            commit_msg = f"auto: {self.date} 盤前預測"
            result = subprocess.run(
                ['git', 'commit', '-m', commit_msg],
                cwd=self.project_dir,
                capture_output=True,
                text=True
            )

            if 'nothing to commit' in result.stdout or 'nothing to commit' in result.stderr:
                self.logger.info("沒有變更需要提交")
                return True

            # Git push
            result = subprocess.run(
                ['git', 'push'],
                cwd=self.project_dir,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                self.logger.success("Git 推送成功")
                return True
            else:
                self.logger.error(f"Git 推送失敗: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Git 操作失敗: {str(e)}")
            return False

    def _get_previous_trading_days_before_today(self, count: int) -> list:
        """取得今天之前的 N 個交易日"""
        trading_days = []
        current = self.date_obj - timedelta(days=1)  # 從昨天開始

        while len(trading_days) < count:
            if is_trading_day(current)[0]:
                trading_days.append(current.strftime('%Y%m%d'))
            current -= timedelta(days=1)

        # 反轉順序（從舊到新）
        return list(reversed(trading_days))

    def _get_previous_trading_days(self, count: int) -> list:
        """取得前 N 個交易日（包含今天，如果今天是交易日）"""
        trading_days = []
        current = self.date_obj

        while len(trading_days) < count:
            # 使用 is_trading_day 函數判斷（包含國定假日）
            if is_trading_day(current)[0]:
                trading_days.append(current.strftime('%Y%m%d'))
            current -= timedelta(days=1)

        # 反轉順序（從舊到新）
        return list(reversed(trading_days))

    def _sync_to_docs(self) -> bool:
        """同步到 docs 目錄"""
        self.logger.info("-" * 40)
        self.logger.info("步驟 4: 同步到 docs")

        try:
            result = subprocess.run(
                ['python3', 'sync_to_docs.py'],
                capture_output=True,
                text=True,
                cwd=self.project_dir
            )

            if result.returncode == 0:
                self.logger.success("同步完成")
                return True
            else:
                self.logger.warning(f"同步可能有問題: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"同步失敗: {str(e)}")
            return False

    def _update_index(self) -> bool:
        """更新首頁"""
        self.logger.info("-" * 40)
        self.logger.info("步驟 5: 更新首頁")

        try:
            result = subprocess.run(
                ['python3', 'generate_index_with_weekday.py'],
                capture_output=True,
                text=True,
                cwd=self.project_dir
            )

            if result.returncode == 0:
                self.logger.success("首頁更新完成")
                return True
            else:
                self.logger.warning(f"首頁更新可能有問題: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"首頁更新失敗: {str(e)}")
            return False

    def _git_push(self) -> bool:
        """Git 推送"""
        self.logger.info("-" * 40)
        self.logger.info("步驟 6: Git 推送")

        try:
            # Git add
            subprocess.run(
                ['git', 'add', 'docs/', 'reports/', 'logs/'],
                cwd=self.project_dir,
                capture_output=True
            )

            # Git commit
            commit_msg = f"auto: {self.date} 每日報告更新"
            result = subprocess.run(
                ['git', 'commit', '-m', commit_msg],
                cwd=self.project_dir,
                capture_output=True,
                text=True
            )

            if 'nothing to commit' in result.stdout or 'nothing to commit' in result.stderr:
                self.logger.info("沒有變更需要提交")
                return True

            # Git push
            result = subprocess.run(
                ['git', 'push'],
                cwd=self.project_dir,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                self.logger.success("Git 推送成功")
                return True
            else:
                self.logger.error(f"Git 推送失敗: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"Git 操作失敗: {str(e)}")
            return False


def view_logs(lines: int = 50):
    """查看最近日誌"""
    log_file = Path('logs/workflow.log')

    if not log_file.exists():
        print("尚無日誌記錄")
        return

    print("=" * 60)
    print(f"最近 {lines} 行日誌")
    print("=" * 60)

    with open(log_file, 'r', encoding='utf-8') as f:
        all_lines = f.readlines()
        recent_lines = all_lines[-lines:]
        for line in recent_lines:
            print(line.rstrip())


def view_history(count: int = 10):
    """查看執行歷史"""
    history_file = Path('logs/workflow_history.json')

    if not history_file.exists():
        print("尚無執行歷史")
        return

    with open(history_file, 'r', encoding='utf-8') as f:
        history = json.load(f)

    print("=" * 60)
    print(f"最近 {count} 次執行記錄")
    print("=" * 60)

    for run in history[-count:]:
        status_icon = "✅" if run['status'] == 'completed' else "❌"
        start_time = run.get('start_time', 'N/A')[:19]
        date = run.get('date', 'N/A')
        step_count = len(run.get('steps', []))

        print(f"{status_icon} [{start_time}] 日期: {date} | 步驟數: {step_count} | 狀態: {run['status']}")


def view_history_detail(index: int = -1):
    """查看特定執行的詳細記錄"""
    history_file = Path('logs/workflow_history.json')

    if not history_file.exists():
        print("尚無執行歷史")
        return

    with open(history_file, 'r', encoding='utf-8') as f:
        history = json.load(f)

    if not history:
        print("尚無執行歷史")
        return

    try:
        run = history[index]
    except IndexError:
        print(f"找不到索引 {index} 的記錄")
        return

    status_icon = "✅" if run['status'] == 'completed' else "❌"

    print("=" * 60)
    print(f"執行詳情 {status_icon}")
    print("=" * 60)
    print(f"日期: {run.get('date', 'N/A')}")
    print(f"開始: {run.get('start_time', 'N/A')}")
    print(f"結束: {run.get('end_time', 'N/A')}")
    print(f"狀態: {run['status']}")
    print("-" * 60)
    print("執行步驟:")

    for step in run.get('steps', []):
        level = step.get('level', 'INFO')
        level_icon = {'INFO': 'ℹ️', 'SUCCESS': '✅', 'WARNING': '⚠️', 'ERROR': '❌'}.get(level, '•')
        print(f"  {level_icon} [{step.get('time', '')}] {step.get('message', '')}")


def main():
    parser = argparse.ArgumentParser(
        description='台指選擇權每日自動化工作流',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  python3 daily_workflow.py                    # 執行今日工作流
  python3 daily_workflow.py --date 20260115    # 執行指定日期
  python3 daily_workflow.py --skip-git         # 跳過 Git 推送
  python3 daily_workflow.py --premarket        # 執行盤前預測（結算日早上）
  python3 daily_workflow.py --logs             # 查看日誌
  python3 daily_workflow.py --history          # 查看執行歷史
  python3 daily_workflow.py --detail           # 查看最近一次執行詳情
  python3 daily_workflow.py --detail -2        # 查看倒數第二次執行詳情
        """
    )

    parser.add_argument('--date', '-d', help='目標日期 (YYYYMMDD)')
    parser.add_argument('--skip-git', action='store_true', help='跳過 Git 推送')
    parser.add_argument('--force', '-f', action='store_true', help='強制重新下載 PDF')
    parser.add_argument('--max-retries', type=int, default=5, help='最大重試次數 (預設: 5)')
    parser.add_argument('--retry-interval', type=int, default=1800, help='重試間隔秒數 (預設: 1800)')
    parser.add_argument('--premarket', '-p', action='store_true', help='執行盤前預測（結算日早上 08:00）')

    # 日誌相關
    parser.add_argument('--logs', '-l', action='store_true', help='查看最近日誌')
    parser.add_argument('--logs-lines', type=int, default=50, help='顯示日誌行數 (預設: 50)')
    parser.add_argument('--history', '-H', action='store_true', help='查看執行歷史')
    parser.add_argument('--history-count', type=int, default=10, help='顯示歷史筆數 (預設: 10)')
    parser.add_argument('--detail', '-D', nargs='?', const=-1, type=int, help='查看執行詳情 (預設: 最近一次)')

    args = parser.parse_args()

    # 查看日誌
    if args.logs:
        view_logs(args.logs_lines)
        return

    # 查看歷史
    if args.history:
        view_history(args.history_count)
        return

    # 查看詳情
    if args.detail is not None:
        view_history_detail(args.detail)
        return

    # 執行工作流
    workflow = DailyWorkflow(
        date=args.date,
        max_retries=args.max_retries,
        retry_interval=args.retry_interval
    )

    # 盤前預測模式
    if args.premarket:
        success = workflow.run_premarket(skip_git=args.skip_git)
    else:
        success = workflow.run(
            skip_git=args.skip_git,
            force=args.force
        )

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
