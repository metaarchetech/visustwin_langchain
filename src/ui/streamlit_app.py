import streamlit as st
from datetime import datetime
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.config.groq_config import UnifiedEngineConfig
from langchain_core.prompts import ChatPromptTemplate
import re
import requests
import json
import subprocess
import threading
import time
import psutil

# --- 初始化 AI 引擎 ---
@st.cache_resource
def get_ai_engine():
    """初始化並緩存 AI 引擎配置"""
    return UnifiedEngineConfig()

# --- 真實的 Groq 代碼生成函數 ---
def generate_omniverse_code(user_input: str) -> tuple[str, bool]:
    """
    使用 Groq 生成 Omniverse Python 代碼
    返回：(生成的代碼, 是否成功)
    """
    try:
        # 獲取 AI 引擎
        engine = get_ai_engine()
        
        # 創建針對代碼生成優化的模型實例
        llm = engine.create_model_instance(
            task_type="code",
            temperature=0.3,  # 降低隨機性確保代碼準確
            max_tokens=1500
        )
        
        # 設計專業的提示詞模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", """
你是一個專業的 Omniverse 開發工程師，擅長將自然語言轉換為高品質的 Omniverse Python 代碼。

**輸出要求**：
1. 只返回可直接執行的 Python 代碼，不要任何解釋文字
2. 使用標準的 Omniverse API：omni.kit.scripting, pxr.UsdGeom, pxr.UsdPhysics 等
3. 包含所有必要的 import 語句
4. 代碼結構清晰，適當添加中文註解
5. 確保代碼安全，避免文件操作或系統調用
6. 將主要邏輯封裝在函數中並調用

**常用 API 參考**：
- 創建幾何體：UsdGeom.Cube.Define(stage, "/World/Cube")
- 獲取場景：omni.usd.get_context().get_stage()
- 物理屬性：UsdPhysics.RigidBodyAPI.Apply(prim)
- 材質：UsdShade.Material.Define(stage, "/World/Materials/Material")
            """),
            ("human", "用戶指令：{user_input}")
        ])
        
        # 生成代碼
        chain = prompt | llm
        response = chain.invoke({"user_input": user_input})
        
        # 提取代碼內容
        code = response.content if hasattr(response, 'content') else str(response)
        
        # 代碼安全檢查
        if not validate_code_safety(code):
            return "# 安全檢查未通過：代碼包含潛在危險操作", False
            
        return code, True
        
    except Exception as e:
        error_msg = f"""
