# Kanji Test Generator（仮称）— 要件定義・設計ドラフト

> 前提：Windows 11 ローカル運用／単一ユーザー前提。認証・権限・サーバ公開なし。Python＋Streamlitベース（案A）。

---

## 1. 目的・背景

* 小学生向けの**漢字テスト用プリントを自動作成**し、紙で運用できるようにする。
* 問題ごとの**正誤履歴**を残し、次回以降の出題に活用できるようにする。
* ローカルPCのみで完結（ネットワーク不要）。

---

## 2. 用語定義

* **問題**：元の文章（例：独創的な表現で知られるアーティスト）と、その中で回答させたい**漢字**、および**読み**のセット。
* **テストシート**：複数の問題を紙に印刷するためのPDF。
* **試行（attempt）**：ある日に実施したテストでの各問題に対する正誤記録。

---

## 3. スコープ

### 3.1 対象機能

1. 問題の追加（文章／回答させたい漢字／読み）
2. 問題の一覧・検索・再利用（CSV/DBからの呼び出し）
3. 置換プレビュー（漢字→カタカナの読みで置換、解答欄を空白）
4. PDF出力（1ページN問、解答欄・ページ番号・余白・フォント指定）
5. 印刷（Windows標準で実施）
6. 採点UI（試行ごとの正誤入力）
7. 記録ファイル保存（CSV）と読み込み（履歴から呼び出し）

### 3.2 非対象（Out of Scope）

* ユーザー管理（ログイン／権限）
* クラウド同期やオンライン共有
* 自動ルビ生成の高精度化（補助として pykakasi を利用可能）

---

## 4. ユースケース

* **UC-01** 問題を1件ずつ入力 → プレビュー確認 → シートに追加
* **UC-02** 既存の記録（CSV/DB）から問題を検索し、選択してシートに追加
* **UC-03** シートの出題数を設定（例：10問／ページ）しPDF生成
* **UC-04** 印刷して配布
* **UC-05** テスト後に採点画面で〇/×を入力し保存
* **UC-06** 正誤履歴をCSVにエクスポート／CSVから再インポート

---

## 5. 機能要件（FR）

* **FR-1** 問題入力：文章（必須）、回答漢字（必須）、読み（必須）を受け付ける。
* **FR-2** 置換プレビュー：文章内の回答漢字を読み（カタカナ）に置換し、解答欄を空白として表示。
* **FR-3** バリデーション：

  * 文章が空でないこと
  * 回答漢字が文章内に含まれること
  * 読みがひらがな/カタカナであること（内部ではカタカナに正規化）
* **FR-4** 追加／編集／削除：作成中のシートに問題を加除できる。
* **FR-5** 履歴呼び出し：過去に保存した問題一覧から検索（語句一致）し選択して追加できる。
* **FR-6** 印刷用ページ表示：

  * 1ページN問（Nは設定可能）
  * ブラウザの印刷機能を使用
  * 印刷用CSS（@media print）でレイアウト最適化
  * ヘッダ（タイトル／日付／氏名欄）、ページ番号、解答欄の罫線
  * 印刷プレビュー機能の活用
* **FR-7** 正誤記録：

  * 試行日（デフォルト＝本日）
  * 各問題の正誤（true/false）
  * 保存先：`attempts.csv`
* **FR-8** データ保存：

  * 問題マスタ：`problems.csv`
  * 試行ログ：`attempts.csv`
  * 文字コードUTF-8（BOMなし）
* **FR-9** エクスポート／インポート：CSVでの入出力に対応。
* **FR-10** 設定：

  * 出題数、フォント、マージン、行間、解答欄の高さ、保存先フォルダをGUIから指定。

---

## 6. 非機能要件（NFR）

