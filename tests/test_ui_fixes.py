"""
UI修正のテスト
- 印刷用ページの「印刷」「閉じる」ボタンの非表示
- 印刷時のフォントサイズ調整
- リセットボタンの動作
"""

import pytest
import streamlit as st
from unittest.mock import Mock, patch
from src.app import show_problem_creation_page, show_print_page
from src.modules.print_page import PrintPageGenerator
from src.modules.models import Problem


class TestUIFixes:
    """UI修正のテスト"""
    
    def setup_method(self):
        """各テストメソッド実行前の準備"""
        # セッション状態をリセット
        if hasattr(st, 'session_state'):
            st.session_state.clear()
    
    def test_reset_button_functionality(self):
        """リセットボタンの動作テスト"""
        # Arrange
        with patch.object(st, 'session_state') as mock_session:
            mock_session.__contains__ = lambda key: key in ['duplicate_detected', 'duplicate_message', 'pending_problem']
            mock_session.__getitem__ = lambda key: None
            
            # Act
            with patch('streamlit.form') as mock_form:
                with patch('streamlit.form_submit_button') as mock_submit_button:
                    mock_submit_button.side_effect = [False, True]  # リセットボタンが押された
                    show_problem_creation_page()
            
            # Assert
            # リセット処理が呼ばれることを確認
            assert mock_submit_button.call_count >= 2
    
    def test_print_page_css_embedding(self):
        """印刷用ページのCSS埋め込みテスト"""
        # Arrange
        test_problems = [
            Problem(
                sentence="テスト問題文",
                answer_kanji="テスト",
                reading="テスト"
            )
        ]
        
        # Act
        generator = PrintPageGenerator()
        html_content = generator.generate_print_page(test_problems, "テストタイトル", 1)
        
        # Assert
        # CSSが埋め込まれていることを確認
        assert "@media print" in html_content
        assert "font-size: 20pt" in html_content
        assert ".no-print" in html_content
        assert "display: none !important" in html_content
    
    def test_print_page_no_print_class(self):
        """印刷用ページのno-printクラステスト"""
        # Arrange
        test_problems = [
            Problem(
                sentence="テスト問題文",
                answer_kanji="テスト",
                reading="テスト"
            )
        ]
        
        # Act
        generator = PrintPageGenerator()
        html_content = generator.generate_print_page(test_problems, "テストタイトル", 1)
        
        # Assert
        # 印刷制御ボタンにno-printクラスが設定されていることを確認
        assert 'class="print-controls no-print"' in html_content
        assert "印刷" in html_content
        assert "閉じる" in html_content
    
    def test_print_page_font_sizes(self):
        """印刷用ページのフォントサイズテスト"""
        # Arrange
        test_problems = [
            Problem(
                sentence="テスト問題文",
                answer_kanji="テスト",
                reading="テスト"
            )
        ]
        
        # Act
        generator = PrintPageGenerator()
        html_content = generator.generate_print_page(test_problems, "テストタイトル", 1)
        
        # Assert
        # 各要素のフォントサイズが正しく設定されていることを確認
        assert "font-size: 20pt" in html_content  # body
        assert "font-size: 24pt" in html_content  # title
        assert "font-size: 18pt" in html_content  # header-info
        assert "font-size: 16pt" in html_content  # footer
    
    def test_print_page_answer_box_size(self):
        """印刷用ページの回答ボックスサイズテスト"""
        # Arrange
        test_problems = [
            Problem(
                sentence="テスト問題文",
                answer_kanji="テスト",
                reading="テスト"
            )
        ]
        
        # Act
        generator = PrintPageGenerator()
        html_content = generator.generate_print_page(test_problems, "テストタイトル", 1)
        
        # Assert
        # 回答ボックスのサイズが正しく設定されていることを確認
        assert "width: 80mm" in html_content
        assert "height: 12mm" in html_content


if __name__ == "__main__":
    pytest.main([__file__])