# AI 代碼生成失敗
# 錯誤詳情：{str(e)}
# 
# 建議：
# 1. 檢查網路連接
# 2. 確認 API 配置正確
# 3. 重新描述指令
print("代碼生成失敗，請重試")
"""
        return error_msg, False

# --- 代碼安全檢查函數 ---
def validate_code_safety(code: str) -> bool:
    """檢查代碼是否安全"""
    # 危險操作黑名單
    forbidden_patterns = [
        r'os\.system',
        r'subprocess',
        r'open\s*\(',
        r'exec\s*\(',
        r'eval\s*\(',
        r'__import__',
        r'import\s+os',
        r'import\s+subprocess',
        r'from\s+os',
        r'rmdir',
        r'remove',
        r'delete'
    ]
    
    # 檢查是否包含危險操作
    for pattern in forbidden_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            return False
    
    return True

# --- 狀態緩存機制 ---
@st.cache_data(ttl=30)  # 緩存30秒，避免頻繁測試
def get_ai_status_cached():
    """緩存的 AI 引擎連接狀態檢測"""
    return get_ai_status_real()

# --- 檢查 AI 引擎狀態 ---
def get_ai_status():
    """獲取 AI 引擎連接狀態（使用緩存）"""
    return get_ai_status_cached()

def get_ai_status_real():
    """獲取 AI 引擎連接狀態（真實偵測）"""
    try:
        engine = get_ai_engine()
        current = engine.get_current_engine()
        
        # 真實測試連接狀態
        if current == "groq":
            # 測試 Groq API 連接
            is_connected = engine.test_groq_connection()
            if is_connected:
                # 進一步檢查模型可用性
                try:
                    test_llm = engine.create_model_instance(task_type="default", max_tokens=10)
                    # 發送簡單測試請求
                    test_response = test_llm.invoke("Hello")
                    return f"🟢 已連接 (GROQ API - {engine.get_model('default')})", True
                except Exception as model_error:
                    return f"🟡 API 可達但模型異常 (GROQ): {str(model_error)[:50]}...", False
            else:
                return "🔴 GROQ API 連接失敗", False
                
        elif current == "ollama":
            # 測試 Ollama 連接
            is_connected = engine.test_ollama_connection()
            if is_connected:
                try:
                    test_llm = engine.create_model_instance(task_type="default")
                    # 發送簡單測試請求
                    test_response = test_llm.invoke("Hello")
                    return f"🟢 已連接 (OLLAMA - {engine.get_model('default')})", True
                except Exception as model_error:
                    return f"🟡 Ollama 可達但模型異常: {str(model_error)[:50]}...", False
            else:
                return "🔴 Ollama 服務連接失敗", False
        else:
            return f"🔴 未知引擎: {current}", False
            
    except Exception as e:
        return f"🔴 狀態檢測失敗: {str(e)[:50]}...", False

# --- 傳送代碼到 Omniverse 函數 ---
def send_code_to_omniverse(code: str, is_safe: bool) -> bool:
    """
    將生成的代碼傳送到 Omniverse Extension 執行
    返回：True 表示傳送成功，False 表示失敗
    """
    if not is_safe:
        return False
    
    try:
        # 嘗試連接 FastAPI 後端
        response = requests.post(
            "http://localhost:8000/queue_code",
            json={
                "code": code,
                "safe": is_safe
            },
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("status") == "queued"
        else:
            return False
            
    except requests.exceptions.RequestException:
        # FastAPI 後端未啟動或連接失敗
        return False
    except Exception as e:
        st.error(f"傳送過程發生錯誤：{str(e)}")
        return False

# --- FastAPI 服務器管理 ---
def check_fastapi_status() -> tuple[str, bool]:
    """檢查 FastAPI 後端是否運行"""
    try:
        response = requests.get("http://localhost:8000/healthz", timeout=3)
        if response.status_code == 200:
            return "🟢 FastAPI 服務運行中", True
        else:
            return "🔴 FastAPI 服務異常", False
    except requests.exceptions.RequestException:
        return "🔴 FastAPI 服務未啟動", False
    except Exception as e:
        return f"🔴 狀態檢查失敗: {str(e)[:30]}...", False

def start_fastapi_server():
    """啟動 FastAPI 服務器"""
    try:
        # 檢查是否已經在運行
        status, is_running = check_fastapi_status()
        if is_running:
            return True, "FastAPI 服務已在運行中"
        
        # 構建啟動命令 - 使用絕對路徑
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.join(current_dir, '..', '..')
        script_path = os.path.join(project_root, 'src', 'api', 'fastapi_server.py')
        
        # 檢查文件是否存在
        if not os.path.exists(script_path):
            return False, f"找不到 FastAPI 腳本: {script_path}"
        
        # 使用 python -m 方式啟動
        command = [sys.executable, "-m", "src.api.fastapi_server"]
        
        # 在後台啟動 FastAPI 服務器
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=project_root,  # 設置工作目錄
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
        )
        
        # 等待服務啟動並檢查進程狀態
        time.sleep(4)
        
        # 檢查進程是否還在運行
        if process.poll() is not None:
            # 進程已結束，讀取錯誤信息
            stdout, stderr = process.communicate()
            error_msg = stderr.decode('utf-8', errors='ignore') if stderr else "無錯誤信息"
            return False, f"進程啟動失敗: {error_msg[:200]}"
        
        # 檢查是否成功啟動
        status, is_running = check_fastapi_status()
        if is_running:
            return True, "FastAPI 服務啟動成功！"
        else:
            # 嘗試讀取錯誤信息
            try:
                stdout, stderr = process.communicate(timeout=1)
                error_msg = stderr.decode('utf-8', errors='ignore') if stderr else "服務可能正在啟動中"
                return False, f"服務未響應: {error_msg[:200]}"
            except subprocess.TimeoutExpired:
                return False, "服務啟動中，請稍後檢查狀態"
            
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return False, f"啟動失敗: {str(e)}\n詳細錯誤: {error_detail[:300]}"

def stop_fastapi_server():
    """停止 FastAPI 服務器"""
    try:
        # 查找並終止 FastAPI 進程
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline']
                if cmdline and any('fastapi_server.py' in str(arg) for arg in cmdline):
                    proc.terminate()
                    proc.wait(timeout=5)
                    return True, "FastAPI 服務已停止"
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        return False, "未找到運行中的 FastAPI 服務"
        
    except Exception as e:
        return False, f"停止失敗: {str(e)}"

# --- 原有的 FastAPI 狀態檢查（保持兼容性）---
def check_fastapi_status_legacy() -> tuple[str, bool]:
    """舊版 FastAPI 狀態檢查（保持兼容性）"""
    try:
        response = requests.get("http://localhost:8000/queue_status", timeout=3)
        if response.status_code == 200:
            data = response.json()
            pending_count = data.get("pending_count", 0)
            return f"🟢 FastAPI 已連接 (待執行: {pending_count})", True
        else:
            return "🟡 FastAPI 回應異常", False
    except requests.exceptions.RequestException:
        return "🔴 FastAPI 未啟動", False
    except Exception as e:
        return f"🔴 FastAPI 檢查失敗: {str(e)[:30]}...", False

# --- Streamlit 配置 ---
st.set_page_config(
    page_title="Omniverse Exec AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 全局CSS樣式 ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500&family=SF+Mono:wght@300;400;500&family=Menlo:wght@300;400;500&display=swap');
    
    /* 全局背景和基礎樣式 - 統一深黑色 */
    [data-testid="stAppViewContainer"] {
        background: #050505;
        color: #ffffff;
        font-family: 'IBM Plex Mono', 'SF Mono', 'Menlo', monospace;
        font-size: 11px;
        font-weight: 300;
    }
    
    /* 強制覆蓋主標題樣式 - 1.1倍大小 */
    .main-title, h1[class*=\"main-title\"] {
        font-size: 3.08rem !important;  /* 2.8rem * 1.1 */
        font-family: 'IBM Plex Mono', monospace !important;
        font-weight: 400 !important;
        text-align: center !important;
        color: #ffffff !important;
        margin-bottom: 0.3rem !important;
        letter-spacing: 0.1em !important;
    }
    
    /* 副標題樣式 - 加大至0.9rem */
    .sub-title {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.9rem !important;  /* 從0.75rem加大 */
        text-align: center;
        color: #888888;
        margin-bottom: 1.5rem;
        font-weight: 300;
        letter-spacing: 0.05em;
        line-height: 1.4;  /* 增加行高確保雙語顯示清晰 */
    }
    
    /* 小節標題樣式 - 左右統一 */
    h1, h2, h3 {
        font-family: 'IBM Plex Mono', monospace !important;
        color: #ffffff !important;
        font-weight: 400 !important;
        font-size: 14px !important;
        letter-spacing: 0.02em !important;
        margin-bottom: 8px !important;
    }
    
    /* 強制覆蓋側邊欄背景色 */
    [data-testid="stSidebar"] > div:first-child {
        background-color: #030303 !important;
    }
    
    /* 側邊欄內容區樣式 */
    .css-1d391kg {
        background: #030303 !important;
        border-right: 1px solid #222222 !important;
    }
    
    /* 確保樣式優先級 */
    .css-1d391kg * {
        background: inherit !important;
    }
    
    /* 側邊欄標題 */
    .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3 {
        font-family: 'IBM Plex Mono', monospace !important;
        color: #ffffff !important;
        font-weight: 400 !important;
        font-size: 14px !important;
        letter-spacing: 0.02em !important;
        margin-bottom: 8px !important;
    }
    
    /* 輸入框樣式 */
    .stTextInput input, .stTextArea textarea {
        background: #0a0a0a !important;
        color: #ffffff !important;
        border: 1px solid #222222 !important;
        border-radius: 2px !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 11px !important;
        font-weight: 300 !important;
        padding: 8px 12px !important;
        transition: border-color 0.2s ease !important;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #666666 !important;
        outline: none !important;
        box-shadow: none !important;
    }
    
    /* 按鈕樣式 */
    .stButton>button {
        background: #0a0a0a !important;
        color: #ffffff !important;
        border: 1px solid #222222 !important;
        border-radius: 2px !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-weight: 400 !important;
        font-size: 11px !important;
        padding: 6px 16px !important;
        text-transform: none !important;
        letter-spacing: 0.02em !important;
        transition: all 0.15s ease !important;
        box-shadow: none !important;
    }
    
    .stButton>button:hover {
        background: #2a2a2a !important;
        border-color: #555555 !important;
        transform: none !important;
    }
    
    .stButton>button:active {
        background: #0a0a0a !important;
        transform: none !important;
    }
    
    /* 側邊欄按鈕統一樣式 */
    .css-1d391kg .stButton>button {
        background: #0a0a0a !important;
        color: #ffffff !important;
        border: 1px solid #222222 !important;
        border-radius: 2px !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-weight: 400 !important;
        font-size: 11px !important;
        padding: 6px 16px !important;
        text-transform: none !important;
        letter-spacing: 0.02em !important;
        transition: all 0.15s ease !important;
        box-shadow: none !important;
    }
    
    .css-1d391kg .stButton>button:hover {
        background: #2a2a2a !important;
        border-color: #555555 !important;
        transform: none !important;
    }
    
    /* 主按鈕特殊樣式 */
    .stButton>button[kind="primary"] {
        background: #ffffff !important;
        color: #000000 !important;
        border: 1px solid #ffffff !important;
    }
    
    .stButton>button[kind="primary"]:hover {
        background: #f0f0f0 !important;
        color: #000000 !important;
        border-color: #f0f0f0 !important;
    }
    
    /* 狀態列樣式 */
    .status-bar {
        background: #0a0a0a;
        border: 1px solid #222222;
        border-radius: 2px;
        padding: 8px 12px;
        margin-bottom: 16px;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        font-weight: 300;
    }
    
    .status-connected {
        color: #ffffff;
        font-weight: 400;
    }
    
    .status-disconnected {
        color: #ff6b6b;
        font-weight: 400;
    }
    
    /* 代碼區域樣式 */
    .code-safe {
        background: #0a0a0a;
        border: 1px solid #222222;
        border-left: 2px solid #888888;
        border-radius: 2px;
        padding: 12px;
        margin: 12px 0;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        color: #ffffff;
    }
    
    .code-unsafe {
        background: #0a0a0a;
        border: 1px solid #222222;
        border-left: 2px solid #ff6b6b;
        border-radius: 2px;
        padding: 12px;
        margin: 12px 0;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        color: #ffffff;
    }
    
    /* 代碼塊樣式 */
    .stCodeBlock {
        background: #0a0a0a !important;
        border: 1px solid #222222 !important;
        border-radius: 2px !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 11px !important;
    }
    
    /* 表單樣式 */
    .stForm {
        background: #0a0a0a;
        border: 1px solid #222222;
        border-radius: 2px;
        padding: 16px;
        margin: 12px 0;
    }
    
    /* 選擇框樣式 */
    .stSelectbox > div > div {
        background: #0a0a0a !important;
        border: 1px solid #222222 !important;
        border-radius: 2px !important;
        color: #ffffff !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 11px !important;
    }
    
    /* 滾動條樣式 */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0a0a0a;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #222222;
        border-radius: 2px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #555555;
    }
    
    /* 分隔線樣式 */
    hr {
        border: none;
        height: 1px;
        background: #222222;
        margin: 1.5rem 0;
    }
    
    /* 訊息樣式統一 */
    .stSuccess, .stError, .stInfo, .stWarning {
        background: #0a0a0a !important;
        border: 1px solid #222222 !important;
        border-radius: 2px !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 11px !important;
    }
    
    .stSuccess {
        color: #ffffff !important;
        border-left: 2px solid #888888 !important;
    }
    
    .stError {
        color: #ff6b6b !important;
        border-left: 2px solid #ff6b6b !important;
    }
    
    .stInfo {
        color: #aaaaaa !important;
        border-left: 2px solid #aaaaaa !important;
    }
    
    .stWarning {
        color: #ffa500 !important;
        border-left: 2px solid #ffa500 !important;
    }
    
    /* 隱藏 Streamlit 預設元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    .online-status { color: green; font-weight: bold; }
    .offline-status { color: red; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 狀態列顯示函數 ---
def show_status():
    col1, col2 = st.columns([4, 1])
    
    with col1:
        status_text, is_connected = get_ai_status()
        status_class = "status-connected" if is_connected else "status-disconnected"
        status_icon = "online / 在線" if is_connected else "offline / 離線"
        status_color = "#00ff00" if is_connected else "#ff6b6b"
        
        st.markdown(
            f"""
            <div class="status-bar">
                <span style="color: #aaaaaa;">engine status / 引擎狀態:</span>
                <span class="{status_class}" style="color: {status_color};">{status_icon} {status_text}</span>
                <span style="float:right; color: #666666; font-size: 10px;">{datetime.now().strftime("%H:%M:%S")}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        if st.button("refresh", key="refresh_status", help="強制刷新 AI 狀態"):
            # 清除緩存並重新檢測
            get_ai_status_cached.clear()
            st.rerun()

