"""
統計機能のテスト
"""

import pytest
from datetime import datetime, date, timedelta
from unittest.mock import Mock, patch
from src.modules.statistics import StatisticsCalculator, VisualizationEngine, StatisticsManager
from src.modules.models import Problem, Attempt


class TestStatisticsCalculator:
    """StatisticsCalculatorのテスト"""
    
    def setup_method(self):
        """テスト前の準備"""
        self.calculator = StatisticsCalculator()
        
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
                timestamp=datetime(2025, 1, 2, 12, 0)
            )
        ]
    
    @patch('src.modules.statistics.AttemptStorage.load_attempts')
    def test_calculate_problem_statistics(self, mock_load_attempts):
        """問題別統計計算のテスト"""
        mock_load_attempts.return_value = self.mock_attempts
        
        results = self.calculator.calculate_problem_statistics(self.mock_problems)
        
        # 結果確認
        assert len(results) == 2
        
        # 問題1の統計確認
        problem1_stats = results["1"]
        assert problem1_stats['correct_count'] == 1
        assert problem1_stats['total_count'] == 2
        assert problem1_stats['accuracy'] == 50.0
        assert problem1_stats['last_attempted'] == datetime(2025, 1, 2, 11, 0)
        assert problem1_stats['mistake_distribution']['読み間違い'] == 1
        
        # 問題2の統計確認
        problem2_stats = results["2"]
        assert problem2_stats['correct_count'] == 1
        assert problem2_stats['total_count'] == 1
        assert problem2_stats['accuracy'] == 100.0
        assert problem2_stats['last_attempted'] == datetime(2025, 1, 2, 12, 0)
        assert problem2_stats['mistake_distribution'] == {}
    
    @patch('src.modules.statistics.AttemptStorage.load_attempts')
    def test_calculate_daily_statistics(self, mock_load_attempts):
        """日別統計計算のテスト"""
        mock_load_attempts.return_value = self.mock_attempts
        
        results = self.calculator.calculate_daily_statistics()
        
        # 結果確認
        assert results['total_attempts'] == 3
        assert results['total_correct'] == 2
        assert results['overall_accuracy'] == 66.67  # 2/3 * 100
        
        # 日別データの確認
        daily_data = results['daily_data']
        assert len(daily_data) == 2  # 2日間
        
        # 1月1日のデータ確認
        jan1_data = next(d for d in daily_data if d['date'] == date(2025, 1, 1))
        assert jan1_data['attempts'] == 1
        assert jan1_data['correct'] == 1
        assert jan1_data['accuracy'] == 100.0
        
        # 1月2日のデータ確認
        jan2_data = next(d for d in daily_data if d['date'] == date(2025, 1, 2))
        assert jan2_data['attempts'] == 2
        assert jan2_data['correct'] == 1
        assert jan2_data['accuracy'] == 50.0
    
    @patch('src.modules.statistics.AttemptStorage.load_attempts')
    def test_calculate_daily_statistics_with_date_range(self, mock_load_attempts):
        """日付範囲指定での日別統計計算のテスト"""
        mock_load_attempts.return_value = self.mock_attempts
        
        # 1月1日のみの統計
        results = self.calculator.calculate_daily_statistics(
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 1)
        )
        
        # 結果確認
        assert results['total_attempts'] == 1
        assert results['total_correct'] == 1
        assert results['overall_accuracy'] == 100.0
        
        daily_data = results['daily_data']
        assert len(daily_data) == 1
        assert daily_data[0]['date'] == date(2025, 1, 1)
    
    @patch('src.modules.statistics.AttemptStorage.load_attempts')
    def test_calculate_mistake_analysis(self, mock_load_attempts):
        """間違い分析計算のテスト"""
        mock_load_attempts.return_value = self.mock_attempts
        
        results = self.calculator.calculate_mistake_analysis()
        
        # 結果確認
        assert results['mistake_distribution']['読み間違い'] == 1
        assert results['common_mistakes'][0] == ('読み間違い', 1)
        assert len(results['improvement_areas']) == 0  # 3回未満なので改善領域なし
    
    @patch('src.modules.statistics.AttemptStorage.load_attempts')
    def test_calculate_learning_progress(self, mock_load_attempts):
        """学習進捗計算のテスト"""
        mock_load_attempts.return_value = self.mock_attempts
        
        results = self.calculator.calculate_learning_progress(days=30)
        
        # 結果確認
        assert results['period_days'] == 30
        assert results['total_attempts'] == 3
        assert results['total_correct'] == 2
        assert results['accuracy'] == 66.67
        assert results['consistency_score'] == 6.67  # 2日 / 30日 * 100
        
        # 学習曲線の確認
        learning_curve = results['learning_curve']
        assert len(learning_curve) == 2  # 2日間
        
        # 1月1日の学習曲線確認
        jan1_curve = next(c for c in learning_curve if c['date'] == date(2025, 1, 1))
        assert jan1_curve['daily_attempts'] == 1
        assert jan1_curve['daily_correct'] == 1
        assert jan1_curve['cumulative_attempts'] == 1
        assert jan1_curve['cumulative_correct'] == 1
        assert jan1_curve['cumulative_accuracy'] == 100.0


