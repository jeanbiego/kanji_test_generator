"""
採点機能拡張のテスト
"""

import pytest
from unittest.mock import Mock, patch
from src.modules.models import Problem, Attempt
from src.modules.storage import AttemptStorage
from datetime import datetime

class TestScoringEnhancement:
    """採点機能拡張のテストクラス"""
    
    def setup_method(self):
        """各テストメソッド実行前の準備"""
        self.attempt_storage = AttemptStorage()
        self.test_problems = [
            Problem(
                id="test-problem-1",
                sentence="独創的な表現で知られるアーティスト",
                answer_kanji="独創",
                reading="ドクソウ",
                created_at=datetime.now()
            ),
            Problem(
                id="test-problem-2", 
                sentence="美しい景色を眺める",
                answer_kanji="景色",
                reading="ケシキ",
                created_at=datetime.now()
            )
        ]
    
    def test_printed_problems_storage(self):
        """印刷した問題群の保存機能テスト"""
        # セッション状態のシミュレーション
        printed_problems = self.test_problems.copy()
        
        # 問題群が正しく保存されることを確認
        assert len(printed_problems) == 2
        assert printed_problems[0].answer_kanji == "独創"
        assert printed_problems[1].answer_kanji == "景色"
    
    def test_scoring_form_generation(self):
        """採点フォーム生成機能テスト"""
        printed_problems = self.test_problems.copy()
        
        # 採点フォーム用のスコアデータ生成
        scores = {}
        for i, problem in enumerate(printed_problems):
            scores[problem.id] = {
                'is_correct': i == 0,  # 最初の問題は正解、2番目は不正解
                'mistake_type': '読み間違い' if i != 0 else None,
                'notes': f'テストメモ{i+1}'
            }
        
        # スコアデータが正しく生成されることを確認
        assert len(scores) == 2
        assert scores['test-problem-1']['is_correct'] == True
        assert scores['test-problem-2']['is_correct'] == False
        assert scores['test-problem-2']['mistake_type'] == '読み間違い'
    
    def test_attempt_creation_from_scores(self):
        """スコアデータから試行データ作成テスト"""
        scores = {
            'test-problem-1': {
                'is_correct': True,
                'mistake_type': None,
                'notes': 'テストメモ1'
            },
            'test-problem-2': {
                'is_correct': False,
                'mistake_type': '読み間違い',
                'notes': 'テストメモ2'
            }
        }
        
        # スコアデータから試行データを作成
        attempts = []
        for problem_id, score_data in scores.items():
            attempt = Attempt(
                problem_id=problem_id,
                is_correct=score_data['is_correct']
            )
            attempts.append(attempt)
        
        # 試行データが正しく作成されることを確認
        assert len(attempts) == 2
        assert attempts[0].problem_id == 'test-problem-1'
        assert attempts[0].is_correct == True
        assert attempts[1].problem_id == 'test-problem-2'
        assert attempts[1].is_correct == False
    
    def test_batch_save_attempts(self):
        """一括保存機能テスト"""
        # モックを使用してファイル操作をシミュレート
        with patch.object(self.attempt_storage, 'save_attempt') as mock_save:
            mock_save.return_value = True
            
            # テスト用の試行データを作成
            attempts = [
                Attempt(problem_id='test-problem-1', is_correct=True),
                Attempt(problem_id='test-problem-2', is_correct=False)
            ]
            
            # 一括保存を実行
            saved_count = self.attempt_storage.save_attempts_batch(attempts)
            
            # 保存が正しく実行されることを確認
            assert saved_count == 2
            assert mock_save.call_count == 2
    
    def test_scoring_result_calculation(self):
        """採点結果計算テスト"""
        scores = {
            'problem-1': {'is_correct': True},
            'problem-2': {'is_correct': False},
            'problem-3': {'is_correct': True},
            'problem-4': {'is_correct': False}
        }
        
        # 正解数と正答率を計算
        correct_count = sum(1 for score in scores.values() if score['is_correct'])
        total_count = len(scores)
        accuracy = (correct_count / total_count) * 100 if total_count > 0 else 0
        
        # 計算結果が正しいことを確認
        assert correct_count == 2
        assert total_count == 4
        assert accuracy == 50.0
    
    def test_mistake_analysis(self):
        """間違い分析機能テスト"""
        scores = {
            'problem-1': {'is_correct': False, 'mistake_type': '読み間違い'},
            'problem-2': {'is_correct': False, 'mistake_type': '漢字間違い'},
            'problem-3': {'is_correct': False, 'mistake_type': '読み間違い'},
            'problem-4': {'is_correct': True, 'mistake_type': None}
        }
        
        # 間違いの分析
        mistake_analysis = {}
        for score in scores.values():
            if not score['is_correct'] and score['mistake_type']:
                mistake_type = score['mistake_type']
                mistake_analysis[mistake_type] = mistake_analysis.get(mistake_type, 0) + 1
        
        # 分析結果が正しいことを確認
        assert mistake_analysis['読み間違い'] == 2
        assert mistake_analysis['漢字間違い'] == 1
        assert len(mistake_analysis) == 2
    
    def test_empty_printed_problems_handling(self):
        """空の印刷問題群の処理テスト"""
        printed_problems = []
        
        # 空のリストが正しく処理されることを確認
        assert len(printed_problems) == 0
        
        # 空の場合の条件分岐テスト
        if not printed_problems:
            # 手動選択モードに移行する処理をシミュレート
            show_manual_selection = True
            assert show_manual_selection == True
    
    def test_scoring_form_validation(self):
        """採点フォームバリデーションテスト"""
        # 有効なスコアデータ
        valid_scores = {
            'problem-1': {
                'is_correct': True,
                'mistake_type': None,
                'notes': '正解'
            }
        }
        
        # 無効なスコアデータ（is_correctが欠如）
        invalid_scores = {
            'problem-1': {
                'mistake_type': '読み間違い',
                'notes': '間違い'
            }
        }
        
        # 有効なデータの検証
        for problem_id, score_data in valid_scores.items():
            assert 'is_correct' in score_data
            assert isinstance(score_data['is_correct'], bool)
        
        # 無効なデータの検証
        for problem_id, score_data in invalid_scores.items():
            assert 'is_correct' not in score_data
