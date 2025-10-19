"""
入力バリデーション
"""

from dataclasses import dataclass
from typing import List
from .utils import validate_reading_format, contains_kanji

@dataclass
class ValidationResult:
    """バリデーション結果"""
    is_valid: bool
    errors: List[str]
    
    def __init__(self, is_valid: bool = True, errors: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []

class InputValidator:
    """入力バリデーションクラス"""
    
    def validate_problem(self, sentence: str, answer_kanji: str, reading: str) -> ValidationResult:
        """問題のバリデーション"""
        errors = []
        
        # 文章のチェック
        if not sentence or not sentence.strip():
            errors.append("問題文を入力してください")
        elif not contains_kanji(sentence):
            errors.append("問題文に漢字が含まれていません")
        
        # 回答漢字のチェック
        if not answer_kanji or not answer_kanji.strip():
            errors.append("回答漢字を入力してください")
        elif not contains_kanji(answer_kanji):
            errors.append("回答漢字は漢字である必要があります")
        elif sentence and answer_kanji not in sentence:
            errors.append("回答漢字が問題文に含まれていません")
        
        # 読みのチェック
        if not reading or not reading.strip():
            errors.append("読みを入力してください")
        elif not validate_reading_format(reading):
            errors.append("読みはひらがなまたはカタカナで入力してください")
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
    
    def validate_sentence(self, sentence: str) -> ValidationResult:
        """文章のバリデーション"""
        errors = []
        
        if not sentence or not sentence.strip():
            errors.append("問題文を入力してください")
        elif not contains_kanji(sentence):
            errors.append("問題文に漢字が含まれていません")
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
    
    def validate_answer_kanji(self, answer_kanji: str, sentence: str = "") -> ValidationResult:
        """回答漢字のバリデーション"""
        errors = []
        
        if not answer_kanji or not answer_kanji.strip():
            errors.append("回答漢字を入力してください")
        elif not contains_kanji(answer_kanji):
            errors.append("回答漢字は漢字である必要があります")
        elif sentence and answer_kanji not in sentence:
            errors.append("回答漢字が問題文に含まれていません")
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
    
    def validate_reading(self, reading: str) -> ValidationResult:
        """読みのバリデーション"""
        errors = []
        
        if not reading or not reading.strip():
            errors.append("読みを入力してください")
        elif not validate_reading_format(reading):
            errors.append("読みはひらがなまたはカタカナで入力してください")
        
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)
