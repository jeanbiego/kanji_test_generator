"""
重複チェック機能の動作不良修正のテスト
"""

from unittest.mock import Mock, patch

import pytest
import streamlit as st

from src.app import check_duplicate_problem
from src.modules.models import Problem


class TestDuplicateCheckFix:
    """重複チェック機能の修正テスト"""

    def setup_method(self):
        """各テストメソッド実行前の準備"""
        # セッション状態をリセット
        if hasattr(st, "session_state"):
            st.session_state.clear()

        # モックデータの準備
        self.test_problems = [
            Problem(
                sentence="独創的な表現で知られるアーティスト",
                answer_kanji="独創",
                reading="ドクソウ",
            ),
            Problem(sentence="新しい技術を開発する", answer_kanji="開発", reading="カイハツ"),
        ]

    def test_check_duplicate_problem_complete_match(self):
        """完全一致の重複チェックテスト(実装仕様: 回答漢字と読みの組み合わせのみチェック)"""
        # Arrange
        with patch.object(st, "session_state") as mock_session:
            mock_storage = Mock()
            mock_storage.load_problems.return_value = self.test_problems
            mock_session.problem_storage = mock_storage

            # Act
            is_duplicate, message = check_duplicate_problem(
                "独創的な表現で知られるアーティスト", "独創", "ドクソウ"
            )

            # Assert
            assert is_duplicate
            assert "同じ漢字・読みの組み合わせが既に存在します" in message

    def test_check_duplicate_problem_kanji_reading_match(self):
        """漢字・読み組み合わせの重複チェックテスト"""
        # Arrange
        with patch.object(st, "session_state") as mock_session:
            mock_storage = Mock()
            mock_storage.load_problems.return_value = self.test_problems
            mock_session.problem_storage = mock_storage

            # Act
            is_duplicate, message = check_duplicate_problem(
                "異なる文章だが同じ漢字", "独創", "ドクソウ"
            )

            # Assert
            assert is_duplicate
            assert "同じ漢字・読みの組み合わせが既に存在します" in message

    def test_check_duplicate_problem_sentence_match(self):
        """問題文一致の重複チェックテスト(実装仕様: 問題文一致はチェックしないため、重複なしとなる)"""
        # Arrange
        with patch.object(st, "session_state") as mock_session:
            mock_storage = Mock()
            mock_storage.load_problems.return_value = self.test_problems
            mock_session.problem_storage = mock_storage

            # Act
            is_duplicate, message = check_duplicate_problem(
                "独創的な表現で知られるアーティスト", "表現", "ヒョウゲン"
            )

            # Assert
            # 実装では問題文一致をチェックしないため、回答漢字と読みが異なれば重複なし
            assert not is_duplicate
            assert message == ""

    def test_check_duplicate_problem_no_duplicate(self):
        """重複なしのテスト"""
        # Arrange
        with patch.object(st, "session_state") as mock_session:
            mock_storage = Mock()
            mock_storage.load_problems.return_value = self.test_problems
            mock_session.problem_storage = mock_storage

            # Act
            is_duplicate, message = check_duplicate_problem("全く新しい問題文", "新規", "シンキ")

            # Assert
            assert not is_duplicate
            assert message == ""

    def test_check_duplicate_problem_empty_storage(self):
        """空のストレージでの重複チェックテスト"""
        # Arrange
        with patch.object(st, "session_state") as mock_session:
            mock_storage = Mock()
            mock_storage.load_problems.return_value = []
            mock_session.problem_storage = mock_storage

            # Act
            is_duplicate, message = check_duplicate_problem("新しい問題文", "新規", "シンキ")

            # Assert
            assert not is_duplicate
            assert message == ""

    def test_check_duplicate_problem_exception_handling(self):
        """例外処理のテスト"""
        # Arrange
        with patch.object(st, "session_state") as mock_session:
            mock_storage = Mock()
            mock_storage.load_problems.side_effect = Exception("ストレージエラー")
            mock_session.problem_storage = mock_storage

            # Act
            is_duplicate, message = check_duplicate_problem("新しい問題文", "新規", "シンキ")

            # Assert
            assert not is_duplicate
            assert message == ""


if __name__ == "__main__":
    pytest.main([__file__])
