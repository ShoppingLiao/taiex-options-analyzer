#!/usr/bin/env python3
"""
台指選擇權每日自動化工作流
- 自動下載 PDF 並產生日報
- 週二/四自動產生結算預報（預測週三/五結算）
- 自動更新首頁並推送到 Git
- 完整日誌記錄
"""

import os
import sys
import time
import subprocess
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import json


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

    def run(self, skip_git: bool = False, force: bool = False):
        """執行完整工作流"""
        self.logger.info("=" * 60)
        self.logger.info(f"開始執行每日工作流")
        self.logger.info(f"目標日期: {self.date} (週{self.weekday_names[self.weekday]})")
        self.logger.info("=" * 60)

        try:
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
        """檢查並產生結算預報"""
        self.logger.info("-" * 40)
        self.logger.info("步驟 3: 檢查結算預報需求")

        # 週二 (1) -> 產生週三結算預報
        # 週四 (3) -> 產生週五結算預報

        if self.weekday == 1:  # 週二
            self.logger.info("今天是週二，產生週三結算預報")
            self._generate_settlement_report('wednesday')
        elif self.weekday == 3:  # 週四
            self.logger.info("今天是週四，產生週五結算預報")
            self._generate_settlement_report('friday')
        else:
            self.logger.info(f"今天是週{self.weekday_names[self.weekday]}，不需要產生結算預報")

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

    def _get_previous_trading_days(self, count: int) -> list:
        """取得前 N 個交易日"""
        trading_days = []
        current = self.date_obj

        while len(trading_days) < count:
            # 週六日不是交易日
            if current.weekday() < 5:
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

    success = workflow.run(
        skip_git=args.skip_git,
        force=args.force
    )

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