# --- FastAPI 控制面板（側邊欄）---
def show_fastapi_control_panel():
    """顯示 FastAPI 控制面板"""
    
    # 添加分隔線
    st.sidebar.markdown("""
    <hr style="border: none; height: 1px; background: #222222; margin: 1.5rem 0;">
    """, unsafe_allow_html=True)
    
    # 標題 - 統一字體風格
    st.sidebar.markdown("""
    <div style="font-family: 'IBM Plex Mono', monospace; font-size: 13px; font-weight: 400; color: #ffffff; margin-bottom: 16px;">
        api server control / 服務器控制
    </div>
    """, unsafe_allow_html=True)
    
    # 檢查當前狀態
    status, is_running = check_fastapi_status()
    
    # 狀態顯示 - 使用統一的樣式
    status_color = "#00ff00" if is_running else "#ff6b6b"
    status_text = "online / 在線" if is_running else "offline / 離線"
    
    st.sidebar.markdown(f"""
    <div style="
        background: #0a0a0a; 
        border: 1px solid #222222; 
        border-radius: 2px; 
        padding: 8px 12px; 
        margin: 8px 0;
        font-family: 'IBM Plex Mono', monospace; 
        font-size: 11px;
        color: {status_color};
        border-left: 2px solid {status_color};
    ">
        fastapi: {status_text}
    </div>
    """, unsafe_allow_html=True)
    
    # 控制按鈕區域
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        # 啟動按鈕 - 使用統一的按鈕樣式
        start_disabled = "disabled" if is_running else ""
        if st.button("start", key="start_fastapi", disabled=is_running, help="啟動 FastAPI 服務"):
            with st.spinner("starting service..."):
                success, message = start_fastapi_server()
                if success:
                    st.sidebar.markdown("""
                    <div style="background: #0a0a0a; border: 1px solid #222222; border-radius: 2px; padding: 8px 12px; margin: 8px 0; font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: #00ff00; border-left: 2px solid #00ff00;">
                        service started / 服務已啟動
                    </div>
                    """, unsafe_allow_html=True)
                    time.sleep(1)
                    st.rerun()
                else:
                    st.sidebar.markdown("""
                    <div style="background: #0a0a0a; border: 1px solid #222222; border-radius: 2px; padding: 8px 12px; margin: 8px 0; font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: #ff6b6b; border-left: 2px solid #ff6b6b;">
                        start failed / 啟動失敗
                    </div>
                    """, unsafe_allow_html=True)
                    # 在主界面顯示詳細錯誤信息
                    with st.expander("error details / 錯誤詳情", expanded=True):
                        st.markdown(f"""
                        <div style="
                            background: #0a0a0a; 
                            border: 1px solid #222222; 
                            border-radius: 2px; 
                            padding: 12px; 
                            font-family: 'IBM Plex Mono', monospace; 
                            font-size: 10px; 
                            color: #ff6b6b;
                            white-space: pre-wrap;
                            overflow-x: auto;
                        ">
                        {message}
                        </div>
                        """, unsafe_allow_html=True)
    
    with col2:
        # 停止按鈕
        if st.button("stop", key="stop_fastapi", disabled=not is_running, help="停止 FastAPI 服務"):
            with st.spinner("stopping service..."):
                success, message = stop_fastapi_server()
                if success:
                    st.sidebar.markdown("""
                    <div style="background: #0a0a0a; border: 1px solid #222222; border-radius: 2px; padding: 8px 12px; margin: 8px 0; font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: #aaaaaa; border-left: 2px solid #aaaaaa;">
                        service stopped / 服務已停止
                    </div>
                    """, unsafe_allow_html=True)
                    time.sleep(1)
                    st.rerun()
                else:
                    st.sidebar.markdown("""
                    <div style="background: #0a0a0a; border: 1px solid #222222; border-radius: 2px; padding: 8px 12px; margin: 8px 0; font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: #ff6b6b; border-left: 2px solid #ff6b6b;">
                        stop failed / 停止失敗
                    </div>
                    """, unsafe_allow_html=True)
    
    # API 文檔連結 - 使用統一的連結樣式
    if is_running:
        st.sidebar.markdown("""
        <div style="margin: 12px 0; font-family: 'IBM Plex Mono', monospace; font-size: 10px;">
            <a href="http://localhost:8000/docs" target="_blank" style="color: #aaaaaa; text-decoration: none;">
                → api docs / API 文檔
            </a><br/>
            <a href="http://localhost:8000/healthz" target="_blank" style="color: #aaaaaa; text-decoration: none;">
                → health check / 健康檢查
            </a>
        </div>
        """, unsafe_allow_html=True)
    
    # 調試信息 - 使用統一的摺疊樣式
    with st.sidebar.expander("debug info / 調試信息"):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.join(current_dir, '..', '..')
        script_path = os.path.join(project_root, 'src', 'api', 'fastapi_server.py')
        
        st.markdown(f"""
        <div style="font-family: 'IBM Plex Mono', monospace; font-size: 9px; color: #666666; line-height: 1.4;">
            current: {current_dir}<br/>
            root: {os.path.abspath(project_root)}<br/>
            script: {script_path}<br/>
            exists: {os.path.exists(script_path)}<br/>
            python: {sys.executable}
        </div>
        """, unsafe_allow_html=True)

