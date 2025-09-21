"""
ストレージ機能のテスト
"""

import pytest
import tempfile
import os
from datetime import datetime
from src.modules.storage import ProblemStorage, AttemptStorage
from src.modules.models import Problem, Attempt

class TestProblemStorage:
    """ProblemStorageのテスト"""
    
    def test_problem_storage_creation(self):
        """ストレージの作成テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = ProblemStorage(temp_dir)
            assert os.path.exists(storage.file_path)
    
    def test_save_and_load_problem(self):
        """問題の保存と読み込みテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = ProblemStorage(temp_dir)
            
            # テスト用の問題を作成
            problem = Problem(
                sentence="独創的な表現で知られるアーティスト",
                answer_kanji="独創",
                reading="どくそう"
            )
            
            # 保存
            result = storage.save_problem(problem)
            assert result is True
            
            # 読み込み
            loaded_problems = storage.load_problems()
            assert len(loaded_problems) == 1
            assert loaded_problems[0].sentence == problem.sentence
            assert loaded_problems[0].answer_kanji == problem.answer_kanji
            assert loaded_problems[0].reading == problem.reading
    
    def test_delete_problem(self):
        """問題の削除テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = ProblemStorage(temp_dir)
            
            # テスト用の問題を作成
            problem = Problem(
                sentence="独創的な表現で知られるアーティスト",
                answer_kanji="独創",
                reading="どくそう"
            )
            
            # 保存
            storage.save_problem(problem)
            
            # 削除
            result = storage.delete_problem(problem.id)
            assert result is True
            
            # 確認
            loaded_problems = storage.load_problems()
            assert len(loaded_problems) == 0

class TestAttemptStorage:
    """AttemptStorageのテスト"""
    
    def test_attempt_storage_creation(self):
        """ストレージの作成テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = AttemptStorage(temp_dir)
            assert os.path.exists(storage.file_path)
    
    def test_save_and_load_attempt(self):
        """試行の保存と読み込みテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = AttemptStorage(temp_dir)
            
            # テスト用の試行を作成
            attempt = Attempt(
                problem_id="test_problem_id",
                is_correct=True
            )
            
            # 保存
            result = storage.save_attempt(attempt)
            assert result is True
            
            # 読み込み
            loaded_attempts = storage.load_attempts()
            assert len(loaded_attempts) == 1
            assert loaded_attempts[0].problem_id == attempt.problem_id
            assert loaded_attempts[0].is_correct == attempt.is_correct
    
    def test_get_attempts_by_problem(self):
        """特定の問題の試行取得テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            storage = AttemptStorage(temp_dir)
            
            # テスト用の試行を作成
            attempt1 = Attempt(problem_id="problem1", is_correct=True)
            attempt2 = Attempt(problem_id="problem2", is_correct=False)
            attempt3 = Attempt(problem_id="problem1", is_correct=False)
            
            # 保存
            storage.save_attempt(attempt1)
            storage.save_attempt(attempt2)
            storage.save_attempt(attempt3)
            
            # 特定の問題の試行を取得
            problem1_attempts = storage.get_attempts_by_problem("problem1")
            assert len(problem1_attempts) == 2
            
            problem2_attempts = storage.get_attempts_by_problem("problem2")
            assert len(problem2_attempts) == 1
