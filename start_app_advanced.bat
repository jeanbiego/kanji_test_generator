@echo off
chcp 65001 >nul
REM Kanji Test Generator アプリ起動バッチファイル（詳細版）
REM 作成日: 2025-01-27

setlocal enabledelayedexpansion

echo ========================================
echo Kanji Test Generator アプリ起動中...
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
    echo または、以下のコマンドを実行してください:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
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
    echo 仮想環境が正しく設定されていない可能性があります
    pause
    exit /b 1
)

REM アプリファイルの存在確認
if not exist "%APP_FILE%" (
    echo エラー: アプリファイルが見つかりません: %APP_FILE%
    pause
    exit /b 1
)

REM 依存関係の確認とインストール
if exist "requirements.txt" (
    echo 依存関係を確認中...
    pip install -r requirements.txt --quiet
    if %errorlevel% neq 0 (
        echo 警告: 依存関係のインストールに失敗しました
        echo アプリの起動を続行します...
    ) else (
        echo 依存関係の確認が完了しました
    )
) else (
    echo 警告: requirements.txtが見つかりません
    echo 依存関係のインストールをスキップします
)

REM データディレクトリの確認
if not exist "data" (
    echo データディレクトリを作成中...
    mkdir data
)

REM ログディレクトリの確認
if not exist "logs" (
    echo ログディレクトリを作成中...
    mkdir logs
)

REM Pythonパスの設定
set PYTHONPATH=%APP_DIR%
echo Pythonパスを設定しました: %PYTHONPATH%

REM アプリの起動
echo ========================================
echo アプリを起動しています...
echo ========================================
echo ブラウザが自動的に開きます
echo URL: http://%HOST%:%PORT%
echo アプリを停止するには Ctrl+C を押してください
echo ========================================

REM Streamlitアプリの起動
streamlit run "%APP_FILE%" --server.port %PORT% --server.address %HOST% --server.headless false

REM アプリ終了後の処理
echo ========================================
echo アプリが終了しました
echo ========================================
echo 何かキーを押すとウィンドウが閉じます...
pause >nul
