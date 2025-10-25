"""
データ整合性ヘルスチェック
"""

from typing import List, Dict, Tuple
from .storage import ProblemStorage, AttemptStorage
from .models import Problem, Attempt

class HealthCheckResult:
    """ヘルスチェック結果"""
    def __init__(self):
        self.has_issues = False
        self.duplicate_problem_ids: List[str] = []
        self.duplicate_attempt_ids: List[str] = []
        self.orphaned_attempts: List[Tuple[str, str]] = []  # (attempt_id, problem_id)
        self.invalid_boolean_values: List[str] = []
        self.total_problems = 0
        self.total_attempts = 0
    
    def get_summary(self) -> str:
        """サマリーメッセージを取得"""
        if not self.has_issues:
            return "✅ データに問題はありません"
        
        messages = ["⚠️ データに以下の問題が見つかりました："]
        
        if self.duplicate_problem_ids:
            messages.append(f"- 重複問題ID: {len(self.duplicate_problem_ids)}件")
        
        if self.duplicate_attempt_ids:
            messages.append(f"- 重複試行ID: {len(self.duplicate_attempt_ids)}件")
        
        if self.orphaned_attempts:
            messages.append(f"- 孤立試行データ: {len(self.orphaned_attempts)}件")
        
        if self.invalid_boolean_values:
            messages.append(f"- 不正な真偽値: {len(self.invalid_boolean_values)}件")
        
        return "\n".join(messages)

def run_health_check(problem_storage: ProblemStorage, attempt_storage: AttemptStorage) -> HealthCheckResult:
    """ヘルスチェックを実行"""
    result = HealthCheckResult()
    
    # 問題データの読み込み（生データ）
    import csv
    problem_ids = set()
    duplicate_problem_ids = set()
    
    try:
        with open(problem_storage.file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                pid = row.get('id', '')
                if pid:
                    if pid in problem_ids:
                        duplicate_problem_ids.add(pid)
                    problem_ids.add(pid)
        result.total_problems = len(problem_ids)
        result.duplicate_problem_ids = list(duplicate_problem_ids)
    except Exception as e:
        print(f"問題データのチェックに失敗: {e}")
    
    # 試行データの読み込み（生データ）
    attempt_ids = set()
    duplicate_attempt_ids = set()
    orphaned_attempts = []
    invalid_boolean_values = []
    
    try:
        with open(attempt_storage.file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                aid = row.get('id', '')
                pid = row.get('problem_id', '')
                is_correct = row.get('is_correct', '')
                
                # ID重複チェック
                if aid:
                    if aid in attempt_ids:
                        duplicate_attempt_ids.add(aid)
                    attempt_ids.add(aid)
                
                # 外部キーチェック
                if pid and pid not in problem_ids:
                    orphaned_attempts.append((aid, pid))
                
                # 真偽値チェック
                if is_correct not in ['True', 'False', 'true', 'false', '1', '0']:
                    invalid_boolean_values.append(aid)
        
        result.total_attempts = len(attempt_ids)
        result.duplicate_attempt_ids = list(duplicate_attempt_ids)
        result.orphaned_attempts = orphaned_attempts
        result.invalid_boolean_values = invalid_boolean_values
    except Exception as e:
        print(f"試行データのチェックに失敗: {e}")
    
    # 問題の有無を判定
    result.has_issues = bool(
        result.duplicate_problem_ids or 
        result.duplicate_attempt_ids or 
        result.orphaned_attempts or 
        result.invalid_boolean_values
    )
    
    return result
