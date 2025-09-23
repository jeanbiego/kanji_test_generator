"""
データクラス・型定義・ID採番
"""

import uuid
from datetime import datetime
from dataclasses import dataclass
from typing import Optional
from .utils import normalize_reading

@dataclass
class Problem:
    """問題データの管理"""
    id: str
    sentence: str
    answer_kanji: str
    reading: str
    created_at: datetime
    incorrect_count: int
    
    def __init__(self, sentence: str, answer_kanji: str, reading: str, 
                 id: Optional[str] = None, created_at: Optional[datetime] = None, 
                 incorrect_count: int = 0):
        self.id = id or str(uuid.uuid4())
        self.sentence = sentence
        self.answer_kanji = answer_kanji
        self.reading = normalize_reading(reading)
        self.created_at = created_at or datetime.now()
        self.incorrect_count = max(0, incorrect_count)  # 最低値は0
    
    def increment_incorrect_count(self) -> None:
        """不正解数を1増やす"""
        self.incorrect_count += 1
    
    def decrement_incorrect_count(self) -> None:
        """不正解数を1減らす（最低値は0）"""
        self.incorrect_count = max(0, self.incorrect_count - 1)
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            'id': self.id,
            'sentence': self.sentence,
            'answer_kanji': self.answer_kanji,
            'reading': self.reading,
            'created_at': self.created_at.isoformat(),
            'incorrect_count': self.incorrect_count
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Problem':
        """辞書から作成"""
        return cls(
            id=data['id'],
            sentence=data['sentence'],
            answer_kanji=data['answer_kanji'],
            reading=data['reading'],
            created_at=datetime.fromisoformat(data['created_at']),
            incorrect_count=data.get('incorrect_count', 0)  # 後方互換性のためデフォルト値0
        )

@dataclass
class Attempt:
    """試行データの管理"""
    id: str
    problem_id: str
    attempted_at: datetime
    is_correct: bool
    mistake_type: str
    learning_memo: str
    timestamp: datetime
    
    def __init__(self, problem_id: str, is_correct: bool, mistake_type: str = "なし", learning_memo: str = "",
                 id: Optional[str] = None, attempted_at: Optional[datetime] = None, timestamp: Optional[datetime] = None):
        self.id = id or str(uuid.uuid4())
        self.problem_id = problem_id
        self.attempted_at = attempted_at or datetime.now()
        self.is_correct = is_correct
        self.mistake_type = mistake_type
        self.learning_memo = learning_memo
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            'id': self.id,
            'problem_id': self.problem_id,
            'attempted_at': self.attempted_at.isoformat(),
            'is_correct': self.is_correct,
            'mistake_type': self.mistake_type,
            'learning_memo': self.learning_memo,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Attempt':
        """辞書から作成"""
        return cls(
            id=data['id'],
            problem_id=data['problem_id'],
            is_correct=data['is_correct'] == 'True' if isinstance(data['is_correct'], str) else bool(data['is_correct']),
            attempted_at=datetime.fromisoformat(data['attempted_at']),
            mistake_type=data.get('mistake_type', 'なし'),
            learning_memo=data.get('learning_memo', ''),
            timestamp=datetime.fromisoformat(data.get('timestamp', data['attempted_at']))
        )
