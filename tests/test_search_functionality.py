"""
問題検索機能のテスト
"""

import pytest
from datetime import datetime, date
from unittest.mock import Mock, patch
from src.modules.search import SearchEngine, FilterEngine, SearchManager
from src.modules.models import Problem, Attempt


class TestSearchEngine:
    """SearchEngineのテスト"""
    
    def setup_method(self):
        """テスト前の準備"""
        self.search_engine = SearchEngine()
        
        # モックデータ
        self.mock_problems = [
            Problem(
                id="1",
                sentence="独創的な表現で知られるアーティスト",
                answer_kanji="独創的",
                reading="どくそうてき",
                created_at=datetime(2025, 1, 1, 10, 0)
            ),
            Problem(
                id="2",
                sentence="美しい風景を描いた絵画",
                answer_kanji="美しい",
                reading="うつくしい",
                created_at=datetime(2025, 1, 2, 10, 0)
            ),
            Problem(
                id="3",
                sentence="創造的なアイデアを考える",
                answer_kanji="創造的",
                reading="そうぞうてき",
                created_at=datetime(2025, 1, 3, 10, 0)
            )
        ]
    
    @patch('src.modules.search.ProblemStorage.load_problems')
    def test_search_problems_all(self, mock_load_problems):
        """全項目検索のテスト"""
        mock_load_problems.return_value = self.mock_problems
        
        # 検索実行
        results = self.search_engine.search_problems("独創的", "all")
        
        # 結果確認
        assert len(results) == 1
        assert results[0].answer_kanji == "独創的"
    
    @patch('src.modules.search.ProblemStorage.load_problems')
    def test_search_problems_problem_text(self, mock_load_problems):
        """問題文のみ検索のテスト"""
        mock_load_problems.return_value = self.mock_problems
        
        # 検索実行
        results = self.search_engine.search_problems("美しい", "problem_text")
        
        # 結果確認
        assert len(results) == 1
        assert "美しい" in results[0].sentence
    
    @patch('src.modules.search.ProblemStorage.load_problems')
    def test_search_problems_answer(self, mock_load_problems):
        """回答漢字のみ検索のテスト"""
        mock_load_problems.return_value = self.mock_problems
        
        # 検索実行
        results = self.search_engine.search_problems("創造的", "answer")
        
        # 結果確認
        assert len(results) == 1
        assert results[0].answer_kanji == "創造的"
    
    @patch('src.modules.search.ProblemStorage.load_problems')
    def test_search_problems_reading(self, mock_load_problems):
        """読みのみ検索のテスト"""
        mock_load_problems.return_value = self.mock_problems
        
        # 検索実行
        results = self.search_engine.search_problems("うつくしい", "reading")
        
        # 結果確認
        assert len(results) == 1
        assert results[0].reading == "うつくしい"
    
    @patch('src.modules.search.ProblemStorage.load_problems')
    def test_search_problems_empty_query(self, mock_load_problems):
        """空のクエリでの検索テスト"""
        mock_load_problems.return_value = self.mock_problems
        
        # 検索実行
        results = self.search_engine.search_problems("", "all")
        
        # 結果確認（空のクエリの場合は全件返す）
        assert len(results) == 3
    
    @patch('src.modules.search.ProblemStorage.load_problems')
    def test_search_problems_no_results(self, mock_load_problems):
        """該当なしの検索テスト"""
        mock_load_problems.return_value = self.mock_problems
        
        # 検索実行
        results = self.search_engine.search_problems("存在しない", "all")
        
        # 結果確認
        assert len(results) == 0
    
    @patch('src.modules.search.ProblemStorage.load_problems')
    def test_search_with_regex(self, mock_load_problems):
        """正規表現検索のテスト"""
        mock_load_problems.return_value = self.mock_problems
        
        # 検索実行（「的」で終わる漢字を検索）
        results = self.search_engine.search_with_regex("的$", "answer")
        
        # 結果確認
        assert len(results) == 2
        assert all(problem.answer_kanji.endswith("的") for problem in results)
    
    @patch('src.modules.search.ProblemStorage.load_problems')
    def test_search_with_regex_invalid_pattern(self, mock_load_problems):
        """無効な正規表現パターンのテスト"""
        mock_load_problems.return_value = self.mock_problems
        
        # 検索実行（無効なパターン）
        results = self.search_engine.search_with_regex("[", "all")
        
        # 結果確認（エラーの場合は空のリストを返す）
        assert len(results) == 0


