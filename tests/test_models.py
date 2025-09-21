"""
モデルクラスのテスト
"""

import pytest
from datetime import datetime
from src.modules.models import Problem, Attempt
from src.modules.utils import normalize_reading

class TestProblem:
    """Problemクラスのテスト"""
    
    def test_problem_creation(self):
        """問題の作成テスト"""
        problem = Problem(
            sentence="独創的な表現で知られるアーティスト",
            answer_kanji="独創",
            reading="どくそう"
        )
        
        assert problem.sentence == "独創的な表現で知られるアーティスト"
        assert problem.answer_kanji == "独創"
        assert problem.reading == "ドクソウ"  # カタカナに正規化される
        assert problem.id is not None
        assert isinstance(problem.created_at, datetime)
    
    def test_problem_to_dict(self):
        """辞書形式への変換テスト"""
        problem = Problem(
            sentence="テスト文",
            answer_kanji="テスト",
            reading="てすと"
        )
        
        data = problem.to_dict()
        assert data['sentence'] == "テスト文"
        assert data['answer_kanji'] == "テスト"
        assert data['reading'] == "テスト"
        assert 'id' in data
        assert 'created_at' in data
    
    def test_problem_from_dict(self):
        """辞書からの作成テスト"""
        data = {
            'id': 'test-id',
            'sentence': 'テスト文',
            'answer_kanji': 'テスト',
            'reading': 'テスト',
            'created_at': '2025-01-27T10:00:00'
        }
        
        problem = Problem.from_dict(data)
        assert problem.id == 'test-id'
        assert problem.sentence == 'テスト文'
        assert problem.answer_kanji == 'テスト'
        assert problem.reading == 'テスト'

class TestAttempt:
    """Attemptクラスのテスト"""
    
    def test_attempt_creation(self):
        """試行の作成テスト"""
        attempt = Attempt(
            problem_id="test-problem-id",
            is_correct=True
        )
        
        assert attempt.problem_id == "test-problem-id"
        assert attempt.is_correct is True
        assert attempt.id is not None
        assert isinstance(attempt.attempted_at, datetime)
    
    def test_attempt_to_dict(self):
        """辞書形式への変換テスト"""
        attempt = Attempt(
            problem_id="test-problem-id",
            is_correct=False
        )
        
        data = attempt.to_dict()
        assert data['problem_id'] == "test-problem-id"
        assert data['is_correct'] is False
        assert 'id' in data
        assert 'attempted_at' in data