# --- 主界面 ---
st.markdown('<h1 class="main-title">OMNIVERSE EXEC AI</h1>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">natural language to omniverse code generation<br/>自然語言轉 Omniverse 代碼生成</div>', unsafe_allow_html=True)
st.markdown('<hr>', unsafe_allow_html=True)
show_status()

# 步驟1：自然語言輸入
st.markdown('<h3>input / 輸入</h3>', unsafe_allow_html=True)
with st.form(key="nl_input"):
    user_input = st.text_area(
        "command / 指令",
        height=120,
        placeholder="create a red cube with physics properties at coordinates (0,0,5)\nadd directional light to scene\nsetup camera at default viewpoint",
        help="描述所需的 Omniverse 操作，AI 將生成對應的 Python 代碼"
    )
    
    col1, col2 = st.columns([3, 1])
    with col1:
        generate_btn = st.form_submit_button("generate / 生成", type="primary")
    with col2:
        if st.form_submit_button("clear / 清除"):
            st.session_state.pop("generated_code", None)
            st.session_state.pop("code_safe", None)
            st.rerun()

    if generate_btn and user_input:
        with st.spinner("generating code..."):
            generated_code, success = generate_omniverse_code(user_input)
            st.session_state.generated_code = generated_code
            st.session_state.code_safe = success
            st.session_state.user_input = user_input

