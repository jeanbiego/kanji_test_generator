"""
エラーハンドリング機能
"""

import streamlit as st
from typing import Optional, Callable, Any
from functools import wraps
from .logger import app_logger

class ErrorHandler:
    """エラーハンドリングの管理"""
    
    @staticmethod
    def handle_error(error: Exception, context: str = "", show_to_user: bool = True) -> None:
        """
        エラーの処理
        
        Args:
            error: 発生した例外
            context: エラーが発生したコンテキスト
            show_to_user: ユーザーにエラーを表示するかどうか
        """
        error_message = f"{context}: {str(error)}" if context else str(error)
        
        # ログに記録
        app_logger.exception(error_message)
        
        # ユーザーに表示
        if show_to_user:
            st.error(f"❌ エラーが発生しました: {error_message}")
    
    @staticmethod
    def handle_warning(message: str, context: str = "") -> None:
        """
        警告の処理
        
        Args:
            message: 警告メッセージ
            context: 警告が発生したコンテキスト
        """
        warning_message = f"{context}: {message}" if context else message
        
        # ログに記録
        app_logger.warning(warning_message)
        
        # ユーザーに表示
        st.warning(f"⚠️ {warning_message}")
    
    @staticmethod
    def handle_info(message: str, context: str = "") -> None:
        """
        情報の処理
        
        Args:
            message: 情報メッセージ
            context: 情報が発生したコンテキスト
        """
        info_message = f"{context}: {message}" if context else message
        
        # ログに記録
        app_logger.info(info_message)
        
        # ユーザーに表示
        st.info(f"ℹ️ {info_message}")
    
    @staticmethod
    def handle_success(message: str, context: str = "") -> None:
        """
        成功の処理
        
        Args:
            message: 成功メッセージ
            context: 成功が発生したコンテキスト
        """
        success_message = f"{context}: {message}" if context else message
        
        # ログに記録
        app_logger.info(success_message)
        
        # ユーザーに表示
        st.success(f"✅ {success_message}")

def error_handler(context: str = "", show_to_user: bool = True):
    """
    エラーハンドリングデコレータ
    
    Args:
        context: エラーが発生したコンテキスト
        show_to_user: ユーザーにエラーを表示するかどうか
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                ErrorHandler.handle_error(e, context, show_to_user)
                return None
        return wrapper
    return decorator

def safe_execute(func: Callable, *args, context: str = "", show_to_user: bool = True, **kwargs) -> Any:
    """
    安全な関数実行
    
    Args:
        func: 実行する関数
        *args: 関数の引数
        context: エラーが発生したコンテキスト
        show_to_user: ユーザーにエラーを表示するかどうか
        **kwargs: 関数のキーワード引数
        
    Returns:
        関数の実行結果、エラー時はNone
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        ErrorHandler.handle_error(e, context, show_to_user)
        return None

def validate_input(value: Any, validation_func: Callable, error_message: str) -> bool:
    """
    入力値の検証
    
    Args:
        value: 検証する値
        validation_func: 検証関数
        error_message: エラーメッセージ
        
    Returns:
        検証結果
    """
    try:
        if not validation_func(value):
            ErrorHandler.handle_warning(error_message)
            return False
        return True
    except Exception as e:
        ErrorHandler.handle_error(e, "入力値検証中")
        return False

def log_operation(operation: str, context: str = ""):
    """
    操作のログ記録
    
    Args:
        operation: 操作内容
        context: 操作のコンテキスト
    """
    message = f"{context}: {operation}" if context else operation
    app_logger.info(message)