class TestVisualizationEngine:
    """VisualizationEngineのテスト"""
    
    def setup_method(self):
        """テスト前の準備"""
        self.visualizer = VisualizationEngine()
        
        # モックデータ
        self.mock_problem_stats = {
            "1": {
                'problem': Problem(
                    id="1",
                    sentence="独創的な表現で知られるアーティスト",
                    answer_kanji="独創的",
                    reading="どくそうてき",
                    created_at=datetime(2025, 1, 1, 10, 0)
                ),
                'correct_count': 1,
                'total_count': 2,
                'accuracy': 50.0,
                'last_attempted': datetime(2025, 1, 2, 11, 0),
                'mistake_distribution': {'読み間違い': 1}
            }
        }
        
        self.mock_daily_stats = [
            {
                'date': date(2025, 1, 1),
                'attempts': 1,
                'correct': 1,
                'accuracy': 100.0
            },
            {
                'date': date(2025, 1, 2),
                'attempts': 2,
                'correct': 1,
                'accuracy': 50.0
            }
        ]
        
        self.mock_mistake_distribution = {
            '読み間違い': 1,
            '書き間違い': 0
        }
        
        self.mock_learning_curve = [
            {
                'date': date(2025, 1, 1),
                'daily_attempts': 1,
                'daily_correct': 1,
                'cumulative_attempts': 1,
                'cumulative_correct': 1,
                'cumulative_accuracy': 100.0
            },
            {
                'date': date(2025, 1, 2),
                'daily_attempts': 2,
                'daily_correct': 1,
                'cumulative_attempts': 3,
                'cumulative_correct': 2,
                'cumulative_accuracy': 66.67
            }
        ]
    
    def test_create_accuracy_chart(self):
        """正答率チャート作成のテスト"""
        fig = self.visualizer.create_accuracy_chart(self.mock_problem_stats)
        
        # チャートが作成されることを確認
        assert fig is not None
        assert len(fig.data) == 1  # 1つのバーチャート
        assert fig.data[0].type == 'bar'
    
    def test_create_accuracy_chart_empty(self):
        """空データでの正答率チャート作成のテスト"""
        fig = self.visualizer.create_accuracy_chart({})
        
        # 空のチャートが作成されることを確認
        assert fig is not None
        assert len(fig.data) == 0
    
    def test_create_daily_progress_chart(self):
        """日別進捗チャート作成のテスト"""
        fig = self.visualizer.create_daily_progress_chart(self.mock_daily_stats)
        
        # チャートが作成されることを確認
        assert fig is not None
        assert len(fig.data) == 2  # 2つのサブプロット
        assert fig.data[0].type == 'bar'  # 試行回数
        assert fig.data[1].type == 'scatter'  # 正答率
    
    def test_create_mistake_distribution_chart(self):
        """間違い分布チャート作成のテスト"""
        fig = self.visualizer.create_mistake_distribution_chart(self.mock_mistake_distribution)
        
        # チャートが作成されることを確認
        assert fig is not None
        assert len(fig.data) == 1  # 1つのパイチャート
        assert fig.data[0].type == 'pie'
    
    def test_create_learning_curve_chart(self):
        """学習曲線チャート作成のテスト"""
        fig = self.visualizer.create_learning_curve_chart(self.mock_learning_curve)
        
        # チャートが作成されることを確認
        assert fig is not None
        assert len(fig.data) == 2  # 2つのサブプロット
        assert fig.data[0].type == 'scatter'  # 累積正答率
        assert fig.data[1].type == 'bar'  # 日別試行回数


class TestStatisticsManager:
    """StatisticsManagerのテスト"""
    
    def setup_method(self):
        """テスト前の準備"""
        self.manager = StatisticsManager()
    
    @patch('src.modules.statistics.StatisticsCalculator.get_comprehensive_statistics')
    def test_get_comprehensive_statistics(self, mock_get_stats):
        """包括的統計取得のテスト"""
        mock_stats = {
            'overview': {
                'total_problems': 2,
                'total_attempts': 3,
                'overall_accuracy': 66.67
            },
            'problem_statistics': {},
            'daily_statistics': {'daily_data': []},
            'mistake_analysis': {'mistake_distribution': {}},
            'learning_progress': {'learning_curve': []}
        }
        mock_get_stats.return_value = mock_stats
        
        results = self.manager.get_comprehensive_statistics()
        
        # 結果確認
        assert results == mock_stats
        mock_get_stats.assert_called_once()
    
    @patch('src.modules.statistics.StatisticsManager.get_comprehensive_statistics')
    @patch('src.modules.statistics.VisualizationEngine.create_accuracy_chart')
    @patch('src.modules.statistics.VisualizationEngine.create_daily_progress_chart')
    def test_get_visualization_data(self, mock_daily_chart, mock_accuracy_chart, mock_get_stats):
        """可視化データ取得のテスト"""
        mock_stats = {
            'problem_statistics': {'test': 'data'},
            'daily_statistics': {'daily_data': [{'date': date.today(), 'attempts': 1, 'correct': 1, 'accuracy': 100.0}]},
            'mistake_analysis': {'mistake_distribution': {}},
            'learning_progress': {'learning_curve': []}
        }
        mock_get_stats.return_value = mock_stats
        
        mock_accuracy_chart.return_value = 'accuracy_chart'
        mock_daily_chart.return_value = 'daily_chart'
        
        results = self.manager.get_visualization_data()
        
        # 結果確認
        assert 'accuracy_chart' in results
        assert 'daily_progress_chart' in results
        assert results['accuracy_chart'] == 'accuracy_chart'
        assert results['daily_progress_chart'] == 'daily_chart'


if __name__ == "__main__":
    pytest.main([__file__])
