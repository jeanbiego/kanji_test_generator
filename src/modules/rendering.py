"""
置換・プレビュー機能
"""

from typing import List
from .models import Problem

class TextRenderer:
    """テキストレンダリングクラス"""
    
    def create_preview(self, problem: Problem) -> str:
        """プレビュー文字列を生成（漢字→カタカナ置換）"""
        if not problem.sentence or not problem.answer_kanji:
            return problem.sentence
        
        # 回答漢字をカタカナ読みに置換
        preview = problem.sentence.replace(problem.answer_kanji, problem.reading)
        return preview
    
    def create_preview_with_blank(self, problem: Problem) -> str:
        """プレビュー文字列を生成（漢字→空白置換）"""
        if not problem.sentence or not problem.answer_kanji:
            return problem.sentence
        
        # 回答漢字を空白に置換
        blank = "　" * len(problem.answer_kanji)  # 全角空白で置換
        preview = problem.sentence.replace(problem.answer_kanji, blank)
        return preview
    
    def create_preview_with_underline(self, problem: Problem) -> str:
        """プレビュー文字列を生成（漢字→下線付き空白）"""
        if not problem.sentence or not problem.answer_kanji:
            return problem.sentence
        
        # 回答漢字を下線付き空白に置換
        blank = "　" * len(problem.answer_kanji)
        underline = "＿" * len(problem.answer_kanji)
        preview = problem.sentence.replace(problem.answer_kanji, f"{blank}\n{underline}")
        return preview
    
    def create_problem_display(self, problem: Problem, show_answer: bool = False) -> str:
        """問題表示用文字列を生成"""
        if show_answer:
            return f"{problem.sentence} → {problem.answer_kanji}（{problem.reading}）"
        else:
            return self.create_preview(problem)
    
    def create_problems_preview(self, problems: List[Problem]) -> List[str]:
        """複数問題のプレビューを生成"""
        return [self.create_preview(problem) for problem in problems]
