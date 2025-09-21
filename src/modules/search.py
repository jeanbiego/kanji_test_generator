"""
問題検索機能モジュール

問題の検索・フィルタリング機能を提供する。
"""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from src.modules.models import Problem, Attempt
from src.modules.storage import ProblemStorage, AttemptStorage
from src.modules.logger import app_logger


class SearchEngine:
    """問題検索エンジン"""
    
    def __init__(self):
        self.problem_storage = ProblemStorage()
        self.attempt_storage = AttemptStorage()
    
    def search_problems(self, query: str, search_type: str = "all") -> List[Problem]:
        """
        問題を検索する
        
        Args:
            query: 検索クエリ
            search_type: 検索タイプ ("all", "problem_text", "answer", "reading")
        
        Returns:
            検索結果のProblemリスト
        """
        try:
            problems = self.problem_storage.load_problems()
            if not problems:
                return []
            
            if not query.strip():
                return problems
            
            query_lower = query.lower().strip()
            results = []
            
            for problem in problems:
                if self._matches_problem(problem, query_lower, search_type):
                    results.append(problem)
            
            app_logger.info(f"検索完了: クエリ='{query}', タイプ='{search_type}', 結果数={len(results)}")
            return results
            
        except Exception as e:
            app_logger.error(f"問題検索中にエラーが発生しました: {e}")
            return []
    
    def _matches_problem(self, problem: Problem, query: str, search_type: str) -> bool:
        """問題が検索条件に一致するかチェック"""
        try:
            if search_type == "all":
                return (self._contains_text(problem.sentence, query) or
                        self._contains_text(problem.answer_kanji, query) or
                        self._contains_text(problem.reading, query))
            elif search_type == "problem_text":
                return self._contains_text(problem.sentence, query)
            elif search_type == "answer":
                return self._contains_text(problem.answer_kanji, query)
            elif search_type == "reading":
                return self._contains_text(problem.reading, query)
            else:
                return False
        except Exception as e:
            app_logger.error(f"問題マッチング中にエラーが発生しました: {e}")
            return False
    
    def _contains_text(self, text: str, query: str) -> bool:
        """テキストにクエリが含まれているかチェック（部分一致）"""
        if not text:
            return False
        return query in text.lower()
    
    def search_with_regex(self, pattern: str, search_type: str = "all") -> List[Problem]:
        """
        正規表現で問題を検索する
        
        Args:
            pattern: 正規表現パターン
            search_type: 検索タイプ
        
        Returns:
            検索結果のProblemリスト
        """
        try:
            problems = self.problem_storage.load_problems()
            if not problems:
                return []
            
            if not pattern.strip():
                return problems
            
            results = []
            regex = re.compile(pattern, re.IGNORECASE)
            
            for problem in problems:
                if self._matches_regex(problem, regex, search_type):
                    results.append(problem)
            
            app_logger.info(f"正規表現検索完了: パターン='{pattern}', タイプ='{search_type}', 結果数={len(results)}")
            return results
            
        except re.error as e:
            app_logger.error(f"正規表現パターンが無効です: {e}")
            return []
        except Exception as e:
            app_logger.error(f"正規表現検索中にエラーが発生しました: {e}")
            return []
    
    def _matches_regex(self, problem: Problem, regex: re.Pattern, search_type: str) -> bool:
        """問題が正規表現に一致するかチェック"""
        try:
            if search_type == "all":
                return (regex.search(problem.sentence) or
                        regex.search(problem.answer_kanji) or
                        regex.search(problem.reading))
            elif search_type == "problem_text":
                return regex.search(problem.sentence)
            elif search_type == "answer":
                return regex.search(problem.answer_kanji)
            elif search_type == "reading":
                return regex.search(problem.reading)
            else:
                return False
        except Exception as e:
            app_logger.error(f"正規表現マッチング中にエラーが発生しました: {e}")
            return False


