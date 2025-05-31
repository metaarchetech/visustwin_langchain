import streamlit as st
import time
import requests
import json
import pyperclip
from langserve_launch_example.chain import get_chain
# 導入代碼生成器 (需要處理 import 錯誤)
try:
    from omniverse_code_generator import omniverse_code_gen
    CODE_GEN_AVAILABLE = True
except ImportError:
    CODE_GEN_AVAILABLE = False
    print("代碼生成器不可用：Omniverse 模組未安裝")
from speech_module import get_voice_manager

# 設置頁面配置
st.set_page_config(
    page_title="Omniverse 語意整合平台",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定義CSS樣式 - NVIDIA風格黑底綠色調，專業簡潔
st.markdown("""
<style>
    /* 全局背景設置 */
    .stApp {
        background-color: #0a0a0a;
        color: #ffffff;
    }
    
    .main {
        background-color: #0a0a0a;
        padding-top: 1rem;
    }
    
    /* 側邊欄樣式 */
    .css-1d391kg {
        background-color: #1a1a1a;
        border-right: 2px solid #76B900;
    }
    
    /* 標題樣式 */
    .stTitle {
        color: #76B900;
        font-size: 3rem !important;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 0 0 20px rgba(118, 185, 0, 0.5);
        letter-spacing: 2px;
    }
    
    .big-font {
        font-size: 1.2rem !important;
        text-align: center;
        margin-bottom: 2rem;
        color: #cccccc;
        font-weight: 300;
    }
    
    /* 功能展示框 - 更小圓角 */
    .feature-box {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        border: 2px solid #76B900;
        padding: 1.5rem;
        border-radius: 6px;
        color: #ffffff;
        margin: 1rem 0;
        box-shadow: 0 0 20px rgba(118, 185, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .feature-box:hover {
        box-shadow: 0 0 30px rgba(118, 185, 0, 0.4);
        transform: translateY(-2px);
    }
    
    .feature-box h3 {
        color: #76B900;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    /* 狀態顯示框 - 更小圓角 */
    .status-box {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        border: 2px solid #00ff41;
        padding: 1rem;
        border-radius: 6px;
        color: #ffffff;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 0 20px rgba(0, 255, 65, 0.3);
    }
    
    /* 查詢框樣式 - 更小圓角 */
    .query-box {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        border: 2px solid #76B900;
        padding: 1.5rem;
        border-radius: 6px;
        border-left: 5px solid #76B900;
        margin: 1rem 0;
        color: #ffffff;
        box-shadow: 0 0 15px rgba(118, 185, 0, 0.2);
    }
    
    /* 回應框樣式 - 更小圓角 */
    .response-box {
        background: linear-gradient(135deg, #0f1f0f 0%, #1a2d1a 100%);
        border: 2px solid #00ff41;
        padding: 1.5rem;
        border-radius: 6px;
        margin: 1rem 0;
        border-left: 5px solid #00ff41;
        color: #ffffff;
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.2);
    }
    
    /* 代碼框樣式 */
    .code-box {
        background: linear-gradient(135deg, #2d1a1a 0%, #1a1a2d 100%);
        border: 2px solid #ff6b6b;
        padding: 1.5rem;
        border-radius: 6px;
        margin: 1rem 0;
        border-left: 5px solid #ff6b6b;
        color: #ffffff;
        box-shadow: 0 0 15px rgba(255, 107, 107, 0.2);
        font-family: 'Courier New', monospace;
    }
    
    /* 按鈕樣式 - 更小圓角 */
    .stButton > button {
        background: linear-gradient(135deg, #76B900 0%, #5a8f00 100%);
        color: white;
        border: 2px solid #76B900;
        border-radius: 6px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #5a8f00 0%, #76B900 100%);
        box-shadow: 0 0 20px rgba(118, 185, 0, 0.5);
        transform: translateY(-2px);
    }
    
    /* 文字輸入框樣式 - 更小圓角 */
    .stTextArea > div > div > textarea {
        background-color: #1a1a1a;
        color: #ffffff;
        border: 2px solid #76B900;
        border-radius: 6px;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #00ff41;
        box-shadow: 0 0 10px rgba(0, 255, 65, 0.3);
    }
    
    /* 標籤頁樣式 */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #1a1a1a;
        border-radius: 6px;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #76B900;
        background-color: #1a1a1a;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #2d2d2d;
    }
    
    /* 分隔線樣式 */
    hr {
        border-color: #76B900;
        background-color: #76B900;
    }
    
    /* 一般文字顏色 */
    p, li, div {
        color: #cccccc;
    }
    
    /* 標題顏色 */
    h1, h2, h3, h4, h5, h6 {
        color: #76B900;
        font-weight: 600;
    }
    
    /* Markdown內容顏色 */
    .markdown-text-container {
        color: #ffffff;
    }
    
    /* 警告和錯誤訊息樣式 */
    .stAlert {
        background-color: #1a1a1a;
        border: 2px solid #ff4444;
        color: #ffffff;
        border-radius: 6px;
    }
    
    .stSuccess {
        background-color: #1a1a1a;
        border: 2px solid #76B900;
        color: #ffffff;
        border-radius: 6px;
    }
    
    /* 載入動畫樣式 */
    .stSpinner {
        color: #76B900;
    }
</style>
""", unsafe_allow_html=True)

# 初始化session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'chain' not in st.session_state:
    st.session_state.chain = get_chain()
if 'generated_codes' not in st.session_state:
    st.session_state.generated_codes = []

# 主標題
st.markdown('<h1 class="stTitle">Omniverse 語意整合平台</h1>', unsafe_allow_html=True)
st.markdown('<p class="big-font">企業級智能語意分析與協作開發環境</p>', unsafe_allow_html=True)

# 側邊欄
with st.sidebar:
    st.markdown("### 🎛️ 平台控制")
    
    # 語音狀態顯示
    voice_manager = get_voice_manager()
    
    st.markdown("**🎤 語音狀態**")
    if voice_manager.mic_available:
        st.success("✅ 麥克風就緒")
    else:
        st.error("❌ 麥克風未就緒")
    
    if voice_manager.tts_engine:
        st.success("✅ 語音合成就緒")
    else:
        st.error("❌ 語音合成未就緒")
    
    # 語音診斷工具
    with st.expander("🔧 語音診斷", expanded=False):
        if st.button("🔍 測試麥克風", key="test_mic_sidebar"):
            test_result = voice_manager.test_microphone()
            if "error" in test_result:
                st.error(f"❌ {test_result['error']}")
            else:
                st.success("✅ 麥克風測試通過")
                st.info(f"能量閾值: {test_result['energy_threshold']}")
        
        if st.button("⏹️ 停止語音", key="stop_voice_sidebar"):
            voice_manager.stop_speaking()
            st.info("⏹️ 已停止")
        
        if st.button("🔄 重置語音引擎", key="reset_voice"):
            st.cache_resource.clear()
            st.success("✅ 已重置")
    
    st.markdown("---")
    
    st.markdown("### 🌟 核心功能")
    st.markdown("""
    **語意整合**
    - 深度技術分析
    - 最佳實踐建議
    - 上下文理解

    **代碼生成**
    - 自然語言轉代碼
    - 安全執行環境
    - 即時預覽功能
    
    **語音互動**
    - 語音提問直接回覆
    - AI 回覆自動朗讀
    - 免手動操作
    """)
    
    # 狀態顯示
    code_gen_status = "已啟用" if CODE_GEN_AVAILABLE else "模擬模式"
    st.markdown(f"""
    <div class="status-box">
        <strong>系統狀態：</strong> 運行中<br>
        <strong>語意引擎：</strong> Ollama (llama3.2:3b)<br>
        <strong>代碼生成：</strong> {code_gen_status}
    </div>
    """, unsafe_allow_html=True)
    
    # 清除對話按鈕
    if st.button("🗑️ 清除會話記錄", type="secondary"):
        st.session_state.messages = []
        st.session_state.generated_codes = []
        if 'last_ai_response' in st.session_state:
            del st.session_state['last_ai_response']
        st.rerun()

# 主要內容區域 - 使用標籤頁
tab1, tab2, tab3 = st.tabs(["🧠 語意查詢", "🤖 代碼生成器", "📝 執行記錄"])

# 標籤頁 1: 語意查詢 (整合語音功能)
with tab1:
    # 簡化的語音控制
    voice_manager = get_voice_manager()
    
    voice_col1, voice_col2, voice_col3 = st.columns([2, 2, 6])
    
    with voice_col1:
        if st.button("🎤 語音提問", key="voice_input_main", use_container_width=True):
            if voice_manager.mic_available:
                with st.spinner("🎤 正在聽您說話..."):
                    recognized_text = voice_manager.listen_for_speech(timeout=15, phrase_timeout=5)
                    
                if recognized_text:
                    st.success(f"✅ {recognized_text}")
                    
                    # 直接處理語音查詢，自動提交
                    st.session_state.messages.append({"role": "user", "content": recognized_text})
                    
                    with st.spinner('🧠 AI 分析中...'):
                        try:
                            # 調用AI鏈
                            response = st.session_state.chain.invoke({"topic": recognized_text})
                            
                            # 添加AI回應
                            st.session_state.messages.append({"role": "assistant", "content": response})
                            
                            # 保存最新回應供語音播放
                            st.session_state.last_ai_response = response
                            
                            # 自動朗讀回覆
                            voice_manager.speak_text(response)
                            
                            # 重新運行以更新界面
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ 系統錯誤：{str(e)}")
                else:
                    st.error("❌ 未識別到語音，請重試")
            else:
                st.error("❌ 麥克風不可用")
    
    with voice_col2:
        if st.button("🔊 重播回覆", key="voice_read_response", use_container_width=True):
            if 'last_ai_response' in st.session_state and st.session_state.last_ai_response:
                voice_manager.speak_text(st.session_state.last_ai_response)
                st.success("🔊 正在播放...")
            else:
                st.warning("⚠️ 沒有回覆內容")
    
    with voice_col3:
        st.empty()  # 留白空間
    
    st.markdown("---")

    # 支援的組件展示
    st.markdown("## 支援的技術領域")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        - **USD** Universal Scene Description
        - **Omniverse Kit** 核心開發平台
        """)
    with col2:
        st.markdown("""
        - **Extensions** 擴展開發框架
        - **Connectors** 第三方軟體整合
        """)
    with col3:
        st.markdown("""
        - **RTX Rendering** 即時渲染技術
        - **Physics Simulation** 物理模擬引擎
        """)

    st.markdown("---")

    # 對話記錄顯示
    st.markdown("## 對話歷程")
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="query-box">
                <strong>🎯 查詢內容：</strong><br>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="response-box">
                <strong>🤖 AI 回應：</strong><br>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)

    # 查詢輸入
    st.markdown("## 語意查詢介面")

    # 範例問題
    st.markdown("### 常見查詢範例")
    example_col1, example_col2 = st.columns(2)

    with example_col1:
        if st.button("USD 場景架構分析"):
            example_query = "分析 USD 場景的核心架構組件與層級結構設計原則"
            st.session_state.example_query = example_query
        
        if st.button("RTX 渲染管線配置"):
            example_query = "說明 RTX 渲染管線的核心參數配置與優化策略"
            st.session_state.example_query = example_query

    with example_col2:
        if st.button("Extension 開發架構"):
            example_query = "Omniverse Extension 的架構設計模式與核心 API 介面"
            st.session_state.example_query = example_query
        
        if st.button("Physics 引擎整合"):
            example_query = "Physics 模擬引擎與場景物件的整合實作方式"
            st.session_state.example_query = example_query

    # 檢查範例查詢
    initial_query = ""
    if 'example_query' in st.session_state:
        initial_query = st.session_state.example_query
        del st.session_state.example_query

    # 用戶輸入區域
    user_query = st.text_area(
        "請輸入您的技術查詢（或使用🎤語音提問）：",
        value=initial_query,
        height=100,
        placeholder="例如：如何實作 USD Stage 的層級變換與屬性繼承機制？",
        key="semantic_query"
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        submit_button = st.button("🚀 提交查詢", type="primary", use_container_width=True)

    # 處理文字查詢
    if submit_button and user_query.strip():
        # 添加用戶消息
        st.session_state.messages.append({"role": "user", "content": user_query})
        
        # 顯示載入動畫
        with st.spinner('🧠 AI 正在深度分析中...'):
            try:
                # 調用AI鏈
                response = st.session_state.chain.invoke({"topic": user_query})
                
                # 添加AI回應
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                # 保存最新回應供語音播放
                st.session_state.last_ai_response = response
                
                # 重新運行以更新界面
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ 系統錯誤：{str(e)}")
                st.error("請確認 Ollama 語意引擎服務正常運行，且 llama3.2:3b 模型已正確載入。")

    elif submit_button and not user_query.strip():
        st.warning("⚠️ 請輸入查詢內容或使用語音輸入。")

# 標籤頁 2: 代碼生成器
with tab2:
    st.markdown("## Omniverse Python 代碼生成器")
    
    if not CODE_GEN_AVAILABLE:
        st.warning("代碼生成器目前運行在模擬模式，無法實際執行 Omniverse 命令")
    
    # 代碼生成範例按鈕
    st.markdown("### 快速生成範例")
    code_col1, code_col2 = st.columns(2)
    
    with code_col1:
        if st.button("創建基礎幾何物件"):
            code_request = "創建一個立方體、球體和圓柱體，並設置它們的位置和材質"
            st.session_state.code_request = code_request
        
        if st.button("設置場景燈光"):
            code_request = "在場景中添加環境光和方向光，並配置陰影設定"
            st.session_state.code_request = code_request
    
    with code_col2:
        if st.button("創建動畫序列"):
            code_request = "為物件創建旋轉和移動動畫，設定關鍵幀"
            st.session_state.code_request = code_request
        
        if st.button("批量操作物件"):
            code_request = "批量選擇場景中的物件並統一修改它們的屬性"
            st.session_state.code_request = code_request
    
    # 代碼需求輸入
    if 'code_request' in st.session_state:
        code_input = st.session_state.code_request
        del st.session_state.code_request
    else:
        code_input = ""
    
    user_code_request = st.text_area(
        "請描述您需要的 Omniverse 操作：",
        value=code_input,
        height=120,
        placeholder="例如：創建一個有10個隨機位置立方體的場景，每個立方體都有不同的顏色材質",
        key="code_request_input"
    )
    
    # 代碼生成設定
    col1, col2, col3 = st.columns(3)
    with col1:
        safe_mode = st.checkbox("安全模式", value=True, help="啟用代碼安全檢查")
    with col2:
        add_comments = st.checkbox("添加註釋", value=True, help="在生成的代碼中添加詳細註釋")
    with col3:
        error_handling = st.checkbox("錯誤處理", value=True, help="添加 try/except 錯誤處理")
    
    # 生成按鈕
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_button = st.button("生成 Python 代碼", type="primary", use_container_width=True)
    
    # 處理代碼生成
    if generate_button and user_code_request.strip():
        with st.spinner('AI 正在生成代碼...'):
            try:
                if CODE_GEN_AVAILABLE:
                    # 使用真實的代碼生成器
                    result = omniverse_code_gen.generate_code(user_code_request)
                else:
                    # 模擬模式
                    result = {
                        "status": "success",
                        "code": f"""# 模擬生成的代碼 - {user_code_request}
import omni.usd
import omni.kit.commands
from pxr import Usd, UsdGeom, Gf

try:
    # 獲取當前 Stage
    stage = omni.usd.get_context().get_stage()
    
    # 模擬操作代碼
    print("執行用戶請求：{user_code_request}")
    
    # 這裡是生成的代碼內容
    # (在實際環境中會由 AI 生成具體的 Omniverse 操作)
    
except Exception as e:
    print(f"執行錯誤：{{e}}")""",
                        "explanation": "這是模擬生成的代碼，在實際 Omniverse 環境中會生成真實可執行的代碼。"
                    }
                
                if result["status"] == "success":
                    # 顯示生成的代碼
                    st.markdown("### 生成的代碼")
                    st.code(result["code"], language="python")
                    
                    # 顯示說明
                    if "explanation" in result and result["explanation"]:
                        st.markdown("### 代碼說明")
                        st.markdown(result["explanation"])
                    
                    # 保存到會話狀態
                    st.session_state.generated_codes.append({
                        "request": user_code_request,
                        "code": result["code"],
                        "timestamp": time.time(),
                        "explanation": result.get("explanation", "")
                    })
                    
                    # 執行選項
                    st.markdown("### 執行選項")
                    exec_col1, exec_col2 = st.columns(2)
                    
                    with exec_col1:
                        if st.button("立即執行代碼"):
                            if CODE_GEN_AVAILABLE:
                                exec_result = omniverse_code_gen.execute_code(result["code"], safe_mode)
                                if exec_result["status"] == "success":
                                    st.success("代碼執行成功！")
                                    if exec_result["stdout"]:
                                        st.text_area("執行輸出", exec_result["stdout"], height=100)
                                else:
                                    st.error(f"執行失敗：{exec_result['error']}")
                            else:
                                st.info("模擬模式：代碼已準備就緒，請複製到 Omniverse 中執行")
                    
                    with exec_col2:
                        if st.button("複製到剪貼板"):
                            try:
                                import pyperclip
                                pyperclip.copy(result["code"])
                                st.success("代碼已複製到剪貼板！")
                            except ImportError:
                                st.warning("請手動複製代碼")
                
                else:
                    st.error(f"代碼生成失敗：{result.get('error', '未知錯誤')}")
                    
            except Exception as e:
                st.error(f"系統錯誤：{str(e)}")
    
    elif generate_button and not user_code_request.strip():
        st.warning("請描述您需要的 Omniverse 操作")

# 標籤頁 3: 執行記錄
with tab3:
    st.markdown("## 代碼生成與執行記錄")
    
    if st.session_state.generated_codes:
        for i, record in enumerate(reversed(st.session_state.generated_codes)):
            with st.expander(f"記錄 {len(st.session_state.generated_codes) - i}: {record['request'][:50]}..."):
                st.markdown("**原始需求：**")
                st.write(record['request'])
                
                st.markdown("**生成時間：**")
                st.write(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(record['timestamp'])))
                
                st.markdown("**生成的代碼：**")
                st.code(record['code'], language="python")
                
                if record['explanation']:
                    st.markdown("**說明：**")
                    st.write(record['explanation'])
                
                # 重新執行按鈕
                if st.button(f"重新執行代碼 {len(st.session_state.generated_codes) - i}", key=f"reexec_{i}"):
                    if CODE_GEN_AVAILABLE:
                        exec_result = omniverse_code_gen.execute_code(record['code'], True)
                        if exec_result["status"] == "success":
                            st.success("重新執行成功！")
                        else:
                            st.error(f"重新執行失敗：{exec_result['error']}")
                    else:
                        st.info("模擬模式：請複製代碼到 Omniverse 中執行")
    else:
        st.info("尚無代碼生成記錄")
        st.markdown("前往 **代碼生成器** 標籤頁開始生成您的第一個 Omniverse 腳本！")

# 頁腳
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #76B900; padding: 2rem;">
    <p><strong>Omniverse 語意整合平台</strong> | 
    基於 <strong>LangChain</strong> 語意框架 與 <strong>Ollama</strong> 本地推理引擎 | 
    <strong>Streamlit</strong> 企業級界面</p>
    <p style="color: #cccccc;"><em>提升團隊協作效率，加速 Omniverse 項目開發進程</em></p>
</div>
""", unsafe_allow_html=True) 