# 步驟2：代碼預覽與安全檢查
if "generated_code" in st.session_state:
    st.markdown('<hr>', unsafe_allow_html=True)
    
    # 顯示原始指令
    st.markdown('<h3>input command / 輸入指令</h3>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background: #0a0a0a; border: 1px solid #222222; border-radius: 2px; padding: 12px; font-family: 'IBM Plex Mono', monospace; font-size: 11px; color: #aaaaaa;">
        {st.session_state.get('user_input', '')}
    </div>
    """, unsafe_allow_html=True)
    
    # 代碼預覽
    st.markdown('<h3>generated code / 生成代碼</h3>', unsafe_allow_html=True)
    
    # 根據安全檢查結果顯示不同樣式
    code_class = "code-safe" if st.session_state.get("code_safe", False) else "code-unsafe"
    safety_status = "safe" if st.session_state.get("code_safe", False) else "warning"
    safety_color = "#ffffff" if st.session_state.get("code_safe", False) else "#ff6b6b"
    
    st.markdown(f"""
    <div class="{code_class}">
        <span style="color: {safety_color}; font-family: 'IBM Plex Mono', monospace; font-size: 11px;">
        {'validation: passed' if st.session_state.get("code_safe", False) else 'validation: warning - potential risk detected'}
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    st.code(st.session_state.generated_code, language="python")
    
    # 步驟3：執行控制
    st.markdown('<h3>execution / 執行</h3>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if st.button("authorize / 授權", 
                    disabled=not st.session_state.get("code_safe", False),
                    help="將代碼標記為可執行狀態" if st.session_state.get("code_safe", False) else "代碼未通過安全檢查"):
            st.markdown("""
            <div style="background: #0a0a0a; border: 1px solid #222222; border-radius: 2px; padding: 12px; color: #00ff00; font-family: 'IBM Plex Mono', monospace; font-size: 11px;">
                execution authorized / 執行已授權<br/>
                code ready for deployment
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if st.button("copy code / 複製代碼"):
            st.markdown("""
            <div style="background: #0a0a0a; border: 1px solid #222222; border-radius: 2px; padding: 12px; color: #aaaaaa; font-family: 'IBM Plex Mono', monospace; font-size: 11px;">
                code copied / 代碼已複製<br/>
                manual deployment mode
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if st.button("send / 傳送", 
                    disabled=not st.session_state.get("code_safe", False),
                    help="將代碼傳送到 Omniverse Extension 自動執行" if st.session_state.get("code_safe", False) else "代碼未通過安全檢查"):
            with st.spinner("transmitting..."):
                success = send_code_to_omniverse(
                    st.session_state.generated_code, 
                    st.session_state.code_safe
                )
                if success:
                    st.markdown("""
                    <div style="background: #0a0a0a; border: 1px solid #222222; border-radius: 2px; padding: 12px; color: #00ff00; font-family: 'IBM Plex Mono', monospace; font-size: 11px;">
                        transmission complete<br/>
                        code queued for execution
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style="background: #0a0a0a; border: 1px solid #222222; border-left: 2px solid #ff6b6b; border-radius: 2px; padding: 12px; color: #ff6b6b; font-family: 'IBM Plex Mono', monospace; font-size: 11px;">
                        transmission failed<br/>
                        check fastapi connection
                    </div>
                    """, unsafe_allow_html=True)

# 側邊欄：系統狀態與設定
with st.sidebar:
    st.subheader("系統狀態")
    # 檢查 FastAPI 後端連接狀態
    fastapi_status, fastapi_connected = check_fastapi_status()
    if fastapi_connected:
        st.markdown("<p class='online-status'>✅ 在線</p>", unsafe_allow_html=True)
    else:
        st.markdown("<p class='offline-status'>❌ 離線</p>", unsafe_allow_html=True)
    
    st.markdown('<hr style="margin: 1rem 0;">', unsafe_allow_html=True)
    
    # 引擎切換與狀態
    st.markdown('<h3>ai engine status / AI 引擎狀態</h3>', unsafe_allow_html=True)
    try:
        engine = get_ai_engine()
        current_engine = engine.get_current_engine()
        
        # 首次載入時檢查是否需要初始化引擎狀態
        if "engines_initialized" not in st.session_state:
            # 首次載入：執行完整檢測
            engines = engine.get_available_engines(force_test=True)
            st.session_state.engines_initialized = True
        elif st.button("refresh engines / 刷新引擎", key="refresh_engines"):
            # 手動刷新：強制重新檢測所有引擎
            engines = engine.get_available_engines(force_test=True)
        else:
            # 正常情況：使用緩存結果（避免頻繁測試）
            engines = engine.get_available_engines(force_test=False)
        
        # 顯示引擎狀態詳情
        for name, available in engines.items():
            if name == current_engine:
                # 當前引擎顯示更詳細狀態
                status_text, is_connected = get_ai_status()
                if is_connected:
                    model_name = engine.get_model("default")
                    st.markdown(f"""
                    <div style="background: #0a0a0a; border: 1px solid #222222; border-left: 2px solid #00ff00; border-radius: 2px; padding: 8px; margin: 4px 0; color: #00ff00; font-family: 'IBM Plex Mono', monospace; font-size: 11px;">
                        {name}: active / 使用中<br/>
                        model: {model_name}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background: #0a0a0a; border: 1px solid #222222; border-left: 2px solid #ff6b6b; border-radius: 2px; padding: 8px; margin: 4px 0; color: #ff6b6b; font-family: 'IBM Plex Mono', monospace; font-size: 11px;">
                        {name}: error / 錯誤
                    </div>
                    """, unsafe_allow_html=True)
            else:
                # 非當前引擎簡單顯示
                status = "available / 可用" if available else "offline / 離線"
                color = "#aaaaaa" if available else "#666666"
                st.markdown(f"""
                <div style="color: {color}; font-family: 'IBM Plex Mono', monospace; font-size: 11px; margin: 2px 0;">
                    {name}: {status}
                </div>
                """, unsafe_allow_html=True)
                
        # 引擎切換選項（如果有多個可用引擎）
        if len([eng for eng, avail in engines.items() if avail]) > 1:
            st.markdown('<hr style="margin: 0.5rem 0;">', unsafe_allow_html=True)
            available_engines = [name for name, avail in engines.items() if avail]
            
            # 使用 session_state 來存儲選擇的引擎，避免觸發重新檢測
            if "selected_engine" not in st.session_state:
                st.session_state.selected_engine = current_engine
            
            # 下拉選單選擇引擎（不觸發任何檢測）
            selected_engine = st.selectbox(
                "switch engine / 切換引擎",
                available_engines,
                index=available_engines.index(st.session_state.selected_engine) if st.session_state.selected_engine in available_engines else 0,
                key="engine_selector"
            )
            
            # 更新 session_state 中的選擇
            st.session_state.selected_engine = selected_engine
            
            # 顯示當前狀態
            if selected_engine != current_engine:
                st.markdown(f"""
                <div style="background: #0a0a0a; border: 1px solid #222222; border-radius: 2px; padding: 6px; margin: 4px 0; color: #aaaaaa; font-family: 'IBM Plex Mono', monospace; font-size: 10px;">
                    ready to switch: {current_engine} → {selected_engine}
                </div>
                """, unsafe_allow_html=True)
            
            # 確認切換按鈕（只有選擇不同引擎時才啟用）
            if st.button("confirm switch / 確認切換", disabled=selected_engine == current_engine) and selected_engine != current_engine:
                with st.spinner(f"switching to {selected_engine}..."):
                    if engine.switch_engine(selected_engine):
                        st.markdown(f"""
                        <div style="background: #0a0a0a; border: 1px solid #222222; border-left: 2px solid #00ff00; border-radius: 2px; padding: 8px; color: #00ff00; font-family: 'IBM Plex Mono', monospace; font-size: 11px;">
                            switched to {selected_engine} / 已切換至 {selected_engine}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 清除所有相關緩存，確保主頁面和側邊欄狀態同步更新
                        get_ai_status_cached.clear()  # 清除主頁面狀態緩存
                        
                        # 重置引擎初始化標記，強制重新檢測
                        if "engines_initialized" in st.session_state:
                            del st.session_state.engines_initialized
                        
                        # 更新 session_state 並重新載入
                        st.session_state.selected_engine = selected_engine
                        st.rerun()
                    else:
                        st.markdown(f"""
                        <div style="background: #0a0a0a; border: 1px solid #222222; border-left: 2px solid #ff6b6b; border-radius: 2px; padding: 8px; color: #ff6b6b; font-family: 'IBM Plex Mono', monospace; font-size: 11px;">
                            switch failed: {selected_engine} / 切換失敗：{selected_engine}
                        </div>
                        """, unsafe_allow_html=True)
            
    except Exception as e:
        st.markdown(f"""
        <div style="background: #0a0a0a; border: 1px solid #222222; border-left: 2px solid #ff6b6b; border-radius: 2px; padding: 8px; color: #ff6b6b; font-family: 'IBM Plex Mono', monospace; font-size: 11px;">
            engine check failed / 引擎檢查失敗<br/>
            error: {str(e)}
        </div>
        """, unsafe_allow_html=True)
        # 顯示詳細錯誤（開發用）
        with st.expander("error details / 錯誤詳情"):
            st.code(str(e))
    
    st.markdown('<hr style="margin: 1rem 0;">', unsafe_allow_html=True)
    
    # FastAPI 控制面板
    show_fastapi_control_panel()
    
    st.markdown('<hr style="margin: 1rem 0;">', unsafe_allow_html=True)
    
    # 使用說明
    st.markdown('<h3>usage guide / 使用指南</h3>', unsafe_allow_html=True)
    
    st.markdown("**工作流程 / workflow:**", unsafe_allow_html=True)
    st.markdown("""
    <div style="background: #0a0a0a; border: 1px solid #222222; border-radius: 2px; padding: 12px; color: #aaaaaa; font-family: 'IBM Plex Mono', monospace; font-size: 11px; line-height: 1.4;">
        1. 在主輸入區域輸入自然語言指令<br/>
        &nbsp;&nbsp;&nbsp;enter natural language command<br/><br/>
        2. 點擊 "generate" 生成 python 代碼<br/>
        &nbsp;&nbsp;&nbsp;click generate to create code<br/><br/>
        3. 檢查生成的代碼和安全驗證<br/>
        &nbsp;&nbsp;&nbsp;review code and safety validation<br/><br/>
        4. 使用 "authorize" 確認安全執行<br/>
        &nbsp;&nbsp;&nbsp;use authorize to confirm execution<br/><br/>
        5. "copy code" 用於手動部署到 omniverse<br/>
        &nbsp;&nbsp;&nbsp;copy code for manual deployment<br/><br/>
        6. "send" 用於自動傳送到 fastapi 隊列<br/>
        &nbsp;&nbsp;&nbsp;send for automatic transmission
    </div>
    """, unsafe_allow_html=True) 