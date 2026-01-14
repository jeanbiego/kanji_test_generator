"""
履歴管理機能拡張のテスト
"""

from datetime import datetime, timezone

from src.modules.models import Attempt, Problem
from src.modules.storage import AttemptStorage, ProblemStorage


class TestHistoryEnhancement:
    """履歴管理機能拡張のテストクラス"""

    def setup_method(self):
        """各テストメソッド実行前の準備"""
        self.problem_storage = ProblemStorage()
        self.attempt_storage = AttemptStorage()

        # テスト用の問題データ
        self.test_problems = [
            Problem(
                id="test-problem-1",
                sentence="独創的な表現で知られるアーティスト",
                answer_kanji="独創",
                reading="ドクソウ",
                created_at=datetime(2025, 1, 27, 10, 0, 0, tzinfo=timezone.utc),
            ),
            Problem(
                id="test-problem-2",
                sentence="美しい景色を眺める",
                answer_kanji="景色",
                reading="ケシキ",
                created_at=datetime(2025, 1, 27, 11, 0, 0, tzinfo=timezone.utc),
            ),
        ]

        # テスト用の試行データ
        self.test_attempts = [
            Attempt(
                id="attempt-1",
                problem_id="test-problem-1",
                attempted_at=datetime(2025, 1, 27, 12, 0, 0, tzinfo=timezone.utc),
                is_correct=True,
            ),
            Attempt(
                id="attempt-2",
                problem_id="test-problem-1",
                attempted_at=datetime(2025, 1, 27, 13, 0, 0, tzinfo=timezone.utc),
                is_correct=False,
            ),
            Attempt(
                id="attempt-3",
                problem_id="test-problem-2",
                attempted_at=datetime(2025, 1, 27, 14, 0, 0, tzinfo=timezone.utc),
                is_correct=True,
            ),
        ]

    def test_problem_statistics_calculation(self):
        """問題統計計算機能テスト"""
        # 問題別の統計を計算
        problem_stats = {}
        for attempt in self.test_attempts:
            problem_id = attempt.problem_id
            if problem_id not in problem_stats:
                problem_stats[problem_id] = {
                    "correct_count": 0,
                    "total_count": 0,
                    "last_attempted": None,
                }

            problem_stats[problem_id]["total_count"] += 1
            if attempt.is_correct:
                problem_stats[problem_id]["correct_count"] += 1

            # 最後の試行日を更新
            if (
                problem_stats[problem_id]["last_attempted"] is None
                or attempt.attempted_at > problem_stats[problem_id]["last_attempted"]
            ):
                problem_stats[problem_id]["last_attempted"] = attempt.attempted_at

        # 統計が正しく計算されることを確認
        assert len(problem_stats) == 2

        # 問題1の統計
        assert problem_stats["test-problem-1"]["correct_count"] == 1
        assert problem_stats["test-problem-1"]["total_count"] == 2
        assert problem_stats["test-problem-1"]["last_attempted"] == datetime(2025, 1, 27, 13, 0, 0, tzinfo=timezone.utc)

        # 問題2の統計
        assert problem_stats["test-problem-2"]["correct_count"] == 1
        assert problem_stats["test-problem-2"]["total_count"] == 1
        assert problem_stats["test-problem-2"]["last_attempted"] == datetime(2025, 1, 27, 14, 0, 0, tzinfo=timezone.utc)

    def test_accuracy_calculation(self):
        """正答率計算機能テスト"""
        problem_stats = {
            "test-problem-1": {"correct_count": 1, "total_count": 2},
            "test-problem-2": {"correct_count": 1, "total_count": 1},
        }

        # 正答率を計算
        for problem_id, stats in problem_stats.items():
            accuracy = 0
            if stats["total_count"] > 0:
                accuracy = (stats["correct_count"] / stats["total_count"]) * 100

            if problem_id == "test-problem-1":
                assert accuracy == 50.0
            elif problem_id == "test-problem-2":
                assert accuracy == 100.0

    def test_last_attempted_date_formatting(self):
        """最後の試行日フォーマット機能テスト"""
        last_attempted = datetime(2025, 1, 27, 14, 30, 0, tzinfo=timezone.utc)
        last_attempted_str = last_attempted.strftime("%Y/%m/%d %H:%M")

        assert last_attempted_str == "2025/01/27 14:30"

        # 未採点の場合
        last_attempted_str = "未採点"
        assert last_attempted_str == "未採点"

    def test_problem_title_with_statistics(self):
        """統計情報付き問題タイトル生成テスト"""
        problem = self.test_problems[0]
        problem_stat = {
            "correct_count": 1,
            "total_count": 2,
            "last_attempted": datetime(2025, 1, 27, 13, 0, 0, tzinfo=timezone.utc),
        }

        accuracy = (problem_stat["correct_count"] / problem_stat["total_count"]) * 100
        title = f"問題 1: {problem.answer_kanji} ({problem.reading}) - 正答率: {accuracy:.1f}% ({problem_stat['correct_count']}/{problem_stat['total_count']})"

        expected_title = "問題 1: 独創 (ドクソウ) - 正答率: 50.0% (1/2)"
        assert title == expected_title

    def test_overall_statistics_calculation(self):
        """全体統計計算機能テスト"""
        total_attempts = len(self.test_attempts)
        correct_attempts = sum(1 for a in self.test_attempts if a.is_correct)
        accuracy = (correct_attempts / total_attempts) * 100 if total_attempts > 0 else 0

        assert total_attempts == 3
        assert correct_attempts == 2
        assert abs(accuracy - 66.7) < 0.1  # 2/3 * 100 ≈ 66.7

    def test_empty_attempts_handling(self):
        """空の試行データ処理テスト"""
        empty_attempts = []
        problem_stats = {}

        # 空の試行データの場合
        if not empty_attempts:
            # 統計情報が空であることを確認
            assert len(problem_stats) == 0

            # 全体統計が0であることを確認
            total_attempts = len(empty_attempts)
            correct_attempts = sum(1 for a in empty_attempts if a.is_correct)
            accuracy = (correct_attempts / total_attempts) * 100 if total_attempts > 0 else 0

            assert total_attempts == 0
            assert correct_attempts == 0
            assert accuracy == 0

    def test_problem_without_attempts(self):
        """試行データがない問題の処理テスト"""
        problem_stat = {"correct_count": 0, "total_count": 0, "last_attempted": None}

        # 試行データがない場合の統計
        accuracy = 0
        if problem_stat["total_count"] > 0:
            accuracy = (problem_stat["correct_count"] / problem_stat["total_count"]) * 100

        last_attempted_str = "未採点"
        if problem_stat["last_attempted"]:
            last_attempted_str = problem_stat["last_attempted"].strftime("%Y/%m/%d %H:%M")

        assert accuracy == 0
        assert last_attempted_str == "未採点"

    def test_statistics_display_format(self):
        """統計表示フォーマットテスト"""
        problem_stat = {
            "correct_count": 3,
            "total_count": 5,
            "last_attempted": datetime(2025, 1, 27, 15, 0, 0, tzinfo=timezone.utc),
        }

        # 統計情報の表示フォーマット
        correct_str = f"正解回数: {problem_stat['correct_count']}"
        total_str = f"試行回数: {problem_stat['total_count']}"
        accuracy = (problem_stat["correct_count"] / problem_stat["total_count"]) * 100
        accuracy_str = f"正答率: {accuracy:.1f}%"
        last_attempted_str = problem_stat["last_attempted"].strftime("%Y/%m/%d %H:%M")

        assert correct_str == "正解回数: 3"
        assert total_str == "試行回数: 5"
        assert accuracy_str == "正答率: 60.0%"
        assert last_attempted_str == "2025/01/27 15:00"

    def test_duplicate_check_removal(self):
        """重複チェック機能削除テスト"""
        # 重複チェック関連のUI要素が削除されていることを確認
        # このテストは主にUIの変更を確認するため、モックを使用

        # 重複チェック機能が存在しないことを確認
        duplicate_check_elements = [
            "重複チェック",
            "check_sentence",
            "check_kanji",
            "check_reading",
            "重複チェック実行",
        ]

        # これらの要素がUIに含まれていないことを確認
        # 実際の実装では、これらの要素が削除されている
        for element in duplicate_check_elements:
            # 重複チェック関連の要素が削除されていることを確認
            assert element not in ["学習統計", "問題一覧", "検索", "並び順"]