class TestFilterEngine:
    """FilterEngineのテスト"""
    
    def setup_method(self):
        """テスト前の準備"""
        self.filter_engine = FilterEngine()
        
        # モックデータ
        self.mock_problems = [
            Problem(
                id="1",
                sentence="問題1",
                answer_kanji="漢字1",
                reading="よみ1",
                created_at=datetime(2025, 1, 1, 10, 0)
            ),
            Problem(
                id="2",
                sentence="問題2",
                answer_kanji="漢字2",
                reading="よみ2",
                created_at=datetime(2025, 1, 15, 10, 0)
            ),
            Problem(
                id="3",
                sentence="問題3",
                answer_kanji="漢字3",
                reading="よみ3",
                created_at=datetime(2025, 1, 30, 10, 0)
            )
        ]
        
        self.mock_attempts = [
            Attempt(
                id="1",
                problem_id="1",
                is_correct=True,
                mistake_type="なし",
                learning_memo="メモ1",
                timestamp=datetime(2025, 1, 1, 11, 0)
            ),
            Attempt(
                id="2",
                problem_id="1",
                is_correct=False,
                mistake_type="読み間違い",
                learning_memo="メモ2",
                timestamp=datetime(2025, 1, 2, 11, 0)
            ),
            Attempt(
                id="3",
                problem_id="2",
                is_correct=True,
                mistake_type="なし",
                learning_memo="メモ3",
                timestamp=datetime(2025, 1, 15, 11, 0)
            ),
            Attempt(
                id="4",
                problem_id="2",
                is_correct=True,
                mistake_type="なし",
                learning_memo="メモ4",
                timestamp=datetime(2025, 1, 16, 11, 0)
            )
        ]
    
    def test_filter_by_date_range(self):
        """日付範囲フィルタのテスト"""
        # 1月1日から1月15日まで
        start_date = date(2025, 1, 1)
        end_date = date(2025, 1, 15)
        
        results = self.filter_engine.filter_by_date_range(
            self.mock_problems, start_date, end_date
        )
        
        assert len(results) == 2
        assert results[0].id == "1"
        assert results[1].id == "2"
    
    def test_filter_by_date_range_start_only(self):
        """開始日のみのフィルタテスト"""
        start_date = date(2025, 1, 15)
        
        results = self.filter_engine.filter_by_date_range(
            self.mock_problems, start_date, None
        )
        
        assert len(results) == 2
        assert results[0].id == "2"
        assert results[1].id == "3"
    
    def test_filter_by_date_range_end_only(self):
        """終了日のみのフィルタテスト"""
        end_date = date(2025, 1, 15)
        
        results = self.filter_engine.filter_by_date_range(
            self.mock_problems, None, end_date
        )
        
        assert len(results) == 2
        assert results[0].id == "1"
        assert results[1].id == "2"
    
    @patch('src.modules.search.AttemptStorage.load_attempts')
    def test_filter_by_accuracy_range(self, mock_load_attempts):
        """正答率範囲フィルタのテスト"""
        mock_load_attempts.return_value = self.mock_attempts
        
        # 正答率50%以上
        results = self.filter_engine.filter_by_accuracy_range(
            self.mock_problems, 50.0, None
        )
        
        # 問題1: 1/2 = 50%, 問題2: 2/2 = 100%
        assert len(results) == 2
        assert results[0].id == "1"
        assert results[1].id == "2"
    
    @patch('src.modules.search.AttemptStorage.load_attempts')
    def test_filter_by_attempt_count(self, mock_load_attempts):
        """試行回数範囲フィルタのテスト"""
        mock_load_attempts.return_value = self.mock_attempts
        
        # 試行回数2回以上
        results = self.filter_engine.filter_by_attempt_count(
            self.mock_problems, 2, None
        )
        
        # 問題1: 2回, 問題2: 2回
        assert len(results) == 2
        assert results[0].id == "1"
        assert results[1].id == "2"
    
    @patch('src.modules.search.AttemptStorage.load_attempts')
    def test_filter_by_mistake_type(self, mock_load_attempts):
        """間違いの種類フィルタのテスト"""
        mock_load_attempts.return_value = self.mock_attempts
        
        # 読み間違いを含む問題
        results = self.filter_engine.filter_by_mistake_type(
            self.mock_problems, ["読み間違い"]
        )
        
        # 問題1のみ読み間違いがある
        assert len(results) == 1
        assert results[0].id == "1"