class FilterEngine:
    """問題フィルタリングエンジン"""
    
    def __init__(self):
        self.problem_storage = ProblemStorage()
        self.attempt_storage = AttemptStorage()
    
    def filter_by_date_range(self, problems: List[Problem], start_date: Optional[date], end_date: Optional[date]) -> List[Problem]:
        """日付範囲でフィルタリング"""
        try:
            if not start_date and not end_date:
                return problems
            
            filtered = []
            for problem in problems:
                problem_date = problem.created_at.date()
                
                if start_date and end_date:
                    if start_date <= problem_date <= end_date:
                        filtered.append(problem)
                elif start_date:
                    if problem_date >= start_date:
                        filtered.append(problem)
                elif end_date:
                    if problem_date <= end_date:
                        filtered.append(problem)
            
            app_logger.info(f"日付範囲フィルタリング完了: 開始={start_date}, 終了={end_date}, 結果数={len(filtered)}")
            return filtered
            
        except Exception as e:
            app_logger.error(f"日付範囲フィルタリング中にエラーが発生しました: {e}")
            return problems
    
    def filter_by_accuracy_range(self, problems: List[Problem], min_accuracy: Optional[float], max_accuracy: Optional[float]) -> List[Problem]:
        """正答率範囲でフィルタリング"""
        try:
            if min_accuracy is None and max_accuracy is None:
                return problems
            
            filtered = []
            attempts = self.attempt_storage.load_attempts()
            
            for problem in problems:
                problem_attempts = [a for a in attempts if a.problem_id == problem.id]
                if not problem_attempts:
                    continue
                
                correct_count = sum(1 for a in problem_attempts if a.is_correct)
                accuracy = (correct_count / len(problem_attempts)) * 100
                
                if min_accuracy is not None and max_accuracy is not None:
                    if min_accuracy <= accuracy <= max_accuracy:
                        filtered.append(problem)
                elif min_accuracy is not None:
                    if accuracy >= min_accuracy:
                        filtered.append(problem)
                elif max_accuracy is not None:
                    if accuracy <= max_accuracy:
                        filtered.append(problem)
            
            app_logger.info(f"正答率範囲フィルタリング完了: 最小={min_accuracy}, 最大={max_accuracy}, 結果数={len(filtered)}")
            return filtered
            
        except Exception as e:
            app_logger.error(f"正答率範囲フィルタリング中にエラーが発生しました: {e}")
            return problems
    
    def filter_by_attempt_count(self, problems: List[Problem], min_attempts: Optional[int], max_attempts: Optional[int]) -> List[Problem]:
        """試行回数範囲でフィルタリング"""
        try:
            if min_attempts is None and max_attempts is None:
                return problems
            
            filtered = []
            attempts = self.attempt_storage.load_attempts()
            
            for problem in problems:
                problem_attempts = [a for a in attempts if a.problem_id == problem.id]
                attempt_count = len(problem_attempts)
                
                if min_attempts is not None and max_attempts is not None:
                    if min_attempts <= attempt_count <= max_attempts:
                        filtered.append(problem)
                elif min_attempts is not None:
                    if attempt_count >= min_attempts:
                        filtered.append(problem)
                elif max_attempts is not None:
                    if attempt_count <= max_attempts:
                        filtered.append(problem)
            
            app_logger.info(f"試行回数範囲フィルタリング完了: 最小={min_attempts}, 最大={max_attempts}, 結果数={len(filtered)}")
            return filtered
            
        except Exception as e:
            app_logger.error(f"試行回数範囲フィルタリング中にエラーが発生しました: {e}")
            return problems
    
    def filter_by_mistake_type(self, problems: List[Problem], mistake_types: List[str]) -> List[Problem]:
        """間違いの種類でフィルタリング"""
        try:
            if not mistake_types:
                return problems
            
            filtered = []
            attempts = self.attempt_storage.load_attempts()
            
            for problem in problems:
                problem_attempts = [a for a in attempts if a.problem_id == problem.id]
                if not problem_attempts:
                    continue
                
                # 最新の試行の間違いの種類をチェック
                latest_attempt = max(problem_attempts, key=lambda x: x.timestamp)
                if latest_attempt.mistake_type in mistake_types:
                    filtered.append(problem)
            
            app_logger.info(f"間違いの種類フィルタリング完了: 種類={mistake_types}, 結果数={len(filtered)}")
            return filtered
            
        except Exception as e:
            app_logger.error(f"間違いの種類フィルタリング中にエラーが発生しました: {e}")
            return problems


