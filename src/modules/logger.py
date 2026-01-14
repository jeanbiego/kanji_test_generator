"""
ログ機能
"""

import logging
import os
from datetime import datetime
from pathlib import Path


class Logger:
    """ログ機能の管理"""

    def __init__(self, name: str, log_dir: str = "logs"):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """ロガーの設定"""
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.DEBUG)

        # 既存のハンドラーをクリア
        logger.handlers.clear()

        # フォーマッターの設定
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        # ファイルハンドラーの設定
        log_file = self.log_dir / f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # エラーログ用のファイルハンドラー
        error_log_file = self.log_dir / f"{self.name}_error_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = logging.FileHandler(error_log_file, encoding="utf-8")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)

        # コンソールハンドラーの設定（開発時のみ）
        if os.getenv("STREAMLIT_DEBUG", "false").lower() == "true":
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        return logger

    def debug(self, message: str, **kwargs):
        """デバッグログ"""
        self.logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs):
        """情報ログ"""
        self.logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs):
        """警告ログ"""
        self.logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs):
        """エラーログ"""
        self.logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs):
        """重大エラーログ"""
        self.logger.critical(message, **kwargs)

    def exception(self, message: str, **kwargs):
        """例外ログ(スタックトレース付き)"""
        self.logger.exception(message, **kwargs)


# グローバルロガーインスタンス
app_logger = Logger("kanji_test_generator")
