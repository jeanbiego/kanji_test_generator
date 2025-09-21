@echo off
chcp 65001 >nul
REM Kanji Test Generator アプリ起動バッチファイル
REM 作成日: 2025-01-27

echo ========================================
echo Kanji Test Generator アプリ起動中...
echo ========================================

REM 現在のディレクトリを取得
set "CURRENT_DIR=%~dp0"
echo ワークディレクトリ: %CURRENT_DIR%

REM ワークディレクトリに移動
cd /d "%CURRENT_DIR%"
if %errorlevel% neq 0 (
    echo エラー: ワークディレクトリの移動に失敗しました
    pause
    exit /b 1
)

REM 仮想環境の存在確認
if not exist "venv\Scripts\activate.bat" (
    echo エラー: 仮想環境が見つかりません
    echo 仮想環境を作成してください: python -m venv venv
    pause
    exit /b 1
)

REM 仮想環境の有効化
echo 仮想環境を有効化中...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo エラー: 仮想環境の有効化に失敗しました
    pause
    exit /b 1
)

REM Pythonの存在確認
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo エラー: Pythonが見つかりません
    echo 仮想環境が正しく設定されていない可能性があります
    pause
    exit /b 1
)

REM 依存関係の確認
if not exist "requirements.txt" (
    echo 警告: requirements.txtが見つかりません
    echo 依存関係のインストールをスキップします
) else (
    echo 依存関係を確認中...
    pip install -r requirements.txt --quiet
    if %errorlevel% neq 0 (
        echo 警告: 依存関係のインストールに失敗しました
        echo アプリの起動を続行します...
    )
)

REM Pythonパスの設定
set PYTHONPATH=%APP_DIR%
echo Pythonパスを設定しました: %PYTHONPATH%

REM アプリの起動
echo ========================================
echo アプリを起動しています...
echo ========================================
echo ブラウザが自動的に開きます
echo アプリを停止するには Ctrl+C を押してください
echo ========================================

REM Streamlitアプリの起動
streamlit run src/app.py --server.port 8501 --server.address localhost

REM アプリ終了後の処理
echo ========================================
echo アプリが終了しました
echo ========================================
pause
