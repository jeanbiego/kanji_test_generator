# Kanji Test Generator

小学生向けの漢字テスト自動作成アプリケーション

## 概要
問題文、回答漢字、読みを入力して、漢字テスト用のPDFを自動作成するアプリケーションです。

## 機能
- 問題の入力・編集・削除
- プレビュー機能（漢字→カタカナ置換）
- PDF出力（A4レイアウト）
- 採点記録・履歴管理
- CSV形式でのデータ保存

## セットアップ
```bash
pip install -r requirements.txt
```

## 起動方法

### バッチファイルを使用した起動（推奨）
Windows環境では、以下のバッチファイルを使用して簡単に起動できます：

#### 基本起動
```bash
start_app.bat
```

#### 詳細設定版
```bash
start_app_advanced.bat
```

#### 開発モード
```bash
start_app_dev.bat
```

### 手動起動
```bash
# 仮想環境の有効化
venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt

# アプリの起動
streamlit run src/app.py
```

## 技術スタック
- Python 3.10+
- Streamlit
- ReportLab
- pandas

## CI/CD

このプロジェクトでは、GitHub Actionsを使用してCI/CDパイプラインを実装しています。

### CI実行内容

プルリクエスト作成時またはmasterブランチへのpush時に、以下のチェックが自動実行されます：

- **テスト実行**: pytestによる単体テストの実行
- **リントチェック**: ruffによるコード品質チェック
- **フォーマットチェック**: ruff formatによるコードフォーマットチェック
- **型チェック**: mypyによる型チェック

### 設定ファイル

- `.github/workflows/ci.yml`: GitHub Actionsワークフローファイル
- `ruff.toml`: Ruffリント・フォーマット設定
- `pyproject.toml`: プロジェクト設定（black、ruff、mypy設定を含む）
- `mypy.ini`: MyPy型チェック設定

## プロジェクト構成
```
kanji_quiz/
├── src/                    # ソースコード
│   ├── app.py             # Streamlitエントリーポイント
│   └── modules/           # 機能別モジュール
├── tests/                 # テストコード
├── data/                  # データファイル
├── assets/                # 静的ファイル
├── templates/             # HTMLテンプレート
├── docs/                  # ドキュメント
├── openspec/              # OpenSpec仕様管理
│   ├── specs/             # 現在の仕様
│   ├── changes/           # 進行中の変更提案
│   └── archive/           # 完了した変更の履歴
├── logs/                  # ログファイル
└── AGENTS.md              # AI assistant向け指示
```

## OpenSpec仕様駆動開発

このプロジェクトでは、新規機能開発において[OpenSpec](https://openspec.dev/)を使用した仕様駆動開発を実践しています。

### 新規機能開発フロー

1. **提案作成**: `/openspec:proposal <機能名>` または自然言語で依頼
2. **仕様レビュー**: `openspec show <変更名>` で提案内容を確認
3. **仕様検証**: `openspec validate <変更名>` で仕様の妥当性を検証
4. **実装**: `/openspec:apply <変更名>` または自然言語で依頼
5. **アーカイブ**: `/openspec:archive <変更名>` でアーカイブ

### 基本コマンド

```bash
# アクティブな変更一覧
openspec list

# インタラクティブダッシュボード
openspec view

# 変更の詳細表示
openspec show <変更名>

# 仕様の検証
openspec validate <変更名>

# 変更のアーカイブ
openspec archive <変更名>
```

### 既存ドキュメントとの使い分け

- **OpenSpec**: 新規機能の仕様管理・タスク管理
- **docs/implementation.md**: プロジェクト全体の実装状況サマリー
- **docs/implementation/**: 過去の実装記録（参照用）
- **docs/Kanji Test Generator要件定義・設計ドラフト.md**: 基本要件（参照用）

## ライセンス
MIT License
