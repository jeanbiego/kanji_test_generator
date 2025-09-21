# 命名規則

## 変数名の命名規則

### 基本ルール
1. スネークケース（snake_case）を使用
   - 例：`problem_sentence`, `answer_kanji`, `reading_text`

2. 変数名は説明的で具体的に
   - 良い例：`current_problems`, `problem_data`, `validation_result`
   - 避けるべき例：`data`, `temp`, `x`

3. 型を表す接尾辞は使用しない
   - 避けるべき例：`problem_obj`, `storage_var`

### カテゴリ別命名規則

#### 問題データ関連

| 変数名 | 説明 | 使用箇所 | 参考資料 |
|:--|:--|:--|:--|
| `problem_sentence` | 問題文 | src/app.py, src/modules/models.py | - |
| `answer_kanji` | 回答漢字 | src/app.py, src/modules/models.py | - |
| `reading_text` | 読み | src/app.py, src/modules/models.py | - |
| `problem_id` | 問題ID | src/modules/models.py | - |
| `created_at` | 作成日時 | src/modules/models.py | - |
| `problem_data` | 問題データ | src/modules/storage.py | - |
| `problems` | 問題一覧 | src/app.py | - |
| `current_problem` | 現在の問題 | src/app.py | - |
| `problem_storage` | 問題ストレージ | src/app.py | - |

#### 試行データ関連

| 変数名 | 説明 | 使用箇所 | 参考資料 |
|:--|:--|:--|:--|
| `attempt_id` | 試行ID | src/modules/models.py | - |
| `attempted_at` | 試行日時 | src/modules/models.py | - |
| `is_correct` | 正誤フラグ | src/modules/models.py | - |
| `attempt_data` | 試行データ | src/modules/storage.py | - |
| `attempts` | 試行一覧 | src/modules/storage.py | - |
| `attempt_storage` | 試行ストレージ | src/app.py | - |

#### バリデーション関連

| 変数名 | 説明 | 使用箇所 | 参考資料 |
|:--|:--|:--|:--|
| `validation_result` | バリデーション結果 | src/modules/validators.py | - |
| `is_valid` | 有効性フラグ | src/modules/validators.py | - |
| `error_messages` | エラーメッセージ | src/modules/validators.py | - |
| `validator` | バリデーター | src/app.py | - |

#### レンダリング関連

| 変数名 | 説明 | 使用箇所 | 参考資料 |
|:--|:--|:--|:--|
| `renderer` | レンダラー | src/app.py | - |
| `preview_text` | プレビューテキスト | src/modules/rendering.py | - |
| `display_text` | 表示テキスト | src/modules/rendering.py | - |
| `text_renderer` | テキストレンダラー | src/modules/rendering.py | - |

#### 印刷関連

| 変数名 | 説明 | 使用箇所 | 参考資料 |
|:--|:--|:--|:--|
| `print_generator` | 印刷生成器 | src/app.py | - |
| `html_content` | HTMLコンテンツ | src/modules/print_page.py | - |
| `template_dir` | テンプレートディレクトリ | src/modules/print_page.py | - |
| `page_settings` | ページ設定 | src/modules/print_page.py | - |
| `questions_per_page` | 1ページあたりの問題数 | src/app.py | - |
| `print_title` | 印刷タイトル | src/app.py | - |

#### セッション状態関連

| 変数名 | 説明 | 使用箇所 | 参考資料 |
|:--|:--|:--|:--|
| `session_state` | セッション状態 | src/app.py | - |
| `st` | Streamlitモジュール | src/app.py | - |
| `page` | 現在のページ | src/app.py | - |
| `submitted` | フォーム送信フラグ | src/app.py | - |
| `col1`, `col2` | カラムレイアウト | src/app.py | - |

## 関数名の命名規則

### 基本ルール
1. スネークケース（snake_case）を使用
2. 動詞で始める
3. 説明的で具体的な名前を使用

### カテゴリ別命名規則

#### 問題操作
- 作成：`create_{target}`
  - 例：`create_problem`, `create_preview`
- 取得：`get_{target}`
  - 例：`get_problem`, `get_problems`
- 保存：`save_{target}`
  - 例：`save_problem`, `save_all_problems`
- 削除：`delete_{target}`
  - 例：`delete_problem`

#### バリデーション
- 検証：`validate_{target}`
  - 例：`validate_problem`, `validate_input`

#### レンダリング
- 生成：`generate_{target}`
  - 例：`generate_print_page`, `generate_html`
- 表示：`show_{target}`
  - 例：`show_problem_creation_page`, `show_print_page`

#### ストレージ操作
- 読み込み：`load_{target}`
  - 例：`load_problems`, `load_attempts`
- 保存：`save_{target}`
  - 例：`save_problem`, `save_attempt`

## クラス名の命名規則

### 基本ルール
1. パスカルケース（PascalCase）を使用
2. 名詞で始める
3. 説明的で具体的な名前を使用

### 例
- `Problem` - 問題クラス
- `Attempt` - 試行クラス
- `ProblemStorage` - 問題ストレージクラス
- `AttemptStorage` - 試行ストレージクラス
- `TextRenderer` - テキストレンダラークラス
- `InputValidator` - 入力バリデータークラス
- `PrintPageGenerator` - 印刷ページ生成クラス
- `ValidationResult` - バリデーション結果クラス

## 使用禁止の命名パターン

1. 1文字の変数名（ループ変数を除く）
   - 避けるべき例：`x`, `y`, `i`（ループ変数以外）

2. 型を表す接尾辞
   - 避けるべき例：`problem_obj`, `storage_var`

3. ハンガリアン記法
   - 避けるべき例：`strName`, `intCount`

4. 略語の過度な使用
   - 避けるべき例：`prob`, `ans`
   - 許容される例：`max`, `min`, `count`

5. 日本語の変数名
   - 避けるべき例：`問題文`, `回答漢字`

## 定数

| 定数名 | 説明 | 使用箇所 | 参考資料 |
|:--|:--|:--|:--|
| `DEFAULT_TEMPLATE_DIR` | デフォルトテンプレートディレクトリ | src/modules/print_page.py | - |
| `DEFAULT_DATA_DIR` | デフォルトデータディレクトリ | src/modules/storage.py | - |
| `MAX_PROBLEMS_PER_PAGE` | 1ページあたりの最大問題数 | src/app.py | - |
| `MIN_PROBLEMS_PER_PAGE` | 1ページあたりの最小問題数 | src/app.py | - |

## 更新ルール

1. 新規変数追加時
   - このドキュメントの命名規則に従う
   - 必要に応じてドキュメントを更新

2. 定期的な見直し
   - 月次で命名規則の遵守状況を確認
   - 必要に応じてルールを更新

3. レビューでの確認
   - プルリクエスト時に命名規則の遵守を確認
   - 違反がある場合は修正を要求

## 実装状況

- ✅ 基本命名規則の策定
- ✅ カテゴリ別命名規則の策定
- ✅ 使用禁止パターンの定義
- ✅ 更新ルールの策定

---

**最終更新日**: 2025-01-27
**状態**: 漢字テストアプリ用命名規則策定完了

