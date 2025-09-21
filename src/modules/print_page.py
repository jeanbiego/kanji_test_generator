"""
印刷用ページ生成機能
"""

import os
from datetime import datetime
from typing import List, Dict, Any
from jinja2 import Environment, FileSystemLoader
from src.modules.models import Problem
from src.modules.rendering import TextRenderer

class PrintPageGenerator:
    """印刷用ページ生成クラス"""
    
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = templates_dir
        self.renderer = TextRenderer()
        self._setup_jinja2()
    
    def _setup_jinja2(self):
        """Jinja2環境の設定"""
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            autoescape=True
        )
    
    def generate_print_page(
        self, 
        problems: List[Problem], 
        title: str = "漢字テスト",
        questions_per_page: int = 10
    ) -> str:
        """印刷用ページのHTMLを生成"""
        
        # 問題をページごとに分割
        pages = self._split_problems_into_pages(problems, questions_per_page)
        
        # 各ページのHTMLを生成
        page_htmls = []
        for i, page_problems in enumerate(pages, 1):
            page_html = self._generate_single_page(
                page_problems, 
                title, 
                i, 
                len(pages)
            )
            page_htmls.append(page_html)
        
        return "\n".join(page_htmls)
    
    def _split_problems_into_pages(
        self, 
        problems: List[Problem], 
        questions_per_page: int
    ) -> List[List[Problem]]:
        """問題をページごとに分割"""
        pages = []
        for i in range(0, len(problems), questions_per_page):
            page_problems = problems[i:i + questions_per_page]
            pages.append(page_problems)
        return pages
    
    def _generate_single_page(
        self, 
        problems: List[Problem], 
        title: str, 
        page_num: int, 
        total_pages: int
    ) -> str:
        """単一ページのHTMLを生成"""
        
        # 問題データを準備
        question_data = []
        for problem in problems:
            # プレビュー文字列を生成（漢字→ひらがな変換）
            preview_text = self.renderer.create_preview(problem)
            # ひらがな部分を太字にする
            formatted_text = self._format_problem_text(preview_text, problem.reading)
            question_data.append({
                'formatted_text': formatted_text,
                'answer_kanji': problem.answer_kanji,
                'reading': problem.reading
            })
        
        # テンプレートデータを準備
        template_data = {
            'title': title,
            'date': datetime.now().strftime('%Y年%m月%d日'),
            'questions': question_data,
            'page': page_num,
            'total_pages': total_pages
        }
        
        # テンプレートをレンダリング
        template = self.jinja_env.get_template('print_page.html')
        return template.render(**template_data)
    
    def _format_problem_text(self, sentence: str, answer_kanji: str) -> str:
        """
        問題文で漢字部分を太字にする
        
        Args:
            sentence: 問題文
            answer_kanji: 回答漢字
            
        Returns:
            フォーマットされた問題文（HTML）
        """
        if answer_kanji in sentence:
            # 漢字部分を太字で囲む
            formatted = sentence.replace(answer_kanji, f'<strong>{answer_kanji}</strong>')
            return formatted
        else:
            # 漢字が見つからない場合はそのまま返す
            return sentence
    
    def save_print_page(
        self, 
        problems: List[Problem], 
        output_path: str,
        title: str = "漢字テスト",
        questions_per_page: int = 10
    ) -> bool:
        """印刷用ページをファイルに保存"""
        try:
            html_content = self.generate_print_page(
                problems, title, questions_per_page
            )
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return True
        except Exception as e:
            print(f"印刷用ページの保存に失敗しました: {e}")
            return False
    
    def get_print_page_url(
        self, 
        problems: List[Problem], 
        title: str = "漢字テスト",
        questions_per_page: int = 10
    ) -> str:
        """印刷用ページのURLを生成（Streamlit用）"""
        # 一時ファイルに保存してURLを返す
        import tempfile
        import uuid
        
        temp_dir = tempfile.gettempdir()
        temp_filename = f"kanji_test_{uuid.uuid4().hex}.html"
        temp_path = os.path.join(temp_dir, temp_filename)
        
        if self.save_print_page(problems, temp_path, title, questions_per_page):
            return f"file://{temp_path}"
        else:
            return ""

