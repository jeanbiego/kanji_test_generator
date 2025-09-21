"""
エラーハンドリング強化のテスト
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.modules.logger import Logger
from src.modules.error_handler import ErrorHandler, error_handler, safe_execute, validate_input
import logging

class TestErrorHandling:
    """エラーハンドリング強化のテストクラス"""
    
    def setup_method(self):
        """各テストメソッド実行前の準備"""
        self.logger = Logger("test_logger")
        self.error_handler = ErrorHandler()
    
    def test_logger_initialization(self):
        """ロガー初期化テスト"""
        logger = Logger("test_logger")
        assert logger.name == "test_logger"
        assert logger.logger is not None
        assert logger.logger.level == logging.DEBUG
    
    def test_logger_methods(self):
        """ロガーメソッドテスト"""
        with patch.object(self.logger.logger, 'debug') as mock_debug:
            self.logger.debug("デバッグメッセージ")
            mock_debug.assert_called_once_with("デバッグメッセージ")
        
        with patch.object(self.logger.logger, 'info') as mock_info:
            self.logger.info("情報メッセージ")
            mock_info.assert_called_once_with("情報メッセージ")
        
        with patch.object(self.logger.logger, 'warning') as mock_warning:
            self.logger.warning("警告メッセージ")
            mock_warning.assert_called_once_with("警告メッセージ")
        
        with patch.object(self.logger.logger, 'error') as mock_error:
            self.logger.error("エラーメッセージ")
            mock_error.assert_called_once_with("エラーメッセージ")
        
        with patch.object(self.logger.logger, 'critical') as mock_critical:
            self.logger.critical("重大エラーメッセージ")
            mock_critical.assert_called_once_with("重大エラーメッセージ")
    
    def test_error_handler_handle_error(self):
        """エラーハンドラーのエラー処理テスト"""
        with patch('streamlit.error') as mock_st_error:
            with patch('src.modules.error_handler.app_logger') as mock_logger:
                error = Exception("テストエラー")
                ErrorHandler.handle_error(error, "テストコンテキスト")
                
                mock_logger.exception.assert_called_once_with("テストコンテキスト: テストエラー")
                mock_st_error.assert_called_once_with("❌ エラーが発生しました: テストコンテキスト: テストエラー")
    
    def test_error_handler_handle_warning(self):
        """エラーハンドラーの警告処理テスト"""
        with patch('streamlit.warning') as mock_st_warning:
            with patch('src.modules.error_handler.app_logger') as mock_logger:
                ErrorHandler.handle_warning("テスト警告", "テストコンテキスト")
                
                mock_logger.warning.assert_called_once_with("テストコンテキスト: テスト警告")
                mock_st_warning.assert_called_once_with("⚠️ テストコンテキスト: テスト警告")
    
    def test_error_handler_handle_info(self):
        """エラーハンドラーの情報処理テスト"""
        with patch('streamlit.info') as mock_st_info:
            with patch('src.modules.error_handler.app_logger') as mock_logger:
                ErrorHandler.handle_info("テスト情報", "テストコンテキスト")
                
                mock_logger.info.assert_called_once_with("テストコンテキスト: テスト情報")
                mock_st_info.assert_called_once_with("ℹ️ テストコンテキスト: テスト情報")
    
    def test_error_handler_handle_success(self):
        """エラーハンドラーの成功処理テスト"""
        with patch('streamlit.success') as mock_st_success:
            with patch('src.modules.error_handler.app_logger') as mock_logger:
                ErrorHandler.handle_success("テスト成功", "テストコンテキスト")
                
                mock_logger.info.assert_called_once_with("テストコンテキスト: テスト成功")
                mock_st_success.assert_called_once_with("✅ テストコンテキスト: テスト成功")
    
    def test_error_handler_decorator(self):
        """エラーハンドリングデコレータテスト"""
        @error_handler("テストコンテキスト")
        def test_function():
            raise Exception("テストエラー")
        
        with patch('streamlit.error') as mock_st_error:
            with patch('src.modules.error_handler.app_logger') as mock_logger:
                result = test_function()
                
                assert result is None
                mock_logger.exception.assert_called_once()
                mock_st_error.assert_called_once()
    
    def test_error_handler_decorator_success(self):
        """エラーハンドリングデコレータ成功テスト"""
        @error_handler("テストコンテキスト")
        def test_function():
            return "成功"
        
        result = test_function()
        assert result == "成功"
    
    def test_safe_execute_success(self):
        """安全実行成功テスト"""
        def test_function(x, y):
            return x + y
        
        result = safe_execute(test_function, 1, 2, context="テスト")
        assert result == 3
    
    def test_safe_execute_error(self):
        """安全実行エラーテスト"""
        def test_function():
            raise Exception("テストエラー")
        
        with patch('streamlit.error') as mock_st_error:
            with patch('src.modules.error_handler.app_logger') as mock_logger:
                result = safe_execute(test_function, context="テスト")
                
                assert result is None
                mock_logger.exception.assert_called_once()
                mock_st_error.assert_called_once()
    
    def test_validate_input_success(self):
        """入力検証成功テスト"""
        def validation_func(value):
            return value > 0
        
        with patch('streamlit.warning') as mock_st_warning:
            result = validate_input(5, validation_func, "値は正の数である必要があります")
            assert result is True
            mock_st_warning.assert_not_called()
    
    def test_validate_input_failure(self):
        """入力検証失敗テスト"""
        def validation_func(value):
            return value > 0
        
        with patch('streamlit.warning') as mock_st_warning:
            with patch('src.modules.error_handler.app_logger') as mock_logger:
                result = validate_input(-1, validation_func, "値は正の数である必要があります")
                assert result is False
                mock_st_warning.assert_called_once()
                mock_logger.warning.assert_called_once()
    
    def test_validate_input_exception(self):
        """入力検証例外テスト"""
        def validation_func(value):
            raise Exception("検証エラー")
        
        with patch('streamlit.error') as mock_st_error:
            with patch('src.modules.error_handler.app_logger') as mock_logger:
                result = validate_input(5, validation_func, "値は正の数である必要があります")
                assert result is False
                mock_logger.exception.assert_called_once()
                mock_st_error.assert_called_once()
    
    def test_log_operation(self):
        """操作ログ記録テスト"""
        with patch('src.modules.error_handler.app_logger') as mock_logger:
            from src.modules.error_handler import log_operation
            log_operation("テスト操作", "テストコンテキスト")
            mock_logger.info.assert_called_once_with("テストコンテキスト: テスト操作")
    
    def test_error_handler_without_context(self):
        """コンテキストなしエラーハンドリングテスト"""
        with patch('streamlit.error') as mock_st_error:
            with patch('src.modules.error_handler.app_logger') as mock_logger:
                error = Exception("テストエラー")
                ErrorHandler.handle_error(error)
                
                mock_logger.exception.assert_called_once_with("テストエラー")
                mock_st_error.assert_called_once_with("❌ エラーが発生しました: テストエラー")
    
    def test_error_handler_show_to_user_false(self):
        """ユーザー表示なしエラーハンドリングテスト"""
        with patch('streamlit.error') as mock_st_error:
            with patch('src.modules.error_handler.app_logger') as mock_logger:
                error = Exception("テストエラー")
                ErrorHandler.handle_error(error, "テストコンテキスト", show_to_user=False)
                
                mock_logger.exception.assert_called_once_with("テストコンテキスト: テストエラー")
                mock_st_error.assert_not_called()
