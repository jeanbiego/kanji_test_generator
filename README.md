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
```bash
streamlit run src/app.py
```

## 技術スタック
- Python 3.10+
- Streamlit
- ReportLab
- pandas

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
└── logs/                  # ログファイル
```

## ライセンス
MIT License
