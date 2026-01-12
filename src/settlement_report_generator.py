"""
結算日報告生成器
將結算日預測分析結果生成 HTML 報告
"""

from pathlib import Path
from datetime import datetime
from jinja2 import Template
from typing import List
from .settlement_predictor import SettlementPrediction, TrendSignal, Scenario


class SettlementReportGenerator:
    """結算日報告生成器"""
    
    def __init__(self):
        self.template_dir = Path('templates')
        self.output_dir = Path('reports')
        self.docs_dir = Path('docs')
        
        # 確保輸出目錄存在
        self.output_dir.mkdir(exist_ok=True)
        self.docs_dir.mkdir(exist_ok=True)
    
    def generate_report(
        self,
        prediction: SettlementPrediction,
        output_filename: str = None
    ) -> Path:
        """
        生成結算日預測報告
        
        Args:
            prediction: 結算預測結果
            output_filename: 輸出檔名（可選）
            
        Returns:
            Path: 報告檔案路徑
        """
        # 載入模板
        template_path = self.template_dir / 'settlement_report.html'
        
        if not template_path.exists():
            raise FileNotFoundError(f"找不到模板: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template = Template(f.read())
        
        # 準備模板數據
        template_data = self._prepare_template_data(prediction)
        
        # 渲染 HTML
        html_content = template.render(**template_data)
        
        # 決定輸出檔名
        if not output_filename:
            # 格式: settlement_20260107_wed.html 或 settlement_20260109_fri.html
            date_str = prediction.settlement_date.replace('/', '')
            weekday_abbr = 'wed' if prediction.settlement_weekday == 'wednesday' else 'fri'
            output_filename = f'settlement_{date_str}_{weekday_abbr}.html'
        
        # 寫入檔案（同時寫入 reports 和 docs）
        reports_path = self.output_dir / output_filename
        docs_path = self.docs_dir / output_filename
        
        with open(reports_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        with open(docs_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return docs_path
    
    def _prepare_template_data(self, prediction: SettlementPrediction) -> dict:
        """準備模板數據"""
        
        # 基本資訊
        weekday_text = '週三' if prediction.settlement_weekday == 'wednesday' else '週五'
        analysis_dates_text = self._format_analysis_dates(prediction.analysis_dates)
        
        # 趨勢強度星星
        strength_stars = '⭐' * prediction.trend_strength
        
        # 趨勢訊號
        trend_signals = self._format_trend_signals(prediction.trend_signals)
        
        # 結算劇本
        scenarios = self._format_scenarios(prediction.scenarios)
        
        # 關鍵指標
        key_metrics = self._format_key_metrics(prediction.key_metrics)
        
        return {
            # Header
            'settlement_date': prediction.settlement_date,
            'settlement_weekday_text': weekday_text,
            'analysis_dates_text': analysis_dates_text,
            'generated_time': datetime.now().strftime('%Y/%m/%d %H:%M'),
            
            # Trend Overview
            'overall_trend': prediction.overall_trend,
            'overall_trend_text': prediction.overall_trend_text,
            'trend_strength': prediction.trend_strength,
            'strength_stars': strength_stars,
            
            # Predicted Range
            'predicted_lower': f'{prediction.predicted_range[0]:,}',
            'predicted_upper': f'{prediction.predicted_range[1]:,}',
            'current_price': f'{prediction.current_price:,}',
            
            # Trend Signals
            'trend_signals': trend_signals,
            
            # Scenarios
            'scenarios': scenarios,
            
            # Key Metrics
            'key_metrics': key_metrics,
            
            # Risks
            'risks': prediction.risks,
        }
    
    def _format_analysis_dates(self, dates: List[str]) -> str:
        """格式化分析日期"""
        if not dates:
            return '無'
        
        # 將 YYYYMMDD 轉換為 MM/DD
        formatted = []
        for date_str in dates:
            try:
                date_obj = datetime.strptime(date_str, '%Y%m%d')
                formatted.append(date_obj.strftime('%m/%d'))
            except:
                formatted.append(date_str)
        
        return '、'.join(formatted)
    
    def _format_trend_signals(self, signals: List[TrendSignal]) -> List[dict]:
        """格式化趨勢訊號"""
        formatted = []
        
        for signal in signals:
            # 方向文字與圖示
            if signal.direction == 'bullish':
                direction_text = '多頭訊號'
                direction_icon = '📈'
            elif signal.direction == 'bearish':
                direction_text = '空頭訊號'
                direction_icon = '📉'
            else:
                direction_text = '中性訊號'
                direction_icon = '➖'
            
            formatted.append({
                'direction': signal.direction,
                'direction_text': direction_text,
                'direction_icon': direction_icon,
                'strength': signal.strength,
                'indicators': signal.indicators,
                'description': signal.description,
            })
        
        return formatted
    
    def _format_scenarios(self, scenarios: List[Scenario]) -> List[dict]:
        """格式化結算劇本"""
        formatted = []
        
        for scenario in scenarios:
            formatted.append({
                'name': scenario.name,
                'icon': scenario.icon,
                'probability': f'{scenario.probability:.1f}',
                'range_lower': f'{scenario.price_range[0]:,}',
                'range_upper': f'{scenario.price_range[1]:,}',
                'key_levels': [f'{level:,}' for level in scenario.key_levels],
                'conditions': scenario.conditions,
                'strategy': scenario.strategy,
                'color': scenario.color,
            })
        
        return formatted
    
    def _format_key_metrics(self, metrics: dict) -> List[dict]:
        """格式化關鍵指標"""
        formatted = []
        
        # Max Pain
        if 'max_pain' in metrics and metrics['max_pain']:
            formatted.append({
                'label': 'Max Pain',
                'value': f'{metrics["max_pain"]:,}',
                'change': None,
                'change_class': '',
            })
        
        # P/C Ratio
        if 'latest_pc_ratio' in metrics:
            pc_change = ''
            pc_change_class = ''
            
            if 'avg_pc_ratio' in metrics:
                avg_pc = metrics['avg_pc_ratio']
                latest_pc = metrics['latest_pc_ratio']
                diff = latest_pc - avg_pc
                
                if abs(diff) > 0.05:
                    pc_change = f'{diff:+.2f}'
                    pc_change_class = 'positive' if diff > 0 else 'negative'
            
            formatted.append({
                'label': 'P/C Ratio',
                'value': f'{metrics["latest_pc_ratio"]:.2f}',
                'change': pc_change,
                'change_class': pc_change_class,
            })
        
        # 買權 OI
        if 'total_call_oi' in metrics:
            call_change = ''
            call_change_class = ''
            
            if 'avg_call_oi_change' in metrics:
                change = metrics['avg_call_oi_change']
                if abs(change) > 1000:
                    call_change = f'{int(change):+,}'
                    call_change_class = 'positive' if change > 0 else 'negative'
            
            formatted.append({
                'label': '買權 OI',
                'value': f'{metrics["total_call_oi"]:,}',
                'change': call_change,
                'change_class': call_change_class,
            })
        
        # 賣權 OI
        if 'total_put_oi' in metrics:
            put_change = ''
            put_change_class = ''
            
            if 'avg_put_oi_change' in metrics:
                change = metrics['avg_put_oi_change']
                if abs(change) > 1000:
                    put_change = f'{int(change):+,}'
                    put_change_class = 'positive' if change > 0 else 'negative'
            
            formatted.append({
                'label': '賣權 OI',
                'value': f'{metrics["total_put_oi"]:,}',
                'change': put_change,
                'change_class': put_change_class,
            })
        
        # 當前價格
        if 'current_price' in metrics and metrics['current_price']:
            formatted.append({
                'label': '當前價格',
                'value': f'{metrics["current_price"]:,}',
                'change': None,
                'change_class': '',
            })
        
        return formatted


# 測試程式碼
if __name__ == '__main__':
    from src.settlement_predictor import SettlementPredictor
    
    # 創建預測器
    predictor = SettlementPredictor()
    
    # 預測週三結算（使用週一二數據）
    prediction = predictor.predict_settlement(
        dates=['20260105', '20260106'],
        settlement_date='2026/01/07',
        settlement_weekday='wednesday'
    )
    
    # 生成報告
    generator = SettlementReportGenerator()
    report_path = generator.generate_report(prediction)
    
    print(f'\n✅ 結算日報告已生成: {report_path}')
    print(f'   結算日期: {prediction.settlement_date}')
    print(f'   整體趨勢: {prediction.overall_trend_text}')
    print(f'   預測區間: {prediction.predicted_range[0]:,} ~ {prediction.predicted_range[1]:,}')