* **NFR-1** ローカル実行（インターネット接続不要）
* **NFR-2** パフォーマンス：100問規模でも印刷用ページの表示が3秒程度で完了することを目安
* **NFR-3** 安定性：異常系（空入力／存在しない文字置換／CSV競合）でエラーメッセージを明示
* **NFR-4** 可搬性：Windows 11 で再現できるセットアップ手順
* **NFR-5** 印刷品質：A4 300dpi相当の視認性（10pt以上）

---

## 7. データモデル／CSV仕様

### 7.1 ファイル構成

* `data/problems.csv`（問題マスタ）
* `data/attempts.csv`（正誤ログ）

### 7.2 スキーマ

**problems.csv**

| 列名            | 型         | 例                   | 備考            |
| ------------- | --------- | ------------------- | ------------- |
| id            | UUIDv4文字列 | `b1a2-...`          | 主キー           |
| sentence      | str       | 独創的な表現で知られるアーティスト   | 元文章           |
| answer\_kanji | str       | 独創                  | 回答させたい漢字      |
| reading       | str       | ドクソウ                | カタカナ（保存時に正規化） |
| created\_at   | ISO8601   | 2025-09-21T10:00:00 | 生成時刻          |

**attempts.csv**（1行＝1問の1回の採点）

| 列名            | 型       | 例          | 備考               |
| ------------- | ------- | ---------- | ---------------- |
| id            | UUIDv4  | `c9f3-...` | 主キー              |
| problem\_id   | UUIDv4  | `b1a2-...` | problems.id への参照 |
| attempted\_at | ISO8601 | 2025-09-21 | 実施日（時刻任意）        |
| is\_correct   | bool    | true       | 正：true／誤：false   |

---

## 8. 印刷用ページレイアウト仕様

* **ページサイズ**：A4、縦（ブラウザの印刷設定で指定）
* **マージン**：上20mm／下15mm／左右15mm（CSS @media printで設定）
* **ヘッダ**：タイトル（例：漢字テスト）、氏名記入欄、日付
* **本文**：各問は

  * 表示文：置換後（回答漢字→カタカナ）
  * 解答欄：下線（幅100〜140mm）と枠
  * 行間（段落間 6〜10mm）
* **フッタ**：ページ番号（CSS counterで実装）
* **フォント**：ブラウザのデフォルトフォント（日本語対応）
* **印刷最適化**：@media printクエリで印刷時のレイアウト調整

---

## 9. 画面（Streamlit）

* **ページ構成**（multipage も可・単一でも可）

  1. **問題作成**：フォーム（文章／回答漢字／読み）、プレビュー、作成中リスト、追加・削除、CSV保存
  2. **印刷用ページ表示**：出題数、余白、レイアウト設定 → 表示ボタン → ブラウザ印刷機能
  3. **採点**：実施日、問題一覧（チェックボックスで〇×）→ 保存
  4. **履歴・インポート**：CSV読み込み、検索、選択して「問題作成」に送る

* **主要UI要素**

  * 入力バリデーション（エラートースト／警告表示）
  * ファイルダイアログ（保存先／読み込み先）
  * テーブル表示（pandasデータフレーム or st-aggrid）

---

## 10. エラーハンドリング

* 回答漢字が文章に含まれない → 警告
* 読みが未入力／ひらがな・カタカナでない → 警告
* CSVの重複ID → 新規ID採番、または上書き禁止
* 印刷用ページ表示失敗（ブラウザ対応問題）→ ガイド表示

---

## 11. セットアップ要件

* **Python**：3.10+ 推奨
* **ブラウザ**：Chrome、Firefox、Edge等のモダンブラウザ
* **印刷方式**：ブラウザの印刷機能を使用（PDF生成ライブラリ不要）

---

## 12. ディレクトリ構成（初期案）

