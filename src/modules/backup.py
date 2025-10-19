"""
データファイルの自動バックアップ機能
"""

from pathlib import Path
from datetime import datetime, timedelta
import shutil
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class BackupManager:
    """データファイルの自動バックアップ管理"""
    
    def __init__(self, data_dir: str = "data", backup_dir: str = "backups", keep_days: int = 30):
        """
        バックアップマネージャーの初期化
        
        Args:
            data_dir: データディレクトリのパス
            backup_dir: バックアップディレクトリのパス
            keep_days: バックアップの保持日数
        """
        self.data_dir = Path(data_dir)
        self.backup_dir = Path(backup_dir)
        self.keep_days = keep_days
        self.backup_dir.mkdir(exist_ok=True)
        
        logger.info(f"BackupManager initialized: data_dir={self.data_dir}, backup_dir={self.backup_dir}, keep_days={self.keep_days}")
    
    def create_backup(self) -> bool:
        """
        データファイルのバックアップを作成
        
        Returns:
            bool: バックアップ作成の成功/失敗
        """
        try:
            if not self.data_dir.exists():
                logger.warning(f"Data directory does not exist: {self.data_dir}")
                return False
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_count = 0
            
            # CSVファイルをバックアップ
            for csv_file in self.data_dir.glob("*.csv"):
                if csv_file.is_file() and csv_file.stat().st_size > 0:  # 空でないファイルのみ
                    backup_file = self.backup_dir / f"{csv_file.stem}_{timestamp}.csv"
                    shutil.copy2(csv_file, backup_file)
                    backup_count += 1
                    logger.info(f"Backed up: {csv_file.name} -> {backup_file.name}")
            
            if backup_count > 0:
                logger.info(f"Backup completed: {backup_count} files backed up")
                return True
            else:
                logger.info("No files to backup")
                return True
                
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            return False
    
    def cleanup_old_backups(self) -> int:
        """
        古いバックアップを削除
        
        Returns:
            int: 削除されたファイル数
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=self.keep_days)
            deleted_count = 0
            
            for backup_file in self.backup_dir.glob("*.csv"):
                if backup_file.is_file():
                    file_mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
                    if file_mtime < cutoff_date:
                        backup_file.unlink()
                        deleted_count += 1
                        logger.info(f"Deleted old backup: {backup_file.name}")
            
            if deleted_count > 0:
                logger.info(f"Cleanup completed: {deleted_count} old backups deleted")
            else:
                logger.info("No old backups to delete")
                
            return deleted_count
            
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")
            return 0
    
    def get_backup_info(self) -> dict:
        """
        バックアップ情報を取得
        
        Returns:
            dict: バックアップの統計情報
        """
        try:
            backup_files = list(self.backup_dir.glob("*.csv"))
            total_size = sum(f.stat().st_size for f in backup_files if f.is_file())
            
            return {
                "backup_count": len(backup_files),
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "backup_dir": str(self.backup_dir),
                "keep_days": self.keep_days
            }
        except Exception as e:
            logger.error(f"Failed to get backup info: {e}")
            return {}
    
    def restore_backup(self, backup_filename: str) -> bool:
        """
        指定されたバックアップから復元
        
        Args:
            backup_filename: 復元するバックアップファイル名
            
        Returns:
            bool: 復元の成功/失敗
        """
        try:
            backup_file = self.backup_dir / backup_filename
            if not backup_file.exists():
                logger.error(f"Backup file not found: {backup_filename}")
                return False
            
            # 元のファイル名を推測（タイムスタンプ部分を除去）
            original_name = backup_filename.split('_')[0] + '.csv'
            target_file = self.data_dir / original_name
            
            shutil.copy2(backup_file, target_file)
            logger.info(f"Restored backup: {backup_filename} -> {original_name}")
            return True
            
        except Exception as e:
            logger.error(f"Backup restore failed: {e}")
            return False
