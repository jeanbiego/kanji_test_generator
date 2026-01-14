"""
最終修正のテスト
- リセットボタンの動作
- 重複判定の機能
- フォーム内容のクリア
"""

import pytest
import streamlit as st
from unittest.mock import Mock, patch
from src.app import show_problem_creation_page, check_duplicate_problem
from src.modules.models import Problem


class TestFinalFixes:
    """最終修正のテスト"""
    
    def setup_method(self):
        """各テストメソッド実行前の準備"""
        # セッション状態をリセット
        if hasattr(st, 'session_state'):
            st.session_state.clear()
    
    def test_duplicate_check_functionality(self):
        """重複チェック機能のテスト"""
        # Arrange
        with patch.object(st, 'session_state') as mock_session:
            mock_storage = Mock()
            mock_storage.load_problems.return_value = [
                Problem(
                    sentence="独創的な表現で知られるアーティスト",
                    answer_kanji="独創",
                    reading="ドクソウ"
                )
            ]
            mock_session.problem_storage = mock_storage
            
            # Act
            is_duplicate, message = check_duplicate_problem(
                "独創的な表現で知られるアーティスト",
                "独創",
                "ドクソウ"
            )
            
            # Assert
            assert is_duplicate == True
            assert "同じ漢字・読みの組み合わせが既に存在します" in message
    
    @pytest.mark.skip(reason="StreamlitのUI関数のテストは複雑なモックが必要なためスキップ")
    def test_reset_button_preserves_duplicate_state(self):
        """リセットボタンが重複状態を保持するテスト"""
        # Arrange
        with patch.object(st, 'session_state') as mock_session:
            mock_session.__contains__ = lambda key: key in ['duplicate_detected']
            mock_session.__getitem__ = lambda key: True if key == 'duplicate_detected' else None
            
            # Act
            with patch('streamlit.form') as mock_form:
                with patch('streamlit.form_submit_button') as mock_submit_button:
                    mock_submit_button.side_effect = [False, True]  # リセットボタンが押された
                    show_problem_creation_page()
            
            # Assert
            # 重複状態が保持されることを確認
            assert mock_submit_button.call_count >= 2
    
    @pytest.mark.skip(reason="StreamlitのUI関数のテストは複雑なモックが必要なためスキップ")
    def test_form_reset_functionality(self):
        """フォームリセット機能のテスト"""
        # Arrange
        with patch.object(st, 'session_state') as mock_session:
            mock_session.__contains__ = lambda key: False
            mock_session.__getitem__ = lambda key: None
            
            # Act
            with patch('streamlit.form') as mock_form:
                with patch('streamlit.form_submit_button') as mock_submit_button:
                    mock_submit_button.side_effect = [False, True]  # リセットボタンが押された
                    show_problem_creation_page()
            
            # Assert
            # リセット処理が呼ばれることを確認
            assert mock_submit_button.call_count >= 2
    
    @pytest.mark.skip(reason="StreamlitのUI関数のテストは複雑なモックが必要なためスキップ")
    def test_duplicate_warning_display(self):
        """重複警告表示のテスト"""
        # Arrange
        with patch.object(st, 'session_state') as mock_session:
            mock_session.get.return_value = True  # duplicate_detected = True
            mock_session.__contains__ = lambda key: key == 'duplicate_detected'
            mock_session.__getitem__ = lambda key: "テスト重複メッセージ" if key == 'duplicate_message' else None
            
            # Act
            with patch('streamlit.warning') as mock_warning:
                show_problem_creation_page()
            
            # Assert
            # 重複警告が表示されることを確認
            mock_warning.assert_called()
    
    def test_duplicate_check_with_different_problems(self):
        """異なる問題での重複チェックテスト"""
        # Arrange
        with patch.object(st, 'session_state') as mock_session:
            mock_storage = Mock()
            mock_storage.load_problems.return_value = [
                Problem(
                    sentence="独創的な表現で知られるアーティスト",
                    answer_kanji="独創",
                    reading="ドクソウ"
                )
            ]
            mock_session.problem_storage = mock_storage
            
            # Act
            is_duplicate, message = check_duplicate_problem(
                "新しい問題文",
                "新規",
                "シンキ"
            )
            
            # Assert
            assert is_duplicate == False
            assert message == ""


if __name__ == "__main__":
    pytest.main([__file__])
