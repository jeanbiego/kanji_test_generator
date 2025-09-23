"""
Streamlitエントリーポイント
メインアプリケーションの起動とページ構成の管理
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from modules.models import Problem, Attempt
from modules.storage import ProblemStorage, AttemptStorage
from modules.rendering import TextRenderer
from modules.validators import InputValidator
from modules.utils import get_current_datetime
from modules.logger import app_logger
from modules.error_handler import ErrorHandler, error_handler, safe_execute

@error_handler("アプリケーション初期化中")
def main():
    """メインアプリケーション"""
    try:
        st.set_page_config(
            page_title="Kanji Test Generator",
            page_icon="📝",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        st.title("📝 Kanji Test Generator")
        st.markdown("小学生向け漢字テスト自動作成アプリケーション")
        
        app_logger.info("アプリケーション開始")
    except Exception as e:
        ErrorHandler.handle_error(e, "アプリケーション初期化中")
        return
    
    # セッション状態の初期化
    if 'problems' not in st.session_state:
        st.session_state.problems = []
    if 'problem_storage' not in st.session_state:
        st.session_state.problem_storage = ProblemStorage()
    if 'attempt_storage' not in st.session_state:
        st.session_state.attempt_storage = AttemptStorage()
    if 'printed_problems' not in st.session_state:
        st.session_state.printed_problems = []
    if 'scoring_results' not in st.session_state:
        st.session_state.scoring_results = {}
    
    # サイドバーでページ選択（常時表示）
    st.sidebar.title("📝 メニュー")
    
    # 現在のページを取得（デフォルトは問題登録）
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "問題登録"
    
    # ページ選択ボタン
    if st.sidebar.button("📝 問題登録", use_container_width=True):
        st.session_state.current_page = "問題登録"
        st.rerun()
    
    if st.sidebar.button("🖨️ 問題用紙作成", use_container_width=True):
        st.session_state.current_page = "問題用紙作成"
        st.rerun()
    
    if st.sidebar.button("✅ 採点", use_container_width=True):
        st.session_state.current_page = "採点"
        st.rerun()
    
    if st.sidebar.button("📊 履歴管理", use_container_width=True):
        st.session_state.current_page = "履歴管理"
        st.rerun()
    
    if st.sidebar.button("🔍 問題検索", use_container_width=True):
        st.session_state.current_page = "問題検索"
        st.rerun()
    
    if st.sidebar.button("📈 統計", use_container_width=True):
        st.session_state.current_page = "統計"
        st.rerun()
    
    
    page = st.session_state.current_page
    
    # ページに応じた表示
    if page == "問題登録":
        show_problem_creation_page()
    elif page == "問題用紙作成":
        show_print_page()
    elif page == "採点":
        show_scoring_page()
    elif page == "履歴管理":
        show_history_page()
    elif page == "問題検索":
        show_search_page()
    elif page == "統計":
        show_statistics_page()

def show_problem_creation_page():
    """問題登録ページの表示"""
    st.header("📝 問題登録")
    
    
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
            # フォームをリセットするためにページを再読み込み
            # 重複状態はリセットしない（ユーザーが確認できるように）
            st.rerun()
        
        if submitted:
            # バリデーション
            validator = InputValidator()
            validation_result = validator.validate_problem(sentence, answer_kanji, reading)
            
            if validation_result.is_valid:
                # 重複チェック
                is_duplicate, duplicate_message = check_duplicate_problem(sentence, answer_kanji, reading)
                
                if is_duplicate:
                    # 重複が検出された場合、セッション状態に保存
                    st.session_state.duplicate_detected = True
                    st.session_state.duplicate_message = duplicate_message
                    st.session_state.pending_problem = {
                        'sentence': sentence,
                        'answer_kanji': answer_kanji,
                        'reading': reading
                    }
                    # フォーム内で重複警告を表示
                    st.warning(f"⚠️ 重複の可能性: {duplicate_message}")
                else:
                    # 重複がない場合、問題を追加
                    problem = Problem(
                        sentence=sentence,
                        answer_kanji=answer_kanji,
                        reading=reading
                    )
                    st.session_state.problems.append(problem)
                    st.success("✅ 問題を追加しました！")
                    # 重複状態をリセット
                    if 'duplicate_detected' in st.session_state:
                        del st.session_state.duplicate_detected
                    if 'duplicate_message' in st.session_state:
                        del st.session_state.duplicate_message
                    if 'pending_problem' in st.session_state:
                        del st.session_state.pending_problem
                    st.rerun()
            else:
                for error in validation_result.errors:
                    st.error(f"❌ {error}")
    
    # 重複警告とボタン（フォームの外）
    if st.session_state.get('duplicate_detected', False):
        st.warning(f"⚠️ 重複の可能性: {st.session_state.duplicate_message}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 それでも追加する", type="secondary"):
                # 問題を作成して追加
                problem = Problem(
                    sentence=st.session_state.pending_problem['sentence'],
                    answer_kanji=st.session_state.pending_problem['answer_kanji'],
                    reading=st.session_state.pending_problem['reading']
                )
                st.session_state.problems.append(problem)
                st.success("✅ 問題を強制追加しました！")
                # 重複状態をリセット
                st.session_state.duplicate_detected = False
                st.session_state.duplicate_message = ""
                st.session_state.pending_problem = {}
                st.rerun()
        with col2:
            if st.button("❌ キャンセル"):
                st.info("問題の追加をキャンセルしました。")
                # 重複状態をリセット
                st.session_state.duplicate_detected = False
                st.session_state.duplicate_message = ""
                st.session_state.pending_problem = {}
                st.rerun()

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
            if st.button("📄 問題用紙作成", type="primary"):
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

def check_duplicate_problem(sentence: str, answer_kanji: str, reading: str) -> tuple[bool, str]:
    """
    重複問題をチェックする
    
    Args:
        sentence: 問題文
        answer_kanji: 回答漢字
        reading: 読み
        
    Returns:
        (is_duplicate, message): 重複フラグとメッセージ
    """
    try:
        saved_problems = st.session_state.problem_storage.load_problems()
        
        for problem in saved_problems:
            # 完全一致チェック
            if (problem.sentence == sentence and 
                problem.answer_kanji == answer_kanji and 
                problem.reading == reading):
                return True, f"完全に同じ問題が既に存在します（ID: {problem.id}）"
            
            # 回答漢字と読みの組み合わせチェック
            if (problem.answer_kanji == answer_kanji and 
                problem.reading == reading):
                return True, f"同じ漢字・読みの組み合わせが既に存在します（問題文: {problem.sentence[:30]}...）"
            
            # 問題文の類似チェック（部分一致）
            if problem.sentence == sentence:
                return True, f"同じ問題文が既に存在します（回答: {problem.answer_kanji} - {problem.reading}）"
        
        return False, ""
        
    except Exception as e:
        st.warning(f"重複チェック中にエラーが発生しました: {e}")
        return False, ""

@error_handler("問題保存中")
def save_all_problems():
    """すべての問題を保存"""
    if not st.session_state.problems:
        ErrorHandler.handle_warning("保存する問題がありません。")
        return
    
    try:
        saved_count = 0
        for problem in st.session_state.problems:
            if st.session_state.problem_storage.save_problem(problem):
                saved_count += 1
                app_logger.info(f"問題を保存しました: {problem.answer_kanji}")
        
        if saved_count > 0:
            ErrorHandler.handle_success(f"{saved_count}問の問題を保存しました！")
            app_logger.info(f"問題保存完了: {saved_count}問")
        else:
            ErrorHandler.handle_error(Exception("問題の保存に失敗しました"), "問題保存中")
    except Exception as e:
        ErrorHandler.handle_error(e, "問題保存中")

def show_print_page():
    """問題用紙作成ページ"""
    st.header("🖨️ 問題用紙作成")
    
    # 問題の選択方法
    problem_source = st.radio(
        "問題の選択方法",
        ["現在のセッションの問題", "保存された問題から選択", "特定の問題を選択"],
        horizontal=True
    )
    
    problems_to_print = []
    
    if problem_source == "現在のセッションの問題":
        if not st.session_state.problems:
            st.warning("印刷する問題がありません。問題登録ページで問題を追加してください。")
            return
        problems_to_print = st.session_state.problems
        
    elif problem_source == "保存された問題から選択":
        try:
            saved_problems = st.session_state.problem_storage.load_problems()
            if not saved_problems:
                st.warning("保存された問題がありません。問題登録ページで問題を作成してください。")
                return
            
            # 問題選択UI
            selected_problem_ids = st.multiselect(
                "印刷する問題を選択",
                options=[(p.id, f"{p.answer_kanji} ({p.reading}) - {p.sentence[:30]}...") for p in saved_problems],
                format_func=lambda x: x[1]
            )
            
            if selected_problem_ids:
                problems_to_print = [p for p in saved_problems if p.id in [x[0] for x in selected_problem_ids]]
            else:
                st.info("印刷する問題を選択してください。")
                return
                
        except Exception as e:
            st.error(f"❌ 保存された問題の読み込みに失敗しました: {e}")
            return
    
    elif problem_source == "特定の問題を選択":
        if 'selected_problem_for_print' in st.session_state:
            problems_to_print = [st.session_state.selected_problem_for_print]
            st.success(f"選択された問題: {st.session_state.selected_problem_for_print.answer_kanji}")
        else:
            st.info("履歴管理ページから問題を選択してください。")
            return
    
    if not problems_to_print:
        return
    
    # 印刷設定
    col1, col2 = st.columns(2)
    with col1:
        questions_per_page = st.number_input(
            "1ページあたりの問題数",
            min_value=1,
            max_value=20,
            value=min(10, len(problems_to_print))
        )
    with col2:
        title = st.text_input(
            "テストタイトル",
            value="漢字テスト"
        )
    
    # 選択された問題の表示
    st.subheader(f"📋 印刷対象の問題 ({len(problems_to_print)}問)")
    for i, problem in enumerate(problems_to_print):
        with st.expander(f"問題 {i+1}: {problem.answer_kanji} ({problem.reading})"):
            st.write(f"**問題文**: {problem.sentence}")
            st.write(f"**回答漢字**: {problem.answer_kanji}")
            st.write(f"**読み**: {problem.reading}")
    
    # 印刷用ページ生成
    if st.button("🖨️ 印刷用ページを表示", type="primary"):
        try:
            from src.modules.print_page import PrintPageGenerator
            
            generator = PrintPageGenerator()
            html_content = generator.generate_print_page(
                problems_to_print,
                title,
                questions_per_page
            )
            
            # 印刷した問題群をセッション状態に保存
            st.session_state.printed_problems = problems_to_print.copy()
            
            # HTMLを表示
            st.components.v1.html(html_content, height=600, scrolling=True)
            
            # 採点ページへの案内
            st.success("✅ 印刷用ページを表示しました！採点ページで採点できます。")
            if st.button("✅ 採点ページに移動", type="secondary"):
                st.session_state.current_page = "採点"
                st.rerun()
            
        except Exception as e:
            st.error(f"❌ 印刷用ページの生成に失敗しました: {e}")

def show_scoring_page():
    """採点ページ"""
    st.header("📊 採点・学習記録")
    
    # 印刷した問題群がある場合は優先表示
    if st.session_state.printed_problems:
        st.subheader("🖨️ 今回印刷した問題群の採点")
        st.info(f"印刷用ページで表示した {len(st.session_state.printed_problems)} 問の問題を採点できます。")
        
        # 印刷した問題群の表示
        for i, problem in enumerate(st.session_state.printed_problems):
            with st.expander(f"問題 {i+1}: {problem.answer_kanji} ({problem.reading})"):
                st.write(f"**問題文**: {problem.sentence}")
                st.write(f"**回答漢字**: {problem.answer_kanji}")
                st.write(f"**読み**: {problem.reading}")
        
        # 採点フォーム
        with st.form("printed_problems_scoring_form"):
            st.subheader("✏️ 採点")
            scores = {}
            
            for i, problem in enumerate(st.session_state.printed_problems):
                st.write(f"**問題 {i+1}**: {problem.sentence}")
                st.write(f"**回答漢字**: {problem.answer_kanji} ({problem.reading})")
                
                # 正誤選択
                col1, col2, col3 = st.columns(3)
                with col1:
                    correct = st.radio(f"正誤", ["正解", "不正解"], key=f"printed_score_{problem.id}", horizontal=True)
                with col2:
                    if correct == "不正解":
                        mistake_type = st.selectbox(
                            "間違いの種類",
                            ["読み間違い", "漢字間違い", "その他"],
                            key=f"printed_mistake_{problem.id}"
                        )
                    else:
                        mistake_type = None
                with col3:
                    notes = st.text_input("メモ", key=f"printed_notes_{problem.id}", placeholder="学習メモ（任意）")
                
                scores[problem.id] = {
                    'is_correct': correct == "正解",
                    'mistake_type': mistake_type,
                    'notes': notes
                }
                
                st.divider()
            
            # 採点結果の保存
            submitted = st.form_submit_button("💾 採点結果を保存", type="primary")
            
            if submitted:
                try:
                    # 試行データを保存
                    saved_count = 0
                    for problem_id, score_data in scores.items():
                        attempt = Attempt(
                            problem_id=problem_id,
                            is_correct=score_data['is_correct']
                        )
                        if st.session_state.attempt_storage.save_attempt(attempt):
                            saved_count += 1
                    
                    if saved_count > 0:
                        st.success(f"✅ {saved_count}問の採点結果を保存しました！")
                        
                        # 採点結果の表示
                        correct_count = sum(1 for score in scores.values() if score['is_correct'])
                        total_count = len(scores)
                        accuracy = (correct_count / total_count) * 100 if total_count > 0 else 0
                        
                        st.subheader("📊 採点結果")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("正解数", correct_count)
                        with col2:
                            st.metric("不正解数", total_count - correct_count)
                        with col3:
                            st.metric("正答率", f"{accuracy:.1f}%")
                        
                        # 間違いの分析
                        if total_count - correct_count > 0:
                            st.subheader("🔍 間違いの分析")
                            mistake_analysis = {}
                            for score in scores.values():
                                if not score['is_correct'] and score['mistake_type']:
                                    mistake_type = score['mistake_type']
                                    mistake_analysis[mistake_type] = mistake_analysis.get(mistake_type, 0) + 1
                            
                            if mistake_analysis:
                                for mistake_type, count in mistake_analysis.items():
                                    st.write(f"**{mistake_type}**: {count}問")
                        
                        # 印刷した問題群をクリア
                        st.session_state.printed_problems = []
                        st.rerun()
                    else:
                        st.error("❌ 採点結果の保存に失敗しました。")
                        
                except Exception as e:
                    st.error(f"❌ 採点結果の保存に失敗しました: {e}")
        
        # 他の問題を採点する場合の選択
        st.markdown("---")
        st.subheader("📋 他の問題を採点する")
        
        if st.button("📚 保存された問題から選択して採点", type="secondary"):
            st.session_state.show_manual_selection = True
            st.rerun()
    
    # 手動選択モードまたは印刷した問題群がない場合
    if not st.session_state.printed_problems or st.session_state.get('show_manual_selection', False):
        # 手動選択モードをリセット
        if 'show_manual_selection' in st.session_state:
            del st.session_state.show_manual_selection
        
        # 保存された問題を読み込み
        try:
            saved_problems = st.session_state.problem_storage.load_problems()
            
            if not saved_problems:
                st.info("📝 採点する問題がありません。問題登録ページで問題を作成してください。")
                return
            
            # 問題選択
            st.subheader("📋 採点する問題を選択")
            
            # 問題選択方法
            selection_method = st.radio(
                "選択方法",
                ["個別選択", "一括選択", "最近作成した問題"],
                horizontal=True
            )
            
            selected_problems = []
            
            if selection_method == "個別選択":
                selected_problem_ids = st.multiselect(
                    "採点する問題を選択",
                    options=[(p.id, f"{p.answer_kanji} ({p.reading}) - {p.sentence[:30]}...") for p in saved_problems],
                    format_func=lambda x: x[1]
                )
                selected_problems = [p for p in saved_problems if p.id in [x[0] for x in selected_problem_ids]]
                
            elif selection_method == "一括選択":
                col1, col2 = st.columns(2)
                with col1:
                    select_all = st.button("すべて選択")
                with col2:
                    select_none = st.button("選択解除")
                
                if select_all:
                    selected_problems = saved_problems
                elif select_none:
                    selected_problems = []
                else:
                    selected_problems = saved_problems  # デフォルトで全選択
                    
            elif selection_method == "最近作成した問題":
                recent_count = st.number_input("最近作成した問題数", min_value=1, max_value=len(saved_problems), value=5)
                selected_problems = sorted(saved_problems, key=lambda x: x.created_at, reverse=True)[:recent_count]
            
            if not selected_problems:
                st.info("採点する問題を選択してください。")
                return
        
            # 採点フォーム
            st.subheader(f"✏️ 採点 ({len(selected_problems)}問)")
            
            with st.form("manual_scoring_form"):
                scores = {}
                
                for i, problem in enumerate(selected_problems):
                    st.write(f"**問題 {i+1}**: {problem.sentence}")
                    st.write(f"**回答漢字**: {problem.answer_kanji} ({problem.reading})")
                    
                    # 正誤選択
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        correct = st.radio(f"正誤", ["正解", "不正解"], key=f"manual_score_{problem.id}", horizontal=True)
                    with col2:
                        if correct == "不正解":
                            mistake_type = st.selectbox(
                                "間違いの種類",
                                ["読み間違い", "漢字間違い", "その他"],
                                key=f"manual_mistake_{problem.id}"
                            )
                        else:
                            mistake_type = None
                    with col3:
                        notes = st.text_input("メモ", key=f"manual_notes_{problem.id}", placeholder="学習メモ（任意）")
                    
                    scores[problem.id] = {
                        'is_correct': correct == "正解",
                        'mistake_type': mistake_type,
                        'notes': notes
                    }
                    
                    st.divider()
                
                # 採点結果の保存
                submitted = st.form_submit_button("💾 採点結果を保存", type="primary")
                
                if submitted:
                    try:
                        # 試行データを保存
                        saved_count = 0
                        for problem_id, score_data in scores.items():
                            attempt = Attempt(
                                problem_id=problem_id,
                                is_correct=score_data['is_correct']
                            )
                            if st.session_state.attempt_storage.save_attempt(attempt):
                                saved_count += 1
                        
                        if saved_count > 0:
                            st.success(f"✅ {saved_count}問の採点結果を保存しました！")
                            
                            # 採点結果の表示
                            correct_count = sum(1 for score in scores.values() if score['is_correct'])
                            total_count = len(scores)
                            accuracy = (correct_count / total_count) * 100 if total_count > 0 else 0
                            
                            st.subheader("📊 採点結果")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("正解数", correct_count)
                            with col2:
                                st.metric("不正解数", total_count - correct_count)
                            with col3:
                                st.metric("正答率", f"{accuracy:.1f}%")
                            
                            # 間違いの分析
                            if total_count - correct_count > 0:
                                st.subheader("🔍 間違いの分析")
                                mistake_analysis = {}
                                for score in scores.values():
                                    if not score['is_correct'] and score['mistake_type']:
                                        mistake_type = score['mistake_type']
                                        mistake_analysis[mistake_type] = mistake_analysis.get(mistake_type, 0) + 1
                                
                                if mistake_analysis:
                                    for mistake_type, count in mistake_analysis.items():
                                        st.write(f"**{mistake_type}**: {count}問")
                        else:
                            st.error("❌ 採点結果の保存に失敗しました。")
                            
                    except Exception as e:
                        st.error(f"❌ 採点結果の保存に失敗しました: {e}")
        
        except Exception as e:
            st.error(f"❌ 採点ページの読み込みに失敗しました: {e}")

def show_history_page():
    """履歴管理ページ"""
    st.header("📚 履歴管理")
    
    # 保存された問題を読み込み
    try:
        saved_problems = st.session_state.problem_storage.load_problems()
        
        if not saved_problems:
            st.info("📝 保存された問題がありません。問題登録ページで問題を作成してください。")
            return
        
        # 検索・フィルタリング機能
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_term = st.text_input("🔍 検索", placeholder="問題文、漢字、読みで検索")
        
        with col2:
            sort_by = st.selectbox("📊 並び順", ["作成日時（新しい順）", "作成日時（古い順）", "問題文（あいうえお順）", "漢字（あいうえお順）"])
        
        with col3:
            show_count = st.number_input("表示件数", min_value=5, max_value=100, value=20)
        
        # 学習統計の表示
        st.subheader("📊 学習統計")
        # 問題統計の初期化
        problem_stats = {}
        
        try:
            attempts = st.session_state.attempt_storage.load_attempts()
            if attempts:
                # 問題別の統計を計算
                for attempt in attempts:
                    problem_id = attempt.problem_id
                    if problem_id not in problem_stats:
                        problem_stats[problem_id] = {
                            'correct_count': 0,
                            'total_count': 0,
                            'last_attempted': None
                        }
                    
                    problem_stats[problem_id]['total_count'] += 1
                    if attempt.is_correct:
                        problem_stats[problem_id]['correct_count'] += 1
                    
                    # 最後の試行日を更新
                    if (problem_stats[problem_id]['last_attempted'] is None or 
                        attempt.attempted_at > problem_stats[problem_id]['last_attempted']):
                        problem_stats[problem_id]['last_attempted'] = attempt.attempted_at
                
                # 統計情報を表示
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("総問題数", len(saved_problems))
                with col2:
                    st.metric("採点済み問題数", len(problem_stats))
                with col3:
                    total_attempts = len(attempts)
                    st.metric("総試行回数", total_attempts)
                with col4:
                    if total_attempts > 0:
                        correct_attempts = sum(1 for a in attempts if a.is_correct)
                        accuracy = (correct_attempts / total_attempts) * 100
                        st.metric("全体正答率", f"{accuracy:.1f}%")
                    else:
                        st.metric("全体正答率", "0.0%")
            else:
                st.info("まだ採点データがありません。採点ページで採点を行ってください。")
        except Exception as e:
            app_logger.exception(f"学習統計の読み込みに失敗しました: {e}")
            st.warning(f"学習統計の読み込みに失敗しました: {e}")
            # エラーが発生した場合でも空の辞書を維持
            problem_stats = {}
        
        # 問題のフィルタリング
        filtered_problems = saved_problems
        
        if search_term:
            search_term = search_term.lower()
            filtered_problems = [
                p for p in filtered_problems
                if (search_term in p.sentence.lower() or 
                    search_term in p.answer_kanji.lower() or 
                    search_term in p.reading.lower())
            ]
        
        # 問題の並び替え
        if sort_by == "作成日時（新しい順）":
            filtered_problems.sort(key=lambda x: x.created_at, reverse=True)
        elif sort_by == "作成日時（古い順）":
            filtered_problems.sort(key=lambda x: x.created_at)
        elif sort_by == "問題文（あいうえお順）":
            filtered_problems.sort(key=lambda x: x.sentence)
        elif sort_by == "漢字（あいうえお順）":
            filtered_problems.sort(key=lambda x: x.answer_kanji)
        
        # 表示件数制限
        display_problems = filtered_problems[:show_count]
        
        # 統計情報の表示
        st.subheader("📊 統計情報")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("総問題数", len(saved_problems))
        with col2:
            st.metric("表示中", len(display_problems))
        with col3:
            st.metric("検索結果", len(filtered_problems))
        with col4:
            if saved_problems:
                latest_date = max(p.created_at for p in saved_problems)
                st.metric("最新作成日", latest_date.strftime("%m/%d"))
        
        # 学習進捗の可視化
        try:
            attempts = st.session_state.attempt_storage.load_attempts()
            if attempts:
                st.subheader("📈 学習進捗")
                
                # 正答率の計算
                correct_attempts = sum(1 for attempt in attempts if attempt.is_correct)
                total_attempts = len(attempts)
                accuracy = (correct_attempts / total_attempts) * 100 if total_attempts > 0 else 0
                
                # 進捗メトリクス
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("総試行数", total_attempts)
                with col2:
                    st.metric("正解数", correct_attempts)
                with col3:
                    st.metric("不正解数", total_attempts - correct_attempts)
                with col4:
                    st.metric("正答率", f"{accuracy:.1f}%")
                
                # 問題別の正答率
                problem_attempts = {}
                for attempt in attempts:
                    if attempt.problem_id not in problem_attempts:
                        problem_attempts[attempt.problem_id] = {'correct': 0, 'total': 0}
                    problem_attempts[attempt.problem_id]['total'] += 1
                    if attempt.is_correct:
                        problem_attempts[attempt.problem_id]['correct'] += 1
                
                if problem_attempts:
                    st.subheader("📋 問題別正答率")
                    
                    # 問題別の正答率を表示
                    problem_stats = []
                    for problem in saved_problems:
                        if problem.id in problem_attempts:
                            stats = problem_attempts[problem.id]
                            accuracy = (stats['correct'] / stats['total']) * 100 if stats['total'] > 0 else 0
                            problem_stats.append({
                                'problem': problem,
                                'accuracy': accuracy,
                                'correct': stats['correct'],
                                'total': stats['total']
                            })
                    
                    # 正答率でソート
                    problem_stats.sort(key=lambda x: x['accuracy'])
                    
                    # 正答率の低い問題を表示
                    if problem_stats:
                        st.write("**正答率の低い問題（要復習）**")
                        for i, stats in enumerate(problem_stats[:5]):  # 上位5問
                            problem = stats['problem']
                            accuracy = stats['accuracy']
                            correct = stats['correct']
                            total = stats['total']
                            
                            with st.expander(f"{problem.answer_kanji} - 正答率: {accuracy:.1f}% ({correct}/{total})"):
                                st.write(f"**問題文**: {problem.sentence}")
                                st.write(f"**回答漢字**: {problem.answer_kanji}")
                                st.write(f"**読み**: {problem.reading}")
                                st.write(f"**正答率**: {accuracy:.1f}% ({correct}回正解 / {total}回挑戦)")
                                
                                # 復習ボタン
                                if st.button("📄 復習用印刷", key=f"review_{problem.id}"):
                                    st.session_state.selected_problem_for_print = problem
                                    st.rerun()
        except Exception as e:
            st.warning(f"学習進捗の読み込みに失敗しました: {e}")
        
        # 問題一覧の表示
        st.subheader(f"📋 問題一覧 ({len(display_problems)}件)")
        
        try:
            for i, problem in enumerate(display_problems):
                # 問題の統計情報を取得（安全にアクセス）
                if isinstance(problem_stats, dict):
                    problem_stat = problem_stats.get(problem.id, {
                        'correct_count': 0,
                        'total_count': 0,
                        'last_attempted': None
                    })
                else:
                    # problem_statsが辞書でない場合のフォールバック
                    problem_stat = {
                        'correct_count': 0,
                        'total_count': 0,
                        'last_attempted': None
                    }
                
                # 正答率を計算
                accuracy = 0
                if problem_stat['total_count'] > 0:
                    accuracy = (problem_stat['correct_count'] / problem_stat['total_count']) * 100
                
                # 最後の試行日をフォーマット
                last_attempted_str = "未採点"
                if problem_stat['last_attempted']:
                    last_attempted_str = problem_stat['last_attempted'].strftime('%Y/%m/%d %H:%M')
                
                # 問題のタイトルに統計情報を含める
                title = f"問題 {i+1}: {problem.answer_kanji} ({problem.reading}) - 正答率: {accuracy:.1f}% ({problem_stat['correct_count']}/{problem_stat['total_count']})"
                
                with st.expander(title):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**問題文**: {problem.sentence}")
                        st.write(f"**回答漢字**: {problem.answer_kanji}")
                        st.write(f"**読み**: {problem.reading}")
                        st.write(f"**作成日時**: {problem.created_at.strftime('%Y年%m月%d日 %H:%M')}")
                        
                        # 学習統計情報
                        st.write("**学習統計**:")
                        col_stat1, col_stat2, col_stat3 = st.columns(3)
                        with col_stat1:
                            st.write(f"正解回数: {problem_stat['correct_count']}")
                        with col_stat2:
                            st.write(f"試行回数: {problem_stat['total_count']}")
                        with col_stat3:
                            st.write(f"正答率: {accuracy:.1f}%")
                        
                        st.write(f"**最後の採点日**: {last_attempted_str}")
                        
                        # プレビュー表示
                        renderer = TextRenderer()
                        preview = renderer.create_preview(problem)
                        st.write(f"**プレビュー**: {preview}")
                    
                    with col2:
                        # 操作ボタン
                        if st.button("📄 印刷用ページ", key=f"print_{problem.id}"):
                            st.session_state.selected_problem_for_print = problem
                            st.rerun()
                        
                        if st.button("🗑️ 削除", key=f"delete_{problem.id}"):
                            if st.session_state.problem_storage.delete_problem(problem.id):
                                st.success("問題を削除しました")
                                st.rerun()
                            else:
                                st.error("削除に失敗しました")
        
        except Exception as e:
            app_logger.exception(f"問題一覧の表示に失敗しました: {e}")
            st.error(f"問題一覧の表示に失敗しました: {e}")
        
        # ページネーション
        if len(filtered_problems) > show_count:
            st.info(f"表示中: 1-{show_count}件 / 全{len(filtered_problems)}件")
        
    except Exception as e:
        st.error(f"❌ 履歴の読み込みに失敗しました: {e}")


def show_search_page():
    """問題検索ページの表示"""
    st.header("🔍 問題検索")
    
    try:
        from src.modules.search import SearchManager
        
        # 検索マネージャーの初期化
        if 'search_manager' not in st.session_state:
            st.session_state.search_manager = SearchManager()
        
        search_manager = st.session_state.search_manager
        
        # 検索フォーム
        with st.form("search_form"):
            st.subheader("検索条件")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 基本検索
                query = st.text_input(
                    "検索クエリ",
                    placeholder="例：独創的、アーティスト、どくそうてき",
                    help="問題文、回答漢字、読みのいずれかで検索できます"
                )
                
                search_type = st.selectbox(
                    "検索対象",
                    ["all", "problem_text", "answer", "reading"],
                    format_func=lambda x: {
                        "all": "すべて",
                        "problem_text": "問題文のみ",
                        "answer": "回答漢字のみ",
                        "reading": "読みのみ"
                    }[x]
                )
                
                use_regex = st.checkbox("正規表現を使用", help="高度な検索パターンを使用できます")
            
            with col2:
                # 日付範囲フィルタ
                st.write("**日付範囲**")
                col_date1, col_date2 = st.columns(2)
                with col_date1:
                    start_date = st.date_input("開始日", value=None, key="search_start_date")
                with col_date2:
                    end_date = st.date_input("終了日", value=None, key="search_end_date")
                
                # 正答率フィルタ
                st.write("**正答率範囲**")
                col_acc1, col_acc2 = st.columns(2)
                with col_acc1:
                    min_accuracy = st.number_input("最小正答率(%)", min_value=0.0, max_value=100.0, value=None, step=0.1, key="search_min_acc")
                with col_acc2:
                    max_accuracy = st.number_input("最大正答率(%)", min_value=0.0, max_value=100.0, value=None, step=0.1, key="search_max_acc")
            
            # 高度なフィルタ
            with st.expander("高度なフィルタ"):
                col3, col4 = st.columns(2)
                
                with col3:
                    # 試行回数フィルタ
                    st.write("**試行回数範囲**")
                    col_att1, col_att2 = st.columns(2)
                    with col_att1:
                        min_attempts = st.number_input("最小試行回数", min_value=0, value=None, key="search_min_att")
                    with col_att2:
                        max_attempts = st.number_input("最大試行回数", min_value=0, value=None, key="search_max_att")
                
                with col4:
                    # 間違いの種類フィルタ
                    st.write("**間違いの種類**")
                    mistake_types = st.multiselect(
                        "間違いの種類を選択",
                        ["読み間違い", "書き間違い", "意味理解不足", "その他"],
                        key="search_mistake_types"
                    )
            
            # 検索実行ボタン
            search_button = st.form_submit_button("🔍 検索実行", use_container_width=True)
        
        # 検索実行
        if search_button:
            try:
                with st.spinner("検索中..."):
                    results = search_manager.advanced_search(
                        query=query,
                        search_type=search_type,
                        use_regex=use_regex,
                        start_date=start_date,
                        end_date=end_date,
                        min_accuracy=min_accuracy,
                        max_accuracy=max_accuracy,
                        min_attempts=min_attempts,
                        max_attempts=max_attempts,
                        mistake_types=mistake_types if mistake_types else None
                    )
                    
                    st.session_state.search_results = results
                    st.session_state.search_stats = search_manager.get_search_statistics(results)
                    
                    if results:
                        st.success(f"✅ 検索完了: {len(results)}件の結果が見つかりました")
                    else:
                        st.warning("⚠️ 検索条件に一致する問題が見つかりませんでした")
                        
            except Exception as e:
                app_logger.error(f"検索実行中にエラーが発生しました: {e}")
                st.error(f"❌ 検索中にエラーが発生しました: {e}")
        
        # 検索結果の表示
        if 'search_results' in st.session_state and st.session_state.search_results:
            st.subheader("📋 検索結果")
            
            # 統計情報の表示
            if 'search_stats' in st.session_state:
                stats = st.session_state.search_stats
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("総問題数", stats['total_count'])
                with col2:
                    st.metric("平均正答率", f"{stats['average_accuracy']:.1f}%")
                with col3:
                    st.metric("総試行回数", stats['total_attempts'])
                with col4:
                    if stats['date_range']:
                        date_range = f"{stats['date_range']['earliest']} ～ {stats['date_range']['latest']}"
                    else:
                        date_range = "なし"
                    st.metric("日付範囲", date_range)
            
            # 結果の表示
            results = st.session_state.search_results
            
            # 表示件数の選択
            col1, col2 = st.columns([1, 3])
            with col1:
                show_count = st.selectbox("表示件数", [10, 25, 50, 100], index=1)
            with col2:
                st.write("")  # スペーサー
            
            # 問題一覧の表示
            for i, problem in enumerate(results[:show_count]):
                # 問題の統計情報を取得
                attempts = st.session_state.attempt_storage.load_attempts()
                problem_attempts = [a for a in attempts if a.problem_id == problem.id]
                
                if problem_attempts:
                    correct_count = sum(1 for a in problem_attempts if a.is_correct)
                    accuracy = (correct_count / len(problem_attempts)) * 100
                    last_attempted = max(problem_attempts, key=lambda x: x.timestamp).timestamp
                else:
                    accuracy = 0.0
                    last_attempted = None
                
                # 問題のタイトルに統計情報を含める
                title = f"問題 {i+1}: {problem.answer_kanji} ({problem.reading}) - 正答率: {accuracy:.1f}% ({correct_count}/{len(problem_attempts)})"
                
                with st.expander(title):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**問題文**: {problem.sentence}")
                        st.write(f"**回答漢字**: {problem.answer_kanji}")
                        st.write(f"**読み**: {problem.reading}")
                        st.write(f"**作成日時**: {problem.created_at.strftime('%Y年%m月%d日 %H:%M')}")
                        
                        # 学習統計情報
                        if problem_attempts:
                            st.write(f"**試行回数**: {len(problem_attempts)}回")
                            st.write(f"**正答回数**: {correct_count}回")
                            st.write(f"**正答率**: {accuracy:.1f}%")
                            
                            if last_attempted:
                                st.write(f"**最後の試行**: {last_attempted.strftime('%Y年%m月%d日 %H:%M')}")
                        else:
                            st.write("**試行回数**: 0回（未採点）")
                    
                    with col2:
                        # 問題の操作ボタン
                        if st.button(f"印刷", key=f"print_{problem.id}"):
                            st.session_state.printed_problems = [problem]
                            st.session_state.current_page = "問題用紙作成"
                            st.rerun()
                        
                        if st.button(f"採点", key=f"score_{problem.id}"):
                            st.session_state.printed_problems = [problem]
                            st.session_state.current_page = "採点"
                            st.rerun()
            
            # ページネーション
            if len(results) > show_count:
                st.info(f"表示中: 1-{show_count}件 / 全{len(results)}件")
        
        elif 'search_results' in st.session_state and not st.session_state.search_results:
            st.info("検索条件を入力して「検索実行」ボタンを押してください")
        
    except Exception as e:
        app_logger.error(f"検索ページの表示中にエラーが発生しました: {e}")
        st.error(f"❌ 検索ページの表示に失敗しました: {e}")


def show_statistics_page():
    """統計ページの表示"""
    st.header("📈 学習統計")
    
    try:
        from src.modules.statistics import StatisticsManager
        
        # 統計マネージャーの初期化
        if 'statistics_manager' not in st.session_state:
            st.session_state.statistics_manager = StatisticsManager()
        
        statistics_manager = st.session_state.statistics_manager
        
        # 統計データの取得
        with st.spinner("統計データを計算中..."):
            stats = statistics_manager.get_comprehensive_statistics()
            charts = statistics_manager.get_visualization_data()
        
        # 概要統計の表示
        st.subheader("📊 学習概要")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "総問題数",
                stats['overview']['total_problems'],
                help="登録されている問題の総数"
            )
        
        with col2:
            st.metric(
                "総試行回数",
                stats['overview']['total_attempts'],
                help="これまでの採点試行の総数"
            )
        
        with col3:
            st.metric(
                "全体正答率",
                f"{stats['overview']['overall_accuracy']:.1f}%",
                help="全試行の正答率"
            )
        
        with col4:
            # 学習日数の計算
            daily_data = stats['daily_statistics']['daily_data']
            learning_days = len(set(d['date'] for d in daily_data))
            st.metric(
                "学習日数",
                learning_days,
                help="実際に学習を行った日数"
            )
        
        # タブで統計を分ける
        tab1, tab2, tab3, tab4 = st.tabs(["📈 正答率分析", "📅 日別進捗", "❌ 間違い分析", "📊 学習曲線"])
        
        with tab1:
            st.subheader("問題別正答率")
            
            if charts.get('accuracy_chart'):
                st.plotly_chart(charts['accuracy_chart'], use_container_width=True)
            else:
                st.info("正答率データがありません")
            
            # 問題別詳細統計
            if stats['problem_statistics']:
                st.subheader("問題別詳細")
                
                # データフレームの作成
                problem_data = []
                for problem_id, problem_stat in stats['problem_statistics'].items():
                    problem = problem_stat['problem']
                    problem_data.append({
                        '問題': f"{problem.answer_kanji} ({problem.reading})",
                        '問題文': problem.sentence,
                        '正答回数': problem_stat['correct_count'],
                        '試行回数': problem_stat['total_count'],
                        '正答率': f"{problem_stat['accuracy']:.1f}%",
                        '最後の試行': problem_stat['last_attempted'].strftime('%Y/%m/%d') if problem_stat['last_attempted'] else '未採点'
                    })
                
                df = pd.DataFrame(problem_data)
                st.dataframe(df, use_container_width=True)
        
        with tab2:
            st.subheader("日別学習進捗")
            
            if charts.get('daily_progress_chart'):
                st.plotly_chart(charts['daily_progress_chart'], use_container_width=True)
            else:
                st.info("日別進捗データがありません")
            
            # 日別詳細データ
            if stats['daily_statistics']['daily_data']:
                st.subheader("日別詳細")
                
                daily_df = pd.DataFrame(stats['daily_statistics']['daily_data'])
                daily_df['date'] = pd.to_datetime(daily_df['date'])
                daily_df = daily_df.sort_values('date')
                
                st.dataframe(daily_df, use_container_width=True)
        
        with tab3:
            st.subheader("間違いの種類分析")
            
            if charts.get('mistake_distribution_chart'):
                st.plotly_chart(charts['mistake_distribution_chart'], use_container_width=True)
            else:
                st.info("間違いデータがありません")
            
            # 間違い分析の詳細
            mistake_analysis = stats['mistake_analysis']
            
            if mistake_analysis['common_mistakes']:
                st.subheader("よくある間違い")
                
                mistake_data = []
                for mistake_type, count in mistake_analysis['common_mistakes']:
                    mistake_data.append({
                        '間違いの種類': mistake_type,
                        '回数': count
                    })
                
                mistake_df = pd.DataFrame(mistake_data)
                st.dataframe(mistake_df, use_container_width=True)
            
            if mistake_analysis['improvement_areas']:
                st.subheader("改善が必要な領域")
                
                improvement_data = []
                for area in mistake_analysis['improvement_areas']:
                    improvement_data.append({
                        '間違いの種類': area['mistake_type'],
                        '間違い回数': area['count'],
                        '対象問題数': area['unique_problems']
                    })
                
                improvement_df = pd.DataFrame(improvement_data)
                st.dataframe(improvement_df, use_container_width=True)
        
        with tab4:
            st.subheader("学習曲線")
            
            if charts.get('learning_curve_chart'):
                st.plotly_chart(charts['learning_curve_chart'], use_container_width=True)
            else:
                st.info("学習曲線データがありません")
            
            # 学習進捗の詳細
            learning_progress = stats['learning_progress']
            
            if learning_progress['learning_curve']:
                st.subheader("学習進捗詳細")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "期間中の試行回数",
                        learning_progress['total_attempts'],
                        help=f"過去{learning_progress['period_days']}日間の試行回数"
                    )
                
                with col2:
                    st.metric(
                        "期間中の正答率",
                        f"{learning_progress['accuracy']:.1f}%",
                        help=f"過去{learning_progress['period_days']}日間の正答率"
                    )
                
                with col3:
                    st.metric(
                        "学習一貫性",
                        f"{learning_progress['consistency_score']:.1f}%",
                        help="学習日数 / 期間日数"
                    )
                
                # 学習曲線データの表示
                curve_df = pd.DataFrame(learning_progress['learning_curve'])
                curve_df['date'] = pd.to_datetime(curve_df['date'])
                curve_df = curve_df.sort_values('date')
                
                st.dataframe(curve_df, use_container_width=True)
        
        # データエクスポート機能
        st.subheader("📥 データエクスポート")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 統計データをCSVでダウンロード"):
                # 統計データをCSVとして出力
                import io
                
                # 問題別統計のCSV
                if stats['problem_statistics']:
                    problem_data = []
                    for problem_id, problem_stat in stats['problem_statistics'].items():
                        problem = problem_stat['problem']
                        problem_data.append({
                            '問題ID': problem.id,
                            '回答漢字': problem.answer_kanji,
                            '読み': problem.reading,
                            '問題文': problem.sentence,
                            '正答回数': problem_stat['correct_count'],
                            '試行回数': problem_stat['total_count'],
                            '正答率': problem_stat['accuracy'],
                            '最後の試行': problem_stat['last_attempted'].strftime('%Y-%m-%d %H:%M') if problem_stat['last_attempted'] else '未採点'
                        })
                    
                    problem_df = pd.DataFrame(problem_data)
                    csv = problem_df.to_csv(index=False, encoding='utf-8-sig')
                    
                    st.download_button(
                        label="問題別統計をダウンロード",
                        data=csv,
                        file_name=f"problem_statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
        
        with col2:
            if st.button("📅 日別進捗をCSVでダウンロード"):
                # 日別進捗のCSV
                if stats['daily_statistics']['daily_data']:
                    daily_df = pd.DataFrame(stats['daily_statistics']['daily_data'])
                    daily_df['date'] = pd.to_datetime(daily_df['date'])
                    daily_df = daily_df.sort_values('date')
                    daily_df['date'] = daily_df['date'].dt.strftime('%Y-%m-%d')
                    
                    csv = daily_df.to_csv(index=False, encoding='utf-8-sig')
                    
                    st.download_button(
                        label="日別進捗をダウンロード",
                        data=csv,
                        file_name=f"daily_progress_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
        
    except Exception as e:
        app_logger.error(f"統計ページの表示中にエラーが発生しました: {e}")
        st.error(f"❌ 統計ページの表示に失敗しました: {e}")


if __name__ == "__main__":
    main()
