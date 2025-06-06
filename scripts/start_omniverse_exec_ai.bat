@echo off
echo ======================================
echo   Omniverse Exec AI 啟動腳本
echo ======================================
echo.

:: 檢查是否在正確的目錄
if not exist "src\ui\streamlit_app.py" (
    echo ❌ 錯誤：請在專案根目錄執行此腳本
    pause
    exit /b 1
)

:: 激活 Conda 環境
echo 🔧 激活 Conda 環境...
call conda activate visustwin_langchain
if errorlevel 1 (
    echo ❌ 無法激活 Conda 環境，請確認環境名稱是否正確
    pause
    exit /b 1
)

echo ✅ Conda 環境已激活

:: 啟動 FastAPI 後端（背景執行）
echo 🚀 啟動 FastAPI 後端服務...
start "FastAPI Server" cmd /c "conda activate visustwin_langchain && python -m src.api.fastapi_server"

:: 等待 FastAPI 啟動
echo ⏳ 等待 FastAPI 服務啟動...
timeout /t 3 /nobreak > nul

:: 啟動 Streamlit 前端
echo 🎨 啟動 Streamlit 前端界面...
echo.
echo 📱 Streamlit 界面：http://localhost:8501
echo 📡 FastAPI 文檔：http://localhost:8000/docs
echo.
streamlit run src\ui\streamlit_app.py

pause 