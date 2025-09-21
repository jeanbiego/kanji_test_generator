"""
Streamlitエントリーポイント
メインアプリケーションの起動とページ構成の管理
"""

import streamlit as st
from src.modules.models import Problem, Attempt
from src.modules.storage import ProblemStorage, AttemptStorage
from src.modules.rendering import TextRenderer
from src.modules.validators import InputValidator
from src.modules.utils import get_current_datetime

def main():
    """メインアプリケーション"""
    st.set_page_config(
        page_title="Kanji Test Generator",
        page_icon="📝",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📝 Kanji Test Generator")
    st.markdown("小学生向け漢字テスト自動作成アプリケーション")
    
    # セッション状態の初期化
    if 'problems' not in st.session_state:
        st.session_state.problems = []
    if 'problem_storage' not in st.session_state:
        st.session_state.problem_storage = ProblemStorage()
    if 'attempt_storage' not in st.session_state:
        st.session_state.attempt_storage = AttemptStorage()
    
    # サイドバーでページ選択
    page = st.sidebar.selectbox(
        "ページを選択",
        ["問題作成", "印刷用ページ表示", "採点", "履歴管理"]
    )
    
    # ページに応じた表示
    if page == "問題作成":
        show_problem_creation_page()
    elif page == "印刷用ページ表示":
        show_print_page()
    elif page == "採点":
        show_scoring_page()
    elif page == "履歴管理":
        show_history_page()

def show_problem_creation_page():
    """問題作成ページの表示"""
    st.header("📝 問題作成")
    
    # 問題入力フォーム
    with st.form("problem_form"):
        st.subheader("新しい問題を追加")
        
        sentence = st.text_area(
            "問題文",
            placeholder="例：独創的な表現で知られるアーティスト",
            help="漢字を含む文章を入力してください",
            height=100
        )
        
        col1, col2 = st.columns(2)
        with col1:
            answer_kanji = st.text_input(
                "回答漢字",
                placeholder="例：独創",
                help="問題文に含まれる漢字を入力してください"
            )
        with col2:
            reading = st.text_input(
                "読み",
                placeholder="例：どくそう",
                help="ひらがなまたはカタカナで入力してください"
            )
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("問題を追加", type="primary")
        with col2:
            reset_submitted = st.form_submit_button("リセット", type="secondary")
        
        if reset_submitted:
            st.rerun()
        
        if submitted:
            # バリデーション
            validator = InputValidator()
            validation_result = validator.validate_problem(sentence, answer_kanji, reading)
            
            if validation_result.is_valid:
                # 問題を作成
                problem = Problem(
                    sentence=sentence,
                    answer_kanji=answer_kanji,
                    reading=reading
                )
                st.session_state.problems.append(problem)
                st.success("✅ 問題を追加しました！")
                st.rerun()
            else:
                for error in validation_result.errors:
                    st.error(f"❌ {error}")
    
    # 問題一覧の表示
    if st.session_state.problems:
        st.subheader(f"📋 作成中の問題一覧 ({len(st.session_state.problems)}問)")
        
        # 一括操作ボタン
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("💾 すべて保存", type="secondary"):
                save_all_problems()
        with col2:
            if st.button("🗑️ すべて削除", type="secondary"):
                st.session_state.problems = []
                st.rerun()
        with col3:
            if st.button("📄 印刷用ページ表示", type="primary"):
                st.session_state.show_print_page = True
                st.rerun()
        
        # 問題一覧表示
        for i, problem in enumerate(st.session_state.problems):
            with st.expander(f"問題 {i+1}: {problem.answer_kanji} ({problem.reading})"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**問題文**: {problem.sentence}")
                    st.write(f"**回答漢字**: {problem.answer_kanji}")
                    st.write(f"**読み**: {problem.reading}")
                    
                    # プレビュー表示
                    renderer = TextRenderer()
                    preview = renderer.create_preview(problem)
                    st.write(f"**プレビュー**: {preview}")
                
                with col2:
                    if st.button(f"🗑️ 削除", key=f"delete_{i}"):
                        st.session_state.problems.pop(i)
                        st.rerun()
    else:
        st.info("📝 まだ問題がありません。上記のフォームから問題を追加してください。")

def save_all_problems():
    """すべての問題を保存"""
    if not st.session_state.problems:
        st.warning("保存する問題がありません。")
        return
    
    try:
        for problem in st.session_state.problems:
            st.session_state.problem_storage.save_problem(problem)
        st.success(f"✅ {len(st.session_state.problems)}問の問題を保存しました！")
    except Exception as e:
        st.error(f"❌ 保存に失敗しました: {e}")

def show_print_page():
    """印刷用ページ表示"""
    st.header("🖨️ 印刷用ページ表示")
    
    if not st.session_state.problems:
        st.warning("印刷する問題がありません。問題作成ページで問題を追加してください。")
        return
    
    # 印刷設定
    col1, col2 = st.columns(2)
    with col1:
        questions_per_page = st.number_input(
            "1ページあたりの問題数",
            min_value=1,
            max_value=20,
            value=10
        )
    with col2:
        title = st.text_input(
            "テストタイトル",
            value="漢字テスト"
        )
    
    # 印刷用ページ生成
    if st.button("🖨️ 印刷用ページを表示", type="primary"):
        try:
            from src.modules.print_page import PrintPageGenerator
            
            generator = PrintPageGenerator()
            html_content = generator.generate_print_page(
                st.session_state.problems,
                title,
                questions_per_page
            )
            
            # HTMLを表示
            st.components.v1.html(html_content, height=600, scrolling=True)
            
        except Exception as e:
            st.error(f"❌ 印刷用ページの生成に失敗しました: {e}")

def show_scoring_page():
    """採点ページ"""
    st.header("📊 採点")
    st.info("採点機能は今後実装予定です。")

def show_history_page():
    """履歴管理ページ"""
    st.header("📚 履歴管理")
    st.info("履歴管理機能は今後実装予定です。")

if __name__ == "__main__":
    main()
