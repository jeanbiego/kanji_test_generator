@echo off
chcp 65001 >nul
REM Kanji Test Generator アプリ起動バッチファイル（開発用）
REM 作成日: 2025-01-27

setlocal enabledelayedexpansion

echo ========================================
echo Kanji Test Generator アプリ起動中（開発モード）
echo ========================================

REM 設定変数
set "APP_DIR=%~dp0"
set "VENV_DIR=%APP_DIR%venv"
set "APP_FILE=%APP_DIR%src\app.py"
set "PORT=8501"
set "HOST=localhost"

REM ワークディレクトリに移動
echo ワークディレクトリ: %APP_DIR%
cd /d "%APP_DIR%"
if %errorlevel% neq 0 (
    echo エラー: ワークディレクトリの移動に失敗しました
    pause
    exit /b 1
)

REM 仮想環境の存在確認
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo エラー: 仮想環境が見つかりません
    echo 仮想環境を作成してください: python -m venv venv
    pause
    exit /b 1
)

REM 仮想環境の有効化
echo 仮想環境を有効化中...
call "%VENV_DIR%\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo エラー: 仮想環境の有効化に失敗しました
    pause
    exit /b 1
)

REM Pythonの存在確認
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo エラー: Pythonが見つかりません
    pause
    exit /b 1
)

REM 開発用依存関係のインストール
if exist "requirements.txt" (
    echo 開発用依存関係をインストール中...
    pip install -r requirements.txt --quiet
    if %errorlevel% neq 0 (
        echo 警告: 依存関係のインストールに失敗しました
    )
)

REM 開発用ツールのインストール（オプション）
echo 開発用ツールを確認中...
pip install black ruff mypy pytest --quiet >nul 2>&1

REM コードフォーマットの実行（オプション）
echo コードフォーマットを実行中...
black src/ --quiet >nul 2>&1
ruff check src/ --fix --quiet >nul 2>&1

REM Pythonパスの設定
set PYTHONPATH=%APP_DIR%
echo Pythonパスを設定しました: %PYTHONPATH%

REM アプリの起動
echo ========================================
echo アプリを起動しています（開発モード）...
echo ========================================
echo ブラウザが自動的に開きます
echo URL: http://%HOST%:%PORT%
echo アプリを停止するには Ctrl+C を押してください
echo ========================================

REM Streamlitアプリの起動（開発モード）
streamlit run "%APP_FILE%" --server.port %PORT% --server.address %HOST% --server.headless false --server.runOnSave true

REM アプリ終了後の処理
echo ========================================
echo アプリが終了しました
echo ========================================
pause
