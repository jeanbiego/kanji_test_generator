"""
Streamlitエントリーポイント
メインアプリケーションの起動とページ構成の管理
"""

import streamlit as st
from modules.models import Problem, Attempt
from modules.storage import ProblemStorage, AttemptStorage
from modules.rendering import TextRenderer
from modules.validators import InputValidator
from modules.logger import app_logger
from modules.error_handler import ErrorHandler, error_handler
from modules.backup import BackupManager

# Streamlit設定（アプリケーションの最初に実行）
st.set_page_config(
    page_title="Kanji Test Generator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

@error_handler("アプリケーション初期化中")
def main():
    """メインアプリケーション"""
    try:
        app_logger.info("アプリケーション開始")
    except Exception as e:
        ErrorHandler.handle_error(e, "アプリケーション初期化中")
        return
    
    # 初期化完了フラグのチェック
    if 'initialized' not in st.session_state:
        with st.spinner('アプリケーションを初期化しています...'):
            try:
                # セッション状態の初期化
                st.session_state.problems = []
                st.session_state.problem_storage = ProblemStorage()
                st.session_state.attempt_storage = AttemptStorage()
                st.session_state.printed_problems = []
                st.session_state.scoring_results = {}
                
                # 初期化完了フラグを設定
                st.session_state.initialized = True
                app_logger.info("アプリケーション初期化完了")
            except Exception as e:
                st.error(f"初期化エラー: {e}")
                app_logger.error(f"初期化失敗: {e}")
                return
        
        # 初期化完了後にリロード
        st.rerun()
    
    # 初期化が完了していない場合は何も表示しない
    if not st.session_state.get('initialized', False):
        st.info('アプリケーションを初期化しています...')
        return
    
    # アプリケーションのタイトルと説明（初期化完了後に表示）
    st.title("📝 Kanji Test Generator")
    st.markdown("小学生向け漢字テスト自動作成アプリケーション")
    
    # バックアップ機能の初期化（初期化完了後に実行）
    if st.session_state.get('initialized', False) and 'backup_created' not in st.session_state:
        try:
            with st.spinner('データをバックアップしています...'):
                backup_manager = BackupManager()
                backup_manager.create_backup()
                backup_manager.cleanup_old_backups()
            st.session_state.backup_created = True
            app_logger.info("データファイルのバックアップを作成しました")
        except Exception as e:
            app_logger.error(f"バックアップ作成に失敗しました: {e}")
            st.session_state.backup_created = True  # エラーでも次回はスキップ
    
    # サイドバーでページ選択（常時表示）
    st.sidebar.title("📝 メニュー")
    
    # 現在のページを取得（デフォルトは問題登録）
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "問題登録"
    
    # ページ選択ボタン
    if st.sidebar.button("📝 問題登録", use_container_width=True):
        if st.session_state.current_page != "問題登録":
            st.session_state.current_page = "問題登録"
            st.rerun()
    
    if st.sidebar.button("🖨️ 問題用紙作成", use_container_width=True):
        if st.session_state.current_page != "問題用紙作成":
            st.session_state.current_page = "問題用紙作成"
            st.rerun()
    
    if st.sidebar.button("✅ 採点", use_container_width=True):
        if st.session_state.current_page != "採点":
            st.session_state.current_page = "採点"
            st.rerun()
    
    if st.sidebar.button("📊 履歴管理", use_container_width=True):
        if st.session_state.current_page != "履歴管理":
            st.session_state.current_page = "履歴管理"
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

def show_problem_creation_page():
    """問題登録ページの表示"""
    st.header("📝 問題登録")
    
    # セッション状態の初期化
    if 'problem_review_mode' not in st.session_state:
        st.session_state.problem_review_mode = False
    if 'pending_problem_data' not in st.session_state:
        st.session_state.pending_problem_data = {}
    
    # 問題レビューモードの場合
    if st.session_state.problem_review_mode:
        st.subheader("📋 問題の確認")
        
        # レビュー表示
        problem_data = st.session_state.pending_problem_data
        st.write("**プレビュー**:", TextRenderer().create_preview(Problem(
            sentence=problem_data['sentence'],
            answer_kanji=problem_data['answer_kanji'],
            reading=problem_data['reading']
        )))
        
        # バリデーション結果の表示
        validator = InputValidator()
        validation_result = validator.validate_problem(
            problem_data['sentence'],
            problem_data['answer_kanji'],
            problem_data['reading']
        )
        
        if not validation_result.is_valid:
            st.error("❌ 入力内容に問題があります:")
            for error in validation_result.errors:
                st.error(f"  - {error}")
        
        # 重複チェック
        is_duplicate, duplicate_message = check_duplicate_problem(
            problem_data['sentence'],
            problem_data['answer_kanji'],
            problem_data['reading']
        )
        
        if is_duplicate:
            st.error(f"❌ {duplicate_message}")
            st.info("💡 重複する問題は保存できません。編集に戻って内容を変更してください。")
        
        # ボタン（重複時は保存ボタンを表示しない）
        if is_duplicate:
            # 重複時は編集とキャンセルボタンのみ表示
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✏️ 編集に戻る", type="primary"):
                    st.session_state.problem_review_mode = False
                    st.rerun()
            
            with col2:
                if st.button("❌ キャンセル", type="secondary"):
                    st.session_state.problem_review_mode = False
                    st.session_state.pending_problem_data = {}
                    st.rerun()
        else:
            # 重複していない場合は3つのボタンを表示
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("💾 問題を保存", type="primary"):
                    try:
                        # 問題を作成して保存
                        problem = Problem(
                            sentence=problem_data['sentence'],
                            answer_kanji=problem_data['answer_kanji'],
                            reading=problem_data['reading']
                        )
                        
                        if st.session_state.problem_storage.save_problem(problem):
                            st.success("✅ 問題を保存しました！")
                            # 状態をリセット
                            st.session_state.problem_review_mode = False
                            st.session_state.pending_problem_data = {}
                            st.rerun()
                        else:
                            st.error("❌ 問題の保存に失敗しました。")
                    except Exception as e:
                        st.error(f"❌ 問題の保存中にエラーが発生しました: {e}")
            
            with col2:
                if st.button("✏️ 編集に戻る", type="secondary"):
                    st.session_state.problem_review_mode = False
                    st.rerun()
            
            with col3:
                if st.button("❌ キャンセル", type="secondary"):
                    st.session_state.problem_review_mode = False
                    st.session_state.pending_problem_data = {}
                    st.rerun()
    
    else:
        # 問題入力フォーム
        with st.form("problem_form"):
            st.subheader("新しい問題を作成")
            
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
                create_submitted = st.form_submit_button("問題を作成", type="primary")
            with col2:
                reset_submitted = st.form_submit_button("リセット", type="secondary")
            
            if reset_submitted:
                st.rerun()
            
            if create_submitted:
                # バリデーション
                validator = InputValidator()
                validation_result = validator.validate_problem(sentence, answer_kanji, reading)
                
                if validation_result.is_valid:
                    # レビューモードに移行
                    st.session_state.problem_review_mode = True
                    st.session_state.pending_problem_data = {
                        'sentence': sentence,
                        'answer_kanji': answer_kanji,
                        'reading': reading
                    }
                    st.rerun()
                else:
                    for error in validation_result.errors:
                        st.error(f"❌ {error}")
    

def check_duplicate_problem(sentence: str, answer_kanji: str, reading: str) -> tuple[bool, str]:
    """
    重複問題をチェックする
    仕様: 回答漢字と読みの両方が一致する場合に重複と判定
    
    Args:
        sentence: 問題文
        answer_kanji: 回答漢字
        reading: 読み
        
    Returns:
        (is_duplicate, message): 重複フラグとメッセージ
    """
    try:
        from modules.utils import normalize_reading
        
        # 入力された読みを正規化して比較
        normalized_reading = normalize_reading(reading)
        
        saved_problems = st.session_state.problem_storage.load_problems()
        
        for problem in saved_problems:
            # 回答漢字と読みの組み合わせチェック（仕様通り）
            if (problem.answer_kanji == answer_kanji and 
                problem.reading == normalized_reading):
                return True, f"同じ漢字・読みの組み合わせが既に存在します（問題文: {problem.sentence[:30]}...）"
        
        return False, ""
        
    except Exception as e:
        st.warning(f"重複チェック中にエラーが発生しました: {e}")
        return False, ""

def show_print_page():
    """問題用紙作成ページ"""
    st.header("🖨️ 問題用紙作成")
    
    # 印刷設定（問題抽出前から表示）
    st.subheader("⚙️ 印刷設定")
    col_set1, col_set2 = st.columns(2)
    with col_set1:
        total_questions = st.number_input(
            "総問題数",
            min_value=1,
            max_value=100,
            value=10,
            help="印刷する問題の総数を設定します"
        )
    with col_set2:
        title = st.text_input(
            "テストタイトル",
            value="漢字テスト",
            help="印刷用ページのタイトルを設定します"
        )

    # 自動抽出機能のボタン
    st.subheader("📝 問題の自動抽出")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎯 苦手漢字抽出", type="primary", use_container_width=True):
            try:
                # 苦手漢字抽出ロジック
                saved_problems = st.session_state.problem_storage.load_problems()
                attempts = st.session_state.attempt_storage.load_attempts()
                
                if not saved_problems:
                    st.warning("保存された問題がありません。問題登録ページで問題を作成してください。")
                    return
                
                if not attempts:
                    st.warning("採点データがありません。採点ページで採点を行ってください。")
                    return
                
                # 問題の不正解数でソートして上位を抽出
                problems_with_incorrect_count = [(p, p.incorrect_count) for p in saved_problems]
                sorted_problems = sorted(problems_with_incorrect_count, key=lambda x: x[1], reverse=True)
                problems_to_print = [p for p, _ in sorted_problems[:int(total_questions)]]
                
                if problems_to_print:
                    st.session_state.extracted_problems = problems_to_print
                    st.success(f"✅ 苦手漢字を{len(problems_to_print)}問抽出しました")
                else:
                    st.warning("苦手漢字が見つかりませんでした。")
                    return
                    
            except Exception as e:
                st.error(f"❌ 苦手漢字抽出に失敗しました: {e}")
                return
    
    with col2:
        if st.button("🎲 ランダム抽出", type="secondary", use_container_width=True):
            try:
                # ランダム抽出ロジック
                saved_problems = st.session_state.problem_storage.load_problems()
                
                if not saved_problems:
                    st.warning("保存された問題がありません。問題登録ページで問題を作成してください。")
                    return
                
                # ランダムに抽出（重複なし）
                import random
                qpp = int(total_questions)
                if len(saved_problems) >= qpp:
                    problems_to_print = random.sample(saved_problems, qpp)
                else:
                    problems_to_print = saved_problems
                
                st.session_state.extracted_problems = problems_to_print
                st.success(f"✅ ランダムに{len(problems_to_print)}問抽出しました")
                
            except Exception as e:
                st.error(f"❌ ランダム抽出に失敗しました: {e}")
                return
    
    # 設定は上部に移動済み
    
    # 抽出された問題の表示
    if 'extracted_problems' in st.session_state and st.session_state.extracted_problems:
        problems_to_print = st.session_state.extracted_problems
    else:
        st.info("上記のボタンから問題を抽出してください。")
        return
    
    # 選択された問題の表示
    st.subheader(f"📋 印刷対象の問題 ({len(problems_to_print)}問)")
    for i, problem in enumerate(problems_to_print):
        with st.expander(f"問題 {i+1}: {problem.answer_kanji} ({problem.reading}) / 不正解数: {problem.incorrect_count}"):
            st.write(f"**問題文**: {problem.sentence}")
            st.write(f"**回答漢字**: {problem.answer_kanji}")
            st.write(f"**読み**: {problem.reading}")
            st.write(f"**不正解数**: {problem.incorrect_count}")
    
    # 印刷用ページ生成
    if st.button("🖨️ 印刷用ページを表示", type="primary"):
        try:
            from modules.print_page import PrintPageGenerator
            
            generator = PrintPageGenerator()
            html_content = generator.generate_print_page(
                problems_to_print,
                title,
                10  # 1ページあたりの問題数を10にハードコーディング
            )
            
            # ページ数を計算（1ページあたり10問で固定）
            questions_per_page = 10
            total_pages = (len(problems_to_print) + questions_per_page - 1) // questions_per_page
            
            # 印刷した問題群をセッション状態に保存
            st.session_state.printed_problems = problems_to_print.copy()
            
            # ページ情報を表示
            if total_pages > 1:
                st.info(f"📄 {len(problems_to_print)}問を{total_pages}ページに分割して表示します（1ページあたり10問）")
            else:
                st.info(f"📄 {len(problems_to_print)}問を1ページに表示します")
            
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
    st.header("✅ 採点")
    
    # 最後に作成した問題用紙の問題群を自動表示
    if 'extracted_problems' in st.session_state and st.session_state.extracted_problems:
        # 上部の一覧表示は非表示にし、見出し下のみで採点フォームに集約
        
        # 採点フォーム
        with st.form("printed_problems_scoring_form"):
            st.subheader("✏️ 採点")
            scores = {}
            
            for i, problem in enumerate(st.session_state.extracted_problems):
                st.write(f"**問題 {i+1}**: {problem.sentence}")
                st.write(f"**回答漢字**: {problem.answer_kanji} ({problem.reading})")
                
                # 正誤選択
                col1, col2, col3 = st.columns(3)
                with col1:
                    correct = st.radio("正誤", ["正解", "不正解"], key=f"printed_score_{problem.id}", horizontal=True)
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
                    # 試行データを保存し、問題の不正解数を更新
                    saved_count = 0
                    for problem_id, score_data in scores.items():
                        attempt = Attempt(
                            problem_id=problem_id,
                            is_correct=score_data['is_correct']
                        )
                        if st.session_state.attempt_storage.save_attempt(attempt):
                            saved_count += 1
                            
                            # 問題の不正解数を更新
                            saved_problems = st.session_state.problem_storage.load_problems()
                            for problem in saved_problems:
                                if problem.id == problem_id:
                                    if score_data['is_correct']:
                                        problem.decrement_incorrect_count()
                                    else:
                                        problem.increment_incorrect_count()
                                    # 更新された問題を保存
                                    st.session_state.problem_storage.save_problem(problem)
                                    break
                    
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
                        
                        # 抽出した問題群をクリア
                        st.session_state.extracted_problems = []
                        st.rerun()
                    else:
                        st.error("❌ 採点結果の保存に失敗しました。")
                        
                except Exception as e:
                    st.error(f"❌ 採点結果の保存に失敗しました: {e}")
    
    else:
        st.info("📝 問題用紙作成ページで問題を抽出してから採点してください。")

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
        
        # 重複IDをUI上で非表示（最初の1件のみ採用）
        seen_ids = set()
        unique_problems = []
        for p in filtered_problems:
            if p.id in seen_ids:
                continue
            seen_ids.add(p.id)
            unique_problems.append(p)

        # 表示件数制限
        display_problems = unique_problems[:show_count]
        
        # 基本情報の表示
        st.write(f"**総問題数**: {len(saved_problems)} | **表示中**: {len(display_problems)} | **検索結果（重複含む）**: {len(filtered_problems)} | **一意ID数**: {len(unique_problems)}")
        
        # 問題一覧の表示
        st.subheader(f"📋 問題一覧 ({len(display_problems)}件)")
        
        try:
            for i, problem in enumerate(display_problems):
                # 問題のタイトル
                title = f"問題 {i+1}: {problem.answer_kanji} ({problem.reading}) / 不正解数: {problem.incorrect_count}"
                
                with st.expander(title):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**問題文**: {problem.sentence}")
                        st.write(f"**回答漢字**: {problem.answer_kanji}")
                        st.write(f"**読み**: {problem.reading}")
                        st.write(f"**作成日時**: {problem.created_at.strftime('%Y年%m月%d日 %H:%M')}")
                        st.write(f"**不正解数**: {problem.incorrect_count}")
                        
                        # プレビュー表示
                        renderer = TextRenderer()
                        preview = renderer.create_preview(problem)
                        st.write(f"**プレビュー**: {preview}")
                    
                    with col2:
                        # 操作ボタン
                        col_btn1, col_btn2 = st.columns(2)
                        
                        with col_btn1:
                            if st.button("📄 印刷", key=f"print_{i}_{problem.id}_{hash(problem.sentence)}"):
                                st.session_state.selected_problem_for_print = problem
                                st.session_state.current_page = "問題用紙作成"
                                st.rerun()
                        
                        with col_btn2:
                            if st.button("✏️ 採点", key=f"score_{i}_{problem.id}_{hash(problem.sentence)}"):
                                st.session_state.selected_problem_for_scoring = problem
                                st.session_state.current_page = "採点"
                                st.rerun()
                        
                        # 削除ボタン
                        if st.button("🗑️ 削除", key=f"delete_{i}_{problem.id}_{hash(problem.sentence)}"):
                            # 重複が存在する場合でも1件のみ削除
                            if hasattr(st.session_state.problem_storage, 'delete_problem_once') and st.session_state.problem_storage.delete_problem_once(problem.id):
                                st.success(f"問題「{problem.answer_kanji}」を削除しました。")
                                st.rerun()
                            else:
                                st.error("問題の削除に失敗しました。")
        
        except Exception as e:
            app_logger.exception(f"問題一覧の表示に失敗しました: {e}")
            st.error(f"問題一覧の表示に失敗しました: {e}")
        
        # ページネーション
        if len(filtered_problems) > show_count:
            st.info(f"表示中: 1-{show_count}件 / 全{len(filtered_problems)}件")
        
    except Exception as e:
        st.error(f"❌ 履歴の読み込みに失敗しました: {e}")

if __name__ == "__main__":
    main()