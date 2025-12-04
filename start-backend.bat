@echo off
echo ========================================
echo  ビザ選定エキスパートシステム - バックエンド
echo ========================================
cd /d "%~dp0backend"

echo.
echo Python仮想環境をチェック中...
if not exist "venv" (
    echo 仮想環境を作成中...
    python -m venv venv
)

echo.
echo 仮想環境をアクティベート中...
call venv\Scripts\activate.bat

echo.
echo 依存パッケージをインストール中...
pip install -r requirements.txt

echo.
echo サーバーを起動中... (http://localhost:8000)
echo Ctrl+C で停止できます
echo.
uvicorn main:app --reload --host 0.0.0.0 --port 8000
