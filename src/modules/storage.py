"""
CSV入出力機能
"""

import csv
from pathlib import Path
from typing import List
from .models import Problem, Attempt

class ProblemStorage:
    """問題データのCSV入出力"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.file_path = self.data_dir / "problems.csv"
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """CSVファイルが存在しない場合は作成"""
        if not self.file_path.exists():
            with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'sentence', 'answer_kanji', 'reading', 'created_at', 'incorrect_count'])
    
    def save_problem(self, problem: Problem) -> bool:
        """問題を更新保存（未登録IDは追加しない）"""
        try:
            # 既存データを読み込み
            problems = self.load_problems()
            found = False
            for idx, p in enumerate(problems):
                if p.id == problem.id:
                    problems[idx] = problem
                    found = True
                    break
            if not found:
                # 未登録IDは追加しない
                return False

            # 全件を書き戻す（最新スキーマ）
            with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'sentence', 'answer_kanji', 'reading', 'created_at', 'incorrect_count'])
                for p in problems:
                    writer.writerow([
                        p.id,
                        p.sentence,
                        p.answer_kanji,
                        p.reading,
                        p.created_at.isoformat(),
                        p.incorrect_count,
                    ])
            return True
        except Exception as e:
            print(f"問題の保存に失敗しました: {e}")
            return False

    def delete_problem_once(self, problem_id: str) -> bool:
        """同一IDのレコードが複数存在する場合でも、最初の1件だけ削除する"""
        try:
            # 生のCSV行を扱って最初の一致のみ削除
            rows = []
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
            if not rows:
                return True
            header = rows[0]
            # id列のインデックスを特定（後方互換）
            try:
                id_idx = header.index('id')
            except ValueError:
                id_idx = 0
            removed = False
            new_rows = [header]
            for row in rows[1:]:
                if not removed and len(row) > id_idx and row[id_idx] == problem_id:
                    removed = True
                    continue
                new_rows.append(row)
            with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for r in new_rows:
                    writer.writerow(r)
            return True
        except Exception as e:
            print(f"問題の部分削除に失敗しました: {e}")
            return False
    
    def load_problems(self) -> List[Problem]:
        """問題一覧を読み込み（古いスキーマにも後方互換）"""
        problems: List[Problem] = []
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # 後方互換: incorrect_count がないCSVにも対応
                    if 'incorrect_count' not in row or row['incorrect_count'] == '' or row['incorrect_count'] is None:
                        row = {**row, 'incorrect_count': '0'}
                    problem = Problem.from_dict(row)
                    problems.append(problem)
        except Exception as e:
            print(f"問題の読み込みに失敗しました: {e}")
        return problems
    
    def delete_problem(self, problem_id: str) -> bool:
        """問題を削除"""
        try:
            problems = self.load_problems()
            problems = [p for p in problems if p.id != problem_id]
            
            with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'sentence', 'answer_kanji', 'reading', 'created_at', 'incorrect_count'])
                for problem in problems:
                    writer.writerow([
                        problem.id,
                        problem.sentence,
                        problem.answer_kanji,
                        problem.reading,
                        problem.created_at.isoformat(),
                        problem.incorrect_count,
                    ])
            return True
        except Exception as e:
            print(f"問題の削除に失敗しました: {e}")
            return False

class AttemptStorage:
    """試行データのCSV入出力"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.file_path = self.data_dir / "attempts.csv"
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """CSVファイルが存在しない場合は作成"""
        if not self.file_path.exists():
            with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'problem_id', 'attempted_at', 'is_correct'])
    
    def save_attempt(self, attempt: Attempt) -> bool:
        """試行を保存"""
        try:
            with open(self.file_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    attempt.id,
                    attempt.problem_id,
                    attempt.attempted_at.isoformat(),
                    attempt.is_correct
                ])
            return True
        except Exception as e:
            print(f"試行の保存に失敗しました: {e}")
            return False
    
    def load_attempts(self) -> List[Attempt]:
        """試行一覧を読み込み"""
        attempts = []
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    attempt = Attempt.from_dict(row)
                    attempts.append(attempt)
        except Exception as e:
            print(f"試行の読み込みに失敗しました: {e}")
        return attempts
    
    def get_attempts_by_problem(self, problem_id: str) -> List[Attempt]:
        """特定の問題の試行を取得"""
        attempts = self.load_attempts()
        return [a for a in attempts if a.problem_id == problem_id]
    
    def save_attempts_batch(self, attempts: List[Attempt]) -> int:
        """複数の試行を一括保存"""
        saved_count = 0
        try:
            for attempt in attempts:
                if self.save_attempt(attempt):
                    saved_count += 1
        except Exception as e:
            print(f"一括保存中にエラーが発生しました: {e}")
        return saved_count