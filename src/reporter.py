"""
報告產生模組
產生 HTML 格式的選擇權分析報告
"""

import json
from datetime import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict

from .analyzer import AnalysisResult
from .parser import OptionsData
from .settlement_analyzer import SettlementAnalyzer, SettlementAnalysis
from .ai_settlement_analysis import AISettlementAnalyzer
from .ai_daily_analyzer import AIDailyAnalyzer
from .ai_prediction_generator import AIPredictionGenerator
from .ai_review_analyzer import AIReviewAnalyzer
from .ai_learning_system import AILearningSystem


def get_weekday_chinese(date_str: str) -> str:
    """
    將日期字串轉換為中文星期
    
    Args:
        date_str: 日期字串，格式 YYYYMMDD
        
    Returns:
        中文星期，例如 "一"
    """
    try:
        date_obj = datetime.strptime(date_str, '%Y%m%d')
        weekdays = ['一', '二', '三', '四', '五', '六', '日']
        return weekdays[date_obj.weekday()]
    except:
        return ""


def format_date_with_weekday(date_str: str) -> str:
    """
    格式化日期並加上星期
    
    Args:
        date_str: 日期字串，格式 YYYYMMDD
        
    Returns:
        格式化的日期，例如 "2026/01/09 (一)"
    """
    try:
        date_obj = datetime.strptime(date_str, '%Y%m%d')
        weekday = get_weekday_chinese(date_str)
        return f"{date_obj.strftime('%Y/%m/%d')} ({weekday})"
    except:
        return date_str


