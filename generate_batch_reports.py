#!/usr/bin/env python3
"""
批量生成報告腳本
處理指定日期的 PDF 並生成對應的 HTML 報告
"""

from pathlib import Path
from src.parser import PDFParser
from src.analyzer import OptionsAnalyzer
from src.reporter import ReportGenerator
import sys

def generate_report_for_date(date: str):
    """
    為指定日期生成報告
    
    Args:
        date: 日期字串，格式 YYYYMMDD
    """
    print(f"\n{'='*50}")
    print(f"處理日期: {date}")
    print('='*50)
    
    # 尋找 PDF 檔案
    pdf_dir = Path('data/pdf')
    pdf_files = list(pdf_dir.glob(f'*{date}*.pdf'))
    
    if not pdf_files:
        print(f"❌ 找不到 {date} 的 PDF 檔案")
        return False
    
    pdf_path = pdf_files[0]
    print(f"📄 PDF: {pdf_path.name}")
    
    # 解析 PDF
    print("正在解析 PDF...")
    parser = PDFParser()
    options_list = parser.parse(str(pdf_path))
    
    if not options_list:
        print(f"❌ 無法解析 PDF")
        return False
    
    print(f"✅ 找到 {len(options_list)} 組資料")
    
    # 分析資料
    for options_data in options_list:
        print(f"\n--- {options_data.contract_month} 月份 ---")
        
        analyzer = OptionsAnalyzer()
        analysis = analyzer.analyze(options_data)
        
        print(f"  Max Pain: {analysis.max_pain:,}")
        print(f"  P/C Ratio (OI): {analysis.pc_ratio_oi:.4f}")
        print(f"  買權 OI 壓力: {analysis.max_call_oi_strike:,} ({analysis.max_call_oi:,} 口)")
        print(f"  賣權 OI 支撐: {analysis.max_put_oi_strike:,} ({analysis.max_put_oi:,} 口)")
        
        # 生成報告
        reporter = ReportGenerator()
        output_path = reporter.generate(analysis, options_data)
        
        print(f"📊 報告已產生: {output_path}")
    
    return True

def main():
    """主函數"""
    # 要處理的日期列表
    dates = ['20260105', '20260106', '20260107', '20260108']
    
    # 如果命令列有參數，使用命令列參數
    if len(sys.argv) > 1:
        dates = sys.argv[1:]
    
    print("="*50)
    print("台指選擇權批量報告生成器")
    print("="*50)
    print(f"將處理以下日期: {', '.join(dates)}")
    
    success_count = 0
    fail_count = 0
    
    for date in dates:
        if generate_report_for_date(date):
            success_count += 1
        else:
            fail_count += 1
    
    print("\n" + "="*50)
    print("批量處理完成")
    print("="*50)
    print(f"✅ 成功: {success_count}")
    print(f"❌ 失敗: {fail_count}")
    print(f"📁 報告位置: reports/")

if __name__ == "__main__":
    main()
