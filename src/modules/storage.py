"""
CSV入出力機能
"""

import csv
import tempfile
import shutil
from pathlib import Path
from typing import List
from .models import Problem, Attempt
from .logger import app_logger

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
    
    def _atomic_write_csv(self, file_path: Path, header: List[str], rows: List[List]) -> bool:
        """一時ファイル経由でアトミックにCSVを書き込む"""
        tmp_path = None
        try:
            # 一時ファイルに書き込み
            with tempfile.NamedTemporaryFile(
                mode='w', 
                newline='', 
                encoding='utf-8', 
                delete=False,
                dir=file_path.parent,
                suffix='.tmp'
            ) as tmp_file:
                writer = csv.writer(tmp_file)
                writer.writerow(header)
                writer.writerows(rows)
                tmp_path = Path(tmp_file.name)
            
            # 一時ファイルを本ファイルに置換（アトミック操作）
            shutil.move(str(tmp_path), str(file_path))
            return True
            
        except Exception as e:
            print(f"アトミック書き込みに失敗しました: {e}")
            # 一時ファイルのクリーンアップ
            if tmp_path and tmp_path.exists():
                tmp_path.unlink()
            return False
    
    def save_problem(self, problem: Problem) -> bool:
        """新規問題を追加（全体再書き込み方式）"""
        try:
            # 既存問題を読み込み
            problems = self.load_problems()
            
            # ID重複チェック
            if any(p.id == problem.id for p in problems):
                app_logger.warning(f"ID重複検出: {problem.id}")
                print(f"ID重複エラー: {problem.id} は既に存在します")
                return False
            
            # 新規問題を追加
            problems.append(problem)
            
            # 全体を再書き込み
            header = ['id', 'sentence', 'answer_kanji', 'reading', 'created_at', 'incorrect_count']
            rows = [
                [p.id, p.sentence, p.answer_kanji, p.reading, p.created_at.isoformat(), p.incorrect_count]
                for p in problems
            ]
            
            success = self._atomic_write_csv(self.file_path, header, rows)
            if success:
                app_logger.info(f"問題を保存: ID={problem.id}, 漢字={problem.answer_kanji}")
            return success
            
        except Exception as e:
            print(f"問題の保存に失敗しました: {e}")
            return False

    def update_problem(self, problem: Problem) -> bool:
        """既存問題を更新（全体再書き込み方式）"""
        try:
            problems = self.load_problems()
            
            # 該当問題を検索して更新
            updated = False
            for i, p in enumerate(problems):
                if p.id == problem.id:
                    problems[i] = problem
                    updated = True
                    break
            
            if not updated:
                print(f"更新エラー: ID {problem.id} が見つかりません")
                return False
            
            # 全体を再書き込み
            header = ['id', 'sentence', 'answer_kanji', 'reading', 'created_at', 'incorrect_count']
            rows = [
                [p.id, p.sentence, p.answer_kanji, p.reading, p.created_at.isoformat(), p.incorrect_count]
                for p in problems
            ]
            
            success = self._atomic_write_csv(self.file_path, header, rows)
            if success:
                app_logger.info(f"問題を更新: ID={problem.id}")
            return success
            
        except Exception as e:
            print(f"問題の更新に失敗しました: {e}")
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
        """問題一覧を読み込み（重複自動解消付き）"""
        problems: List[Problem] = []
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            # ID重複を解消: 同一IDの場合は created_at が最新のものを採用
            id_to_rows = {}
            for row in rows:
                row_id = row.get('id', '')
                if not row_id:
                    continue
                
                # 後方互換: incorrect_count がない場合は 0 を設定
                if 'incorrect_count' not in row or row['incorrect_count'] == '' or row['incorrect_count'] is None:
                    row['incorrect_count'] = '0'
                
                # 既存IDがある場合は created_at を比較
                if row_id in id_to_rows:
                    from datetime import datetime
                    existing_created_at = datetime.fromisoformat(id_to_rows[row_id]['created_at'])
                    new_created_at = datetime.fromisoformat(row['created_at'])
                    if new_created_at > existing_created_at:
                        id_to_rows[row_id] = row
                else:
                    id_to_rows[row_id] = row
            
            # Problem オブジェクトに変換
            for row in id_to_rows.values():
                problem = Problem.from_dict(row)
                problems.append(problem)
            
            # created_at でソート（古い順）
            problems.sort(key=lambda p: p.created_at)
            
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
    
    def _atomic_write_csv(self, file_path: Path, header: List[str], rows: List[List]) -> bool:
        """一時ファイル経由でアトミックにCSVを書き込む"""
        tmp_path = None
        try:
            # 一時ファイルに書き込み
            with tempfile.NamedTemporaryFile(
                mode='w', 
                newline='', 
                encoding='utf-8', 
                delete=False,
                dir=file_path.parent,
                suffix='.tmp'
            ) as tmp_file:
                writer = csv.writer(tmp_file)
                writer.writerow(header)
                writer.writerows(rows)
                tmp_path = Path(tmp_file.name)
            
            # 一時ファイルを本ファイルに置換（アトミック操作）
            shutil.move(str(tmp_path), str(file_path))
            return True
            
        except Exception as e:
            print(f"アトミック書き込みに失敗しました: {e}")
            # 一時ファイルのクリーンアップ
            if tmp_path and tmp_path.exists():
                tmp_path.unlink()
            return False
    
    def save_attempt(self, attempt: Attempt) -> bool:
        """試行を保存（全体再書き込み方式）"""
        try:
            attempts = self.load_attempts()
            
            # ID重複チェック
            if any(a.id == attempt.id for a in attempts):
                app_logger.warning(f"試行ID重複検出: {attempt.id}")
                print(f"ID重複エラー: {attempt.id} は既に存在します")
                return False
            
            attempts.append(attempt)
            
            # 全体を再書き込み
            header = ['id', 'problem_id', 'attempted_at', 'is_correct']
            rows = [
                [a.id, a.problem_id, a.attempted_at.isoformat(), a.is_correct]
                for a in attempts
            ]
            
            success = self._atomic_write_csv(self.file_path, header, rows)
            if success:
                app_logger.info(f"試行を保存: ID={attempt.id}, 問題ID={attempt.problem_id}, 正解={attempt.is_correct}")
            return success
            
        except Exception as e:
            print(f"試行の保存に失敗しました: {e}")
            return False
    
    def load_attempts(self) -> List[Attempt]:
        """試行一覧を読み込み（ID重複自動解消付き）"""
        attempts = []
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            # ID重複を解消: 同一IDの場合は最終行を採用
            id_to_row = {}
            for row in rows:
                row_id = row.get('id', '')
                if not row_id:
                    continue
                id_to_row[row_id] = row
            
            # Attempt オブジェクトに変換
            for row in id_to_row.values():
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