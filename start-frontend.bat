@echo off
echo ========================================
echo  ビザ選定エキスパートシステム - フロントエンド
echo ========================================
cd /d "%~dp0frontend"

echo.
echo node_modulesをチェック中...
if not exist "node_modules" (
    echo 依存パッケージをインストール中...
    npm install
)

echo.
echo 開発サーバーを起動中... (http://localhost:3000)
echo Ctrl+C で停止できます
echo.
npm start
