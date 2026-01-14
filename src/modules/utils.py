"""
共通処理
"""

import re
from datetime import datetime


def get_current_datetime() -> datetime:
    """現在の日時を取得"""
    return datetime.now()


def normalize_reading(reading: str) -> str:
    """読みをカタカナに正規化"""
    if not reading:
        return ""

    # ひらがなをカタカナに変換
    katakana = ""
    for char in reading:
        if "あ" <= char <= "ん":
            # ひらがなをカタカナに変換
            katakana += chr(ord(char) - ord("あ") + ord("ア"))
        else:
            katakana += char

    return katakana


def validate_reading_format(reading: str) -> bool:
    """読みの形式をチェック(ひらがな/カタカナ)"""
    if not reading:
        return False

    # ひらがなまたはカタカナのみかチェック
    pattern = r"^[あ-んア-ン]+$"
    return bool(re.match(pattern, reading))


def contains_kanji(text: str) -> bool:
    """テキストに漢字が含まれているかチェック"""
    pattern = r"[一-龯]"
    return bool(re.search(pattern, text))


def extract_kanji(text: str) -> list:
    """テキストから漢字を抽出"""
    pattern = r"[一-龯]"
    return re.findall(pattern, text)