class TestSearchManager:
    """SearchManagerのテスト"""
    
    def setup_method(self):
        """テスト前の準備"""
        self.search_manager = SearchManager()
        
        # モックデータ
        self.mock_problems = [
            Problem(
                id="1",
                sentence="独創的な表現で知られるアーティスト",
                answer_kanji="独創的",
                reading="どくそうてき",
                created_at=datetime(2025, 1, 1, 10, 0)
            ),
            Problem(
                id="2",
                sentence="美しい風景を描いた絵画",
                answer_kanji="美しい",
                reading="うつくしい",
                created_at=datetime(2025, 1, 2, 10, 0)
            )
        ]
        
        self.mock_attempts = [
            Attempt(
                id="1",
                problem_id="1",
                is_correct=True,
                mistake_type="なし",
                learning_memo="メモ1",
                timestamp=datetime(2025, 1, 1, 11, 0)
            ),
            Attempt(
                id="2",
                problem_id="1",
                is_correct=False,
                mistake_type="読み間違い",
                learning_memo="メモ2",
                timestamp=datetime(2025, 1, 2, 11, 0)
            ),
            Attempt(
                id="3",
                problem_id="2",
                is_correct=True,
                mistake_type="なし",
                learning_memo="メモ3",
                timestamp=datetime(2025, 1, 2, 11, 0)
            )
        ]
    
    @patch('src.modules.search.SearchEngine.search_problems')
    def test_advanced_search_basic(self, mock_search):
        """基本検索のテスト"""
        mock_search.return_value = self.mock_problems
        
        results = self.search_manager.advanced_search(
            query="独創的",
            search_type="all"
        )
        
        assert len(results) == 2
        mock_search.assert_called_once_with("独創的", "all")
    
    @patch('src.modules.search.SearchEngine.search_with_regex')
    def test_advanced_search_regex(self, mock_search):
        """正規表現検索のテスト"""
        mock_search.return_value = self.mock_problems
        
        results = self.search_manager.advanced_search(
            query="的$",
            search_type="answer",
            use_regex=True
        )
        
        assert len(results) == 2
        mock_search.assert_called_once_with("的$", "answer")
    
    @patch('src.modules.search.SearchEngine.search_problems')
    @patch('src.modules.search.FilterEngine.filter_by_date_range')
    def test_advanced_search_with_filters(self, mock_filter_date, mock_search):
        """フィルタ付き検索のテスト"""
        mock_search.return_value = self.mock_problems
        mock_filter_date.return_value = self.mock_problems
        
        results = self.search_manager.advanced_search(
            query="独創的",
            search_type="all",
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31)
        )
        
        assert len(results) == 2
        mock_search.assert_called_once_with("独創的", "all")
        mock_filter_date.assert_called_once()
    
    def test_get_search_statistics(self):
        """検索統計のテスト"""
        stats = self.search_manager.get_search_statistics(self.mock_problems)
        
        assert stats['total_count'] == 2
        assert stats['total_attempts'] == 3
        assert stats['average_accuracy'] == 66.67  # 2/3 * 100
        assert stats['date_range']['earliest'] == date(2025, 1, 1)
        assert stats['date_range']['latest'] == date(2025, 1, 2)
    
    def test_get_search_statistics_empty(self):
        """空の検索結果の統計テスト"""
        stats = self.search_manager.get_search_statistics([])
        
        assert stats['total_count'] == 0
        assert stats['total_attempts'] == 0
        assert stats['average_accuracy'] == 0.0
        assert stats['date_range'] is None


if __name__ == "__main__":
    pytest.main([__file__])