class ReportGenerator:
    """HTML 報告產生器"""

    def __init__(self, template_dir: str = None, output_dir: str = None):
        """
        初始化報告產生器

        Args:
            template_dir: 模板目錄
            output_dir: 報告輸出目錄
        """
        project_root = Path(__file__).parent.parent

        if template_dir is None:
            template_dir = project_root / "templates"
        if output_dir is None:
            output_dir = project_root / "reports"

        self.template_dir = Path(template_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 設定 Jinja2 環境
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True
        )
        
        # 初始化結算情境分析器
        self.settlement_analyzer = SettlementAnalyzer()
        
        # 初始化 AI 分析器
        self.ai_analyzer = AISettlementAnalyzer()
        
        # 初始化每日 AI 交易員分析器
        self.daily_ai_analyzer = AIDailyAnalyzer()
        
        # 初始化 AI 學習系統
        self.ai_learning_system = AILearningSystem()
        self.prediction_generator = AIPredictionGenerator(self.ai_learning_system)
        self.review_analyzer = AIReviewAnalyzer(self.ai_learning_system, self.prediction_generator)

    def generate(
        self,
        analysis_result: AnalysisResult,
        options_data: OptionsData,
        filename: str = None
    ) -> str:
        """
        產生 HTML 報告

        Args:
            analysis_result: 分析結果
            options_data: 原始選擇權資料
            filename: 輸出檔名 (不含副檔名)

        Returns:
            產生的報告檔案路徑
        """
        if filename is None:
            filename = f"report_{analysis_result.date}_{analysis_result.contract_month}"

        # 進行結算情境分析
        settlement_analysis = self.settlement_analyzer.analyze_settlement_scenarios(options_data)
        
        # 進行 AI 深度分析
        ai_analysis = self.ai_analyzer.analyze_20260109_data(options_data)
        
        # 計算市場情緒（用於 AI 每日分析）
        sentiment = self._calculate_sentiment(analysis_result.pc_ratio_oi)
        
        # 進行每日 AI 交易員分析
        daily_ai_analysis = self.daily_ai_analyzer.analyze(analysis_result, options_data, sentiment)
        
        # 載入預測和檢討數據
        current_date = analysis_result.date
        prediction = self.prediction_generator.load_prediction(current_date)
        review = self.review_analyzer.load_review(current_date)

        # 準備模板資料
        template_data = self._prepare_template_data(
            analysis_result, options_data, settlement_analysis, ai_analysis, 
            daily_ai_analysis, prediction, review
        )

        # 載入並渲染模板
        template = self.env.get_template("report.html")
        html_content = template.render(**template_data)

        # 寫入檔案
        output_path = self.output_dir / f"{filename}.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"報告已產生: {output_path}")
        return str(output_path)

    def _prepare_template_data(
        self,
        result: AnalysisResult,
        options_data: OptionsData,
        settlement_analysis: SettlementAnalysis = None,
        ai_analysis: Dict = None,
        daily_ai_analysis: Dict = None,
        prediction: Dict = None,
        review: Dict = None
    ) -> dict:
        """
        準備模板所需的資料
        """
        # 市場情緒解讀
        sentiment_map = {
            'extremely_bullish': '極度樂觀',
            'bullish': '偏多',
            'neutral': '中性',
            'bearish': '偏空',
            'extremely_bearish': '極度悲觀',
        }

        pc_ratio = result.pc_ratio_oi
        sentiment = self._calculate_sentiment(pc_ratio)

        # 準備圖表資料
        oi_chart_data = {
            'strikes': options_data.strike_prices,
            'call_oi': options_data.call_oi,
            'put_oi': options_data.put_oi,
            'call_oi_change': options_data.call_oi_change,
            'put_oi_change': options_data.put_oi_change,
        }

        # 準備表格資料
        data_rows = []
        for i, strike in enumerate(options_data.strike_prices):
            data_rows.append({
                'strike': strike,
                'call_volume': options_data.call_volume[i],
                'call_oi': options_data.call_oi[i],
                'call_oi_change': options_data.call_oi_change[i],
                'put_volume': options_data.put_volume[i],
                'put_oi': options_data.put_oi[i],
                'put_oi_change': options_data.put_oi_change[i],
            })

        # 產生市場解讀分析項目
        analysis_items = self._generate_analysis_items(result, sentiment)
        
        # 準備結算情境資料
        settlement_scenarios = []
        if settlement_analysis:
            for scenario in settlement_analysis.scenarios:
                settlement_scenarios.append({
                    'name': scenario.name,
                    'probability': scenario.probability,
                    'settlement_range': f"{scenario.settlement_range[0]:,} ~ {scenario.settlement_range[1]:,}",
                    'conditions': scenario.conditions,
                    'description': scenario.description,
                    'impact': scenario.impact,
                    'key_levels': [f"{k:,}" for k in scenario.key_levels]
                })

        return {
            # 基本資訊
            'date': result.date,
            'date_with_weekday': format_date_with_weekday(result.date),
            'contract_month': result.contract_month,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            
            # 契約資訊
            'page_title': options_data.page_title or '',
            'contract_code': options_data.contract_code or '',
            'settlement_date': options_data.settlement_date or '',

            # 關鍵指標
            'max_pain': result.max_pain,
            'pc_ratio_oi': result.pc_ratio_oi,
            'pc_ratio_volume': result.pc_ratio_volume,
            'market_sentiment': sentiment_map.get(sentiment, '未知'),

            # OI 統計
            'total_call_oi': result.total_call_oi,
            'total_put_oi': result.total_put_oi,
            'call_oi_change': result.call_oi_change,
            'put_oi_change': result.put_oi_change,

            # 關鍵價位
            'max_call_oi_strike': result.max_call_oi_strike,
            'max_put_oi_strike': result.max_put_oi_strike,
            'max_call_oi': result.max_call_oi,
            'max_put_oi': result.max_put_oi,
            'call_resistance': result.call_resistance,
            'put_support': result.put_support,

            # 圖表資料
            'oi_chart_data': json.dumps(oi_chart_data),

            # 表格資料
            'data_rows': data_rows,

            # 市場解讀
            'analysis_items': analysis_items,
            
            # 結算情境分析
            'settlement_scenarios': settlement_scenarios,
            'dealer_position': settlement_analysis.dealer_position if settlement_analysis else '',
            'market_bias': settlement_analysis.market_bias if settlement_analysis else '',
            
            # AI 深度分析
            'ai_analysis': ai_analysis if ai_analysis else {},
            
            # 每日 AI 交易員分析
            'daily_ai_analysis': daily_ai_analysis if daily_ai_analysis else {},
            
            # AI 預測與檢討
            'prediction': prediction if prediction else None,
            'review': review if review else None,
            
            # 台指期貨基本資料
            'tx_data': {
                'open': options_data.tx_open or 0,
                'high': options_data.tx_high or 0,
                'low': options_data.tx_low or 0,
                'close': options_data.tx_close or 0,
                # 成交量和結算價目前無法從外部 API 獲取
                # 顯示為 None 以便模板區分「無數據」和「數值為0」
                'volume': options_data.tx_volume if options_data.tx_volume is not None else None,
                'settlement': options_data.tx_settlement if options_data.tx_settlement is not None else None,
            },
        }

    def _generate_analysis_items(self, result: AnalysisResult, sentiment: str) -> list:
        """
        產生市場解讀分析項目
        """
        items = []

        # P/C Ratio 分析
        if result.pc_ratio_oi < 0.7:
            items.append({
                'icon': '▲',
                'icon_class': 'icon-bullish',
                'text': f'P/C Ratio {result.pc_ratio_oi:.4f} 極低，市場極度樂觀，需注意過熱風險'
            })
        elif result.pc_ratio_oi < 0.9:
            items.append({
                'icon': '▲',
                'icon_class': 'icon-bullish',
                'text': f'P/C Ratio {result.pc_ratio_oi:.4f} < 1，市場偏多，買權佈局積極'
            })
        elif result.pc_ratio_oi < 1.1:
            items.append({
                'icon': '●',
                'icon_class': 'icon-neutral',
                'text': f'P/C Ratio {result.pc_ratio_oi:.4f} 接近 1，市場觀望，多空勢均力敵'
            })
        elif result.pc_ratio_oi < 1.3:
            items.append({
                'icon': '▼',
                'icon_class': 'icon-bearish',
                'text': f'P/C Ratio {result.pc_ratio_oi:.4f} > 1，市場偏空，賣權避險增加'
            })
        else:
            items.append({
                'icon': '▼',
                'icon_class': 'icon-bearish',
                'text': f'P/C Ratio {result.pc_ratio_oi:.4f} 極高，市場極度悲觀，可能出現反彈契機'
            })

        # 支撐壓力分析
        if result.max_put_oi_strike < result.max_call_oi_strike:
            items.append({
                'icon': '◆',
                'icon_class': 'icon-neutral',
                'text': f'下檔支撐 {result.max_put_oi_strike:,}，上檔壓力 {result.max_call_oi_strike:,}，區間震盪格局'
            })

        # Max Pain 分析
        items.append({
            'icon': '★',
            'icon_class': 'icon-neutral',
            'text': f'Max Pain {result.max_pain:,}，結算日價格可能向此收斂'
        })

        # OI 變化分析
        if result.call_oi_change > 0 and result.put_oi_change > 0:
            items.append({
                'icon': '●',
                'icon_class': 'icon-neutral',
                'text': f'買賣權 OI 同步增加 (Call +{result.call_oi_change:,}, Put +{result.put_oi_change:,})，籌碼持續堆積'
            })
        elif result.call_oi_change > 0 and result.put_oi_change < 0:
            items.append({
                'icon': '▲',
                'icon_class': 'icon-bullish',
                'text': f'買權增倉 +{result.call_oi_change:,}，賣權減倉 {result.put_oi_change:,}，多方積極佈局'
            })
        elif result.call_oi_change < 0 and result.put_oi_change > 0:
            items.append({
                'icon': '▼',
                'icon_class': 'icon-bearish',
                'text': f'買權減倉 {result.call_oi_change:,}，賣權增倉 +{result.put_oi_change:,}，空方避險增加'
            })

        # 壓力支撐區域
        resistance_str = ', '.join([f'{s:,}' for s in result.call_resistance[:3]])
        support_str = ', '.join([f'{s:,}' for s in result.put_support[:3]])
        items.append({
            'icon': '◎',
            'icon_class': 'icon-neutral',
            'text': f'壓力區: {resistance_str} | 支撐區: {support_str}'
        })

        return items

    def generate_multi_contract_report(
        self,
        options_list: List[OptionsData],
        analyzer
    ) -> str:
        """
        產生包含多個契約類型的綜合報告
        
        Args:
            options_list: 所有契約的資料列表 (週選+月選)
            analyzer: 分析器實例
            
        Returns:
            報告檔案路徑
        """
        if not options_list:
            raise ValueError("options_list 不能為空")
        
        # 使用第一個契約作為主契約（通常是週三選擇權）
        main_options = options_list[0]
        main_result = analyzer.analyze(main_options)
        
        # 準備所有契約的資料
        all_contracts_data = []
        for options_data in options_list:
            result = analyzer.analyze(options_data)
            
            # 準備每個契約的表格數據
            data_rows = []
            for i in range(len(options_data.strike_prices)):
                data_rows.append({
                    'strike': options_data.strike_prices[i],
                    'call_oi': options_data.call_oi[i],
                    'call_oi_change': options_data.call_oi_change[i],
                    'put_oi': options_data.put_oi[i],
                    'put_oi_change': options_data.put_oi_change[i],
                })
            
            # 找到最接近收盤價的履約價（用於反黃標示）
            close_price = options_data.tx_close
            closest_strike = min(options_data.strike_prices, 
                               key=lambda x: abs(x - close_price))
            
            all_contracts_data.append({
                'contract_code': options_data.contract_code or options_data.contract_month,
                'contract_type': options_data.contract_type or 'unknown',
                'page_title': options_data.page_title or '選擇權OI變化',
                'settlement_date': options_data.settlement_date or '',
                'data_rows': data_rows,
                'max_pain': result.max_pain,
                'pc_ratio_oi': result.pc_ratio_oi,
                'max_call_oi_strike': result.max_call_oi_strike,
                'max_put_oi_strike': result.max_put_oi_strike,
                'close_price': close_price,
                'closest_strike': closest_strike,
            })
        
        # 檔案名使用主契約的日期
        filename = f"report_{main_result.date}_{main_options.contract_code}"
        
        # 進行結算情境分析（使用主契約）
        settlement_analysis = self.settlement_analyzer.analyze_settlement_scenarios(main_options)
        
        # 進行 AI 深度分析（使用主契約）
        ai_analysis = self.ai_analyzer.analyze_20260109_data(main_options)
        
        # 計算市場情緒
        sentiment = self._calculate_sentiment(main_result.pc_ratio_oi)
        
        # 進行每日 AI 交易員分析（使用主契約）
        daily_ai_analysis = self.daily_ai_analyzer.analyze(main_result, main_options, sentiment)
        
        # 載入預測和檢討數據
        current_date = main_result.date
        prediction = self.prediction_generator.load_prediction(current_date)
        review = self.review_analyzer.load_review(current_date)
        
        # 準備模板資料（基於主契約）
        template_data = self._prepare_template_data(
            main_result, main_options, settlement_analysis, ai_analysis,
            daily_ai_analysis, prediction, review
        )
        
        # 添加多契約資料
        template_data['all_contracts'] = all_contracts_data
        template_data['is_multi_contract'] = True
        
        # 載入並渲染模板
        template = self.env.get_template("report.html")
        html_content = template.render(**template_data)
        
        # 寫入檔案
        output_path = self.output_dir / f"{filename}.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # 複製到 docs 目錄
        docs_path = self.output_dir.parent / "docs" / f"{filename}.html"
        with open(docs_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"綜合報告已產生: {output_path}")
        return str(output_path)

    def generate_summary_report(
        self,
        results: List[Tuple[AnalysisResult, OptionsData]],
        filename: str = None
    ) -> str:
        """
        產生多月份的摘要報告

        Args:
            results: (分析結果, 原始資料) 的清單
            filename: 輸出檔名

        Returns:
            報告檔案路徑
        """
        if not results:
            raise ValueError("沒有可產生報告的資料")

        # 使用第一筆的日期作為報告日期
        date = results[0][0].date

        if filename is None:
            filename = f"summary_{date}"

        # 產生簡易的 HTML 報告
        html_parts = [
            '<!DOCTYPE html>',
            '<html lang="zh-TW">',
            '<head>',
            '<meta charset="UTF-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
            f'<title>台指選擇權摘要報告 - {date}</title>',
            '<style>',
            'body { font-family: sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }',
            'table { width: 100%; border-collapse: collapse; margin: 20px 0; }',
            'th, td { padding: 10px; text-align: right; border: 1px solid #ddd; }',
            'th { background-color: #f5f5f5; }',
            '.positive { color: green; }',
            '.negative { color: red; }',
            '</style>',
            '</head>',
            '<body>',
            f'<h1>台指選擇權摘要報告</h1>',
            f'<p>交易日期: {date}</p>',
            '<table>',
            '<thead><tr>',
            '<th>契約月份</th>',
            '<th>Max Pain</th>',
            '<th>P/C Ratio</th>',
            '<th>買權 OI</th>',
            '<th>賣權 OI</th>',
            '<th>壓力價</th>',
            '<th>支撐價</th>',
            '</tr></thead>',
            '<tbody>',
        ]

        for result, _ in results:
            html_parts.append('<tr>')
            html_parts.append(f'<td>{result.contract_month}</td>')
            html_parts.append(f'<td>{result.max_pain:,}</td>')
            html_parts.append(f'<td>{result.pc_ratio_oi:.4f}</td>')
            html_parts.append(f'<td>{result.total_call_oi:,}</td>')
            html_parts.append(f'<td>{result.total_put_oi:,}</td>')
            html_parts.append(f'<td>{result.max_call_oi_strike:,}</td>')
            html_parts.append(f'<td>{result.max_put_oi_strike:,}</td>')
            html_parts.append('</tr>')

        html_parts.extend([
            '</tbody>',
            '</table>',
            f'<p>報告產生時間: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>',
            '</body>',
            '</html>',
        ])

        output_path = self.output_dir / f"{filename}.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(html_parts))

        print(f"摘要報告已產生: {output_path}")
        return str(output_path)
    
    def _calculate_sentiment(self, pc_ratio: float) -> str:
        """計算市場情緒"""
        if pc_ratio < 0.7:
            return 'extremely_bullish'
        elif pc_ratio < 0.9:
            return 'bullish'
        elif pc_ratio < 1.1:
            return 'neutral'
        elif pc_ratio < 1.3:
            return 'bearish'
        else:
            return 'extremely_bearish'


if __name__ == "__main__":
    # 測試報告產生
    from .parser import PDFParser
    from .analyzer import OptionsAnalyzer
    from pathlib import Path
    import sys

    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        project_root = Path(__file__).parent.parent
        pdf_dir = project_root / "data" / "pdf"
        pdf_files = list(pdf_dir.glob("*.pdf"))

        if pdf_files:
            pdf_path = str(pdf_files[0])
        else:
            print("請提供 PDF 檔案路徑或將 PDF 放入 data/pdf 目錄")
            sys.exit(1)

    print(f"處理檔案: {pdf_path}")

    parser = PDFParser()
    analyzer = OptionsAnalyzer()
    reporter = ReportGenerator()

    try:
        options_list = parser.parse(pdf_path)

        for options_data in options_list:
            result = analyzer.analyze(options_data)
            report_path = reporter.generate(result, options_data)
            print(f"報告: {report_path}")

    except Exception as e:
        print(f"產生報告失敗: {e}")
        import traceback
        traceback.print_exc()