```
kanji_quiz/
  app.py                       # Streamlitエントリ
  modules/
    __init__.py
    models.py                  # dataclass/型定義・ID採番
    storage.py                 # CSV入出力
    rendering.py               # 置換・プレビュー
    print_page.py              # 印刷用ページ生成
    validators.py              # 入力バリデーション
    utils.py                   # 共通処理（日時/正規化）
  templates/
    print_page.html            # 印刷用ページテンプレート
  assets/
    print.css                  # 印刷用CSS
  data/
    problems.csv               # 初回は空ファイル（ヘッダのみ）
    attempts.csv               # 初回は空ファイル（ヘッダのみ）
  tests/
    test_storage.py
    test_print_page.py
  .streamlit/
    config.toml                # テーマ等（任意）
  requirements.txt
  README.md
```

---

## 13. 初期ファイル雛形

**requirements.txt（例）**

```
streamlit
pandas
pykakasi
# PDF生成ライブラリは不要（ブラウザ印刷機能を使用）
```

**data/problems.csv（ヘッダのみ）**

```
id,sentence,answer_kanji,reading,created_at
```

**data/attempts.csv（ヘッダのみ）**

```
id,problem_id,attempted_at,is_correct
```

**templates/print_page.html（印刷用ページ）**

```html
<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8" />
  <title>漢字テスト</title>
  <link rel="stylesheet" href="../assets/print.css">
  <style>
    @media print {
      body { margin: 0; }
      .no-print { display: none; }
      .print-only { display: block; }
    }
    @media screen {
      .print-only { display: none; }
    }
  </style>
</head>
<body>
  <div class="print-controls no-print">
    <button onclick="window.print()">印刷</button>
    <button onclick="window.close()">閉じる</button>
  </div>
  
  <div class="print-content">
    <header>
      <div class="title">漢字テスト</div>
      <div class="header-info">氏名：__________　日付：__________</div>
    </header>
    
    <main>
      {% for q in questions %}
      <div class="question-item">
        <div class="question-text">{{ q.display_text }}</div>
        <div class="answer-line"></div>
      </div>
      {% endfor %}
    </main>
    
    <footer>
      <div class="page-info">Page {{ page }}/{{ total }}</div>
    </footer>
  </div>
</body>
</html>
```

---

## 14. 主要モジュールの責務

* `models.py`：`Problem`, `Attempt` のデータクラス、UUID採番、正規化（カタカナ化）
* `storage.py`：CSVロード／保存、重複チェック
* `rendering.py`：文章→置換（対象漢字→カタカナ読み）、プレビュー文字列生成
* `print_page.py`：印刷用ページ生成、Jinja2で`print_page.html`を流し込み
* `validators.py`：入力チェック（FR-3）

---

## 15. 受け入れ基準（抜粋）

* 入力した「文章／漢字／読み」がプレビューで正しく反映される。
* 置換は初出の一致のみ／全一致の切替を設定で選べる（任意）
* 印刷用ページにN問が整列して表示され、ブラウザの印刷機能で印刷可能。
* 採点UIで〇×を入力し、`attempts.csv`に1行/問題で追記される。
* CSVを削除してもアプリは起動し、空ファイルを自動生成する。

---

## 16. テスト計画（概要）

* **単体**：validators（異常値）、rendering（置換境界）、storage（CSV I/O）
* **結合**：PDF生成で特定の日本語文字（濁点・促音）や長文でも崩れない
* **UI**：フォームバリデーション、CSVの読み書き、ダウンロード動作

---

## 17. 将来拡張

* 学年・配当漢字との連携（出題範囲の自動フィルタ）
* 苦手度スコアリング、再出題ロジック（SRS的）
* 解答・解説プリントの自動生成

---

## 18. 開発フロー補助（Cursor/Vibe向けプロンプト例）

* **ストーリー**：「Streamlitでフォームを作り、入力をデータクラスに詰め、validators→rendering→storage→PDFの順に関数を繋いで」
* **コード分割指示**：「`modules/`に機能別にファイルを分け、`app.py`はUIのみ。ビジネスロジックはモジュール側」
* **生成指示**：「ReportLab版PDFから実装→後で`pdf_html.py`を追加しテンプレ切替できる設計」
* **テスト**：「pytestでCSV入出力の往復と置換境界のパラメトリックテスト」

---
