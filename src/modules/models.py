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
    
    def __init__(self, sentence: str, answer_kanji: str, reading: str, 
                 id: Optional[str] = None, created_at: Optional[datetime] = None):
        self.id = id or str(uuid.uuid4())
        self.sentence = sentence
        self.answer_kanji = answer_kanji
        self.reading = normalize_reading(reading)
        self.created_at = created_at or datetime.now()
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            'id': self.id,
            'sentence': self.sentence,
            'answer_kanji': self.answer_kanji,
            'reading': self.reading,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Problem':
        """辞書から作成"""
        return cls(
            id=data['id'],
            sentence=data['sentence'],
            answer_kanji=data['answer_kanji'],
            reading=data['reading'],
            created_at=datetime.fromisoformat(data['created_at'])
        )

@dataclass
class Attempt:
    """試行データの管理"""
    id: str
    problem_id: str
    attempted_at: datetime
    is_correct: bool
    
    def __init__(self, problem_id: str, is_correct: bool, 
                 id: Optional[str] = None, attempted_at: Optional[datetime] = None):
        self.id = id or str(uuid.uuid4())
        self.problem_id = problem_id
        self.attempted_at = attempted_at or datetime.now()
        self.is_correct = is_correct
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            'id': self.id,
            'problem_id': self.problem_id,
            'attempted_at': self.attempted_at.isoformat(),
            'is_correct': self.is_correct
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Attempt':
        """辞書から作成"""
        return cls(
            id=data['id'],
            problem_id=data['problem_id'],
            is_correct=data['is_correct'] == 'True' if isinstance(data['is_correct'], str) else bool(data['is_correct']),
            attempted_at=datetime.fromisoformat(data['attempted_at'])
        )
