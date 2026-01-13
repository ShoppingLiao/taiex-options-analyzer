#!/usr/bin/env python3
"""
同步 reports/ 到 docs/ 的工具腳本

用途:
    將 reports/ 目錄中的 HTML 報告同步到 docs/ 目錄
    用於 GitHub Pages 部署前的準備

使用方式:
    python sync_to_docs.py              # 同步所有 HTML 檔案
    python sync_to_docs.py --dry-run    # 預覽要同步的檔案（不實際複製）
    python sync_to_docs.py --force      # 強制覆蓋所有檔案
"""

import shutil
import argparse
from pathlib import Path
from datetime import datetime
import hashlib


def get_file_hash(file_path):
    """計算檔案的 MD5 雜湊值"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def should_sync(src_file, dst_file, force=False):
    """判斷檔案是否需要同步"""
    if force:
        return True, "強制同步"
    
    if not dst_file.exists():
        return True, "目標檔案不存在"
    
    # 比較檔案雜湊值
    src_hash = get_file_hash(src_file)
    dst_hash = get_file_hash(dst_file)
    
    if src_hash != dst_hash:
        return True, "檔案內容不同"
    
    return False, "檔案相同，跳過"


def sync_reports(dry_run=False, force=False, verbose=False):
    """同步 reports/ 到 docs/"""
    
    project_root = Path(__file__).parent
    reports_dir = project_root / "reports"
    docs_dir = project_root / "docs"
    
    # 確認目錄存在
    if not reports_dir.exists():
        print(f"❌ 錯誤: reports/ 目錄不存在")
        return False
    
    if not docs_dir.exists():
        print(f"⚠️  警告: docs/ 目錄不存在，正在創建...")
        docs_dir.mkdir(parents=True, exist_ok=True)
    
    # 找出所有 HTML 檔案
    html_files = sorted(reports_dir.glob("*.html"))
    
    if not html_files:
        print("⚠️  reports/ 目錄中沒有 HTML 檔案")
        return False
    
    print("=" * 60)
    print(f"📊 同步報告: reports/ → docs/")
    print("=" * 60)
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"來源: {reports_dir}")
    print(f"目標: {docs_dir}")
    print(f"模式: {'🔍 預覽模式' if dry_run else '✅ 執行模式'}")
    if force:
        print("⚡ 強制覆蓋模式")
    print("=" * 60)
    print()
    
    synced_count = 0
    skipped_count = 0
    
    for src_file in html_files:
        dst_file = docs_dir / src_file.name
        
        # 判斷是否需要同步
        need_sync, reason = should_sync(src_file, dst_file, force)
        
        if need_sync:
            status = "🔄 同步"
            if dry_run:
                print(f"{status} [{reason}]: {src_file.name}")
                if verbose:
                    print(f"   來源: {src_file.stat().st_size:,} bytes, {datetime.fromtimestamp(src_file.stat().st_mtime):%Y-%m-%d %H:%M:%S}")
                    if dst_file.exists():
                        print(f"   目標: {dst_file.stat().st_size:,} bytes, {datetime.fromtimestamp(dst_file.stat().st_mtime):%Y-%m-%d %H:%M:%S}")
            else:
                try:
                    shutil.copy2(src_file, dst_file)
                    print(f"{status} [{reason}]: {src_file.name}")
                    if verbose:
                        print(f"   ✓ 已複製 {src_file.stat().st_size:,} bytes")
                except Exception as e:
                    print(f"❌ 錯誤 [{src_file.name}]: {e}")
                    continue
            
            synced_count += 1
        else:
            if verbose:
                print(f"⏭️  跳過 [{reason}]: {src_file.name}")
            skipped_count += 1
    
    print()
    print("=" * 60)
    print("📈 同步統計")
    print("=" * 60)
    print(f"總檔案數: {len(html_files)}")
    print(f"已同步: {synced_count}")
    print(f"跳過: {skipped_count}")
    
    if dry_run:
        print()
        print("💡 這是預覽模式，沒有實際複製檔案")
        print("   移除 --dry-run 參數以執行實際同步")
    else:
        print()
        print("✅ 同步完成！")
        print()
        print("📝 下一步:")
        print("   1. 檢查 docs/ 目錄內容")
        print("   2. git add docs/")
        print("   3. git commit -m 'sync: 更新報告到 docs/'")
        print("   4. git push")
    
    print("=" * 60)
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='同步 reports/ 到 docs/ 的工具腳本',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
範例:
  python sync_to_docs.py              同步所有有變更的檔案
  python sync_to_docs.py --dry-run    預覽要同步的檔案（不實際複製）
  python sync_to_docs.py --force      強制覆蓋所有檔案
  python sync_to_docs.py -v           顯示詳細資訊
        '''
    )
    
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='預覽模式，不實際複製檔案'
    )
    
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='強制覆蓋所有檔案，即使內容相同'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='顯示詳細資訊'
    )
    
    args = parser.parse_args()
    
    try:
        success = sync_reports(
            dry_run=args.dry_run,
            force=args.force,
            verbose=args.verbose
        )
        
        if not success:
            exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  已取消操作")
        exit(1)
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