class SearchManager:
    """検索機能の統合管理"""
    
    def __init__(self):
        self.search_engine = SearchEngine()
        self.filter_engine = FilterEngine()
    
    def advanced_search(self, 
                       query: str = "",
                       search_type: str = "all",
                       use_regex: bool = False,
                       start_date: Optional[date] = None,
                       end_date: Optional[date] = None,
                       min_accuracy: Optional[float] = None,
                       max_accuracy: Optional[float] = None,
                       min_attempts: Optional[int] = None,
                       max_attempts: Optional[int] = None,
                       mistake_types: Optional[List[str]] = None) -> List[Problem]:
        """
        高度な検索を実行する
        
        Args:
            query: 検索クエリ
            search_type: 検索タイプ
            use_regex: 正規表現を使用するか
            start_date: 開始日
            end_date: 終了日
            min_accuracy: 最小正答率
            max_accuracy: 最大正答率
            min_attempts: 最小試行回数
            max_attempts: 最大試行回数
            mistake_types: 間違いの種類リスト
        
        Returns:
            検索結果のProblemリスト
        """
        try:
            # 基本検索
            if use_regex and query:
                problems = self.search_engine.search_with_regex(query, search_type)
            elif query:
                problems = self.search_engine.search_problems(query, search_type)
            else:
                problems = self.search_engine.problem_storage.load_problems()
            
            if not problems:
                return []
            
            # フィルタリング
            problems = self.filter_engine.filter_by_date_range(problems, start_date, end_date)
            problems = self.filter_engine.filter_by_accuracy_range(problems, min_accuracy, max_accuracy)
            problems = self.filter_engine.filter_by_attempt_count(problems, min_attempts, max_attempts)
            
            if mistake_types:
                problems = self.filter_engine.filter_by_mistake_type(problems, mistake_types)
            
            app_logger.info(f"高度な検索完了: 結果数={len(problems)}")
            return problems
            
        except Exception as e:
            app_logger.error(f"高度な検索中にエラーが発生しました: {e}")
            return []
    
    def get_search_statistics(self, problems: List[Problem]) -> Dict[str, Any]:
        """検索結果の統計情報を取得"""
        try:
            if not problems:
                return {
                    "total_count": 0,
                    "average_accuracy": 0.0,
                    "total_attempts": 0,
                    "date_range": None
                }
            
            attempts = self.attempt_storage.load_attempts()
            problem_ids = [p.id for p in problems]
            problem_attempts = [a for a in attempts if a.problem_id in problem_ids]
            
            # 基本統計
            total_count = len(problems)
            total_attempts = len(problem_attempts)
            
            # 正答率の計算
            if problem_attempts:
                correct_count = sum(1 for a in problem_attempts if a.is_correct)
                average_accuracy = (correct_count / total_attempts) * 100
            else:
                average_accuracy = 0.0
            
            # 日付範囲
            if problems:
                dates = [p.created_at.date() for p in problems]
                date_range = {
                    "earliest": min(dates),
                    "latest": max(dates)
                }
            else:
                date_range = None
            
            return {
                "total_count": total_count,
                "average_accuracy": round(average_accuracy, 2),
                "total_attempts": total_attempts,
                "date_range": date_range
            }
            
        except Exception as e:
            app_logger.error(f"検索統計取得中にエラーが発生しました: {e}")
            return {
                "total_count": 0,
                "average_accuracy": 0.0,
                "total_attempts": 0,
                "date_range": None
            }
