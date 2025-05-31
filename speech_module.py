"""
Omniverse 語音互動模組
支援語音輸入和語音輸出功能
"""

import streamlit as st
import speech_recognition as sr
import pyttsx3
import threading
import time
import tempfile
import os
import asyncio
from typing import Optional, Dict, Any
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceInteractionManager:
    """語音互動管理器"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.tts_engine = None
        self.is_listening = False
        self.is_speaking = False
        self.mic_available = False
        self._setup_microphone()
        self._setup_tts()
    
    def _setup_microphone(self):
        """設置麥克風"""
        try:
            # 檢查可用的麥克風
            mic_list = sr.Microphone.list_microphone_names()
            logger.info(f"可用麥克風: {mic_list}")
            
            if mic_list:
                self.microphone = sr.Microphone()
                self._calibrate_microphone()
                self.mic_available = True
                logger.info("麥克風設置成功")
            else:
                logger.error("未檢測到麥克風")
                self.mic_available = False
        except Exception as e:
            logger.error(f"麥克風設置失敗: {e}")
            self.mic_available = False
    
    def _setup_tts(self):
        """設置文字轉語音引擎"""
        try:
            self.tts_engine = pyttsx3.init()
            # 設置語音參數
            voices = self.tts_engine.getProperty('voices')
            logger.info(f"可用語音: {len(voices)} 種")
            
            # 嘗試找到中文語音
            for i, voice in enumerate(voices):
                logger.info(f"語音 {i}: {voice.name}")
                if 'chinese' in voice.name.lower() or 'mandarin' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    logger.info(f"設置中文語音: {voice.name}")
                    break
            
            # 設置語速和音量
            self.tts_engine.setProperty('rate', 200)  # 語速
            self.tts_engine.setProperty('volume', 0.8)  # 音量
            
            logger.info("TTS 引擎設置成功")
            
        except Exception as e:
            logger.error(f"TTS 引擎初始化失敗: {e}")
            self.tts_engine = None
    
    def _calibrate_microphone(self):
        """校準麥克風"""
        try:
            with self.microphone as source:
                logger.info("正在校準麥克風...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            logger.info("麥克風校準完成")
        except Exception as e:
            logger.error(f"麥克風校準失敗: {e}")
    
    def test_microphone(self) -> Dict[str, Any]:
        """測試麥克風功能"""
        result = {
            "available": self.mic_available,
            "energy_threshold": 0,
            "ambient_noise": "未測試"
        }
        
        if not self.mic_available:
            result["error"] = "麥克風不可用"
            return result
        
        try:
            with self.microphone as source:
                # 測試環境噪音
                logger.info("測試環境噪音...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                result["energy_threshold"] = self.recognizer.energy_threshold
                result["ambient_noise"] = "正常"
                
                # 錄製測試音頻
                logger.info("請說話測試...")
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=2)
                result["test_recording"] = "成功錄製音頻"
                
        except sr.WaitTimeoutError:
            result["test_recording"] = "超時 - 未檢測到語音"
        except Exception as e:
            result["error"] = f"測試失敗: {e}"
        
        return result
    
    def listen_for_speech(self, timeout: int = 10, phrase_timeout: int = 3, use_offline: bool = False) -> Optional[str]:
        """
        監聽語音輸入
        
        Args:
            timeout: 監聽超時時間
            phrase_timeout: 短語結束超時時間
            use_offline: 是否使用離線識別
            
        Returns:
            識別到的文字，如果失敗則返回 None
        """
        if not self.mic_available:
            logger.error("麥克風不可用")
            return None
        
        try:
            self.is_listening = True
            
            with self.microphone as source:
                logger.info(f"正在監聽... (超時: {timeout}秒)")
                # 調整能量閾值
                self.recognizer.energy_threshold = max(300, self.recognizer.energy_threshold)
                
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_timeout
                )
            
            logger.info("正在識別語音...")
            
            if use_offline:
                # 使用離線識別 (需要安裝額外的模型)
                try:
                    text = self.recognizer.recognize_sphinx(audio, language='zh-cn')
                    logger.info(f"離線識別結果: {text}")
                except sr.UnknownValueError:
                    logger.warning("離線識別失敗，嘗試在線識別...")
                    text = self.recognizer.recognize_google(audio, language='zh-TW')
            else:
                # 使用在線 Google 識別
                text = self.recognizer.recognize_google(audio, language='zh-TW')
            
            logger.info(f"識別結果: {text}")
            return text
            
        except sr.WaitTimeoutError:
            logger.warning("語音輸入超時 - 請檢查麥克風是否工作")
            return None
        except sr.UnknownValueError:
            logger.warning("無法識別語音 - 請說得更清楚或檢查網路連接")
            return None
        except sr.RequestError as e:
            logger.error(f"語音識別服務錯誤: {e}")
            return None
        except Exception as e:
            logger.error(f"語音識別錯誤: {e}")
            return None
        finally:
            self.is_listening = False
    
    def speak_text(self, text: str, async_mode: bool = True):
        """
        文字轉語音播放
        
        Args:
            text: 要播放的文字
            async_mode: 是否異步播放
        """
        if not self.tts_engine:
            logger.warning("TTS 引擎未初始化")
            return
        
        if async_mode:
            threading.Thread(target=self._speak_sync, args=(text,), daemon=True).start()
        else:
            self._speak_sync(text)
    
    def _speak_sync(self, text: str):
        """同步語音播放"""
        try:
            self.is_speaking = True
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            logger.error(f"語音播放錯誤: {e}")
        finally:
            self.is_speaking = False
    
    def stop_speaking(self):
        """停止語音播放"""
        if self.tts_engine:
            try:
                self.tts_engine.stop()
                self.is_speaking = False
            except Exception as e:
                logger.error(f"停止語音播放錯誤: {e}")

# 創建全局語音管理器實例
@st.cache_resource
def get_voice_manager():
    """獲取語音管理器實例"""
    return VoiceInteractionManager()

def create_voice_interface():
    """創建語音界面組件"""
    voice_manager = get_voice_manager()
    
    st.markdown("### 🎤 語音互動")
    
    # 麥克風狀態檢查
    if not voice_manager.mic_available:
        st.error("❌ 麥克風不可用！請檢查麥克風連接和權限設置。")
        return None
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🎤 開始語音輸入", key="voice_input_btn"):
            if not voice_manager.is_listening:
                with st.spinner("正在監聽您的語音..."):
                    # 使用更長的超時時間
                    recognized_text = voice_manager.listen_for_speech(timeout=15, phrase_timeout=5)
                    
                if recognized_text:
                    st.success(f"✅ 識別成功: {recognized_text}")
                    st.session_state.voice_input = recognized_text
                else:
                    st.error("❌ 語音識別失敗，請重試")
                    st.info("💡 提示：請檢查網路連接，確保說話清晰，麥克風靠近嘴部")
            else:
                st.warning("⚠️ 正在監聽中...")
    
    with col2:
        if st.button("🔊 語音回覆", key="voice_output_btn"):
            if 'last_response' in st.session_state and st.session_state.last_response:
                voice_manager.speak_text(st.session_state.last_response)
                st.success("🔊 正在播放語音回覆")
            else:
                st.warning("⚠️ 沒有可播放的回覆內容")
    
    with col3:
        if st.button("⏹️ 停止語音", key="stop_voice_btn"):
            voice_manager.stop_speaking()
            st.info("⏹️ 語音播放已停止")
    
    # 測試功能
    st.markdown("### 🧪 語音診斷")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 測試麥克風", key="test_mic_btn"):
            with st.spinner("正在測試麥克風..."):
                test_result = voice_manager.test_microphone()
            
            if "error" in test_result:
                st.error(f"❌ {test_result['error']}")
            else:
                st.success("✅ 麥克風測試完成")
                st.info(f"""
                **測試結果:**
                - 麥克風可用: {test_result['available']}
                - 能量閾值: {test_result['energy_threshold']}
                - 環境噪音: {test_result['ambient_noise']}
                - 錄音測試: {test_result.get('test_recording', '未測試')}
                """)
    
    with col2:
        if st.button("🎵 測試語音合成", key="test_tts_btn"):
            test_text = "這是語音測試，如果您能聽到這段話，說明語音合成功能正常"
            voice_manager.speak_text(test_text)
            st.success("🔊 語音合成測試中...")
    
    # 語音設定選項
    with st.expander("⚙️ 進階設定", expanded=False):
        offline_mode = st.checkbox("離線模式", value=False, help="使用離線語音識別（需要額外模型）")
        longer_timeout = st.checkbox("延長監聽時間", value=False, help="增加語音輸入的等待時間")
        
        if st.button("🔄 重新初始化語音引擎"):
            # 重新初始化語音管理器
            if 'voice_manager' in st.session_state:
                del st.session_state['voice_manager']
            st.cache_resource.clear()
            st.success("✅ 語音引擎已重新初始化")
            st.rerun()
    
    # 顯示語音輸入結果
    if 'voice_input' in st.session_state and st.session_state.voice_input:
        st.markdown("**🎤 語音輸入內容:**")
        st.info(st.session_state.voice_input)
        
        # 將語音輸入自動填入查詢框
        if st.button("📝 使用語音輸入", key="use_voice_input"):
            return st.session_state.voice_input
    
    return None

def create_voice_settings():
    """創建語音設定界面"""
    st.markdown("### ⚙️ 語音設定")
    
    # 語音引擎狀態
    voice_manager = get_voice_manager()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🎤 語音識別狀態**")
        if voice_manager.mic_available and voice_manager.recognizer:
            st.success("✅ 語音識別已就緒")
            
            # 顯示麥克風詳細信息
            try:
                mic_list = sr.Microphone.list_microphone_names()
                st.info(f"檢測到 {len(mic_list)} 個麥克風設備")
                for i, name in enumerate(mic_list[:3]):  # 只顯示前3個
                    st.text(f"{i+1}. {name}")
            except:
                st.text("無法獲取麥克風列表")
        else:
            st.error("❌ 語音識別未就緒")
        
        if voice_manager.is_listening:
            st.warning("🎤 正在監聽...")
        else:
            st.info("🔇 待機中")
    
    with col2:
        st.markdown("**🔊 語音合成狀態**")
        if voice_manager.tts_engine:
            st.success("✅ 語音合成已就緒")
            
            # 顯示語音引擎詳細信息
            try:
                voices = voice_manager.tts_engine.getProperty('voices')
                st.info(f"可用語音: {len(voices)} 種")
                current_voice = voice_manager.tts_engine.getProperty('voice')
                st.text(f"當前語音: {current_voice}")
            except:
                st.text("無法獲取語音引擎信息")
        else:
            st.error("❌ 語音合成未就緒")
        
        if voice_manager.is_speaking:
            st.warning("🔊 正在播放...")
        else:
            st.info("🔇 靜音中")
    
    # 故障排除建議
    st.markdown("**🔧 故障排除**")
    st.info("""
    **常見問題解決方案:**
    1. **語音識別失敗**: 檢查網路連接和麥克風權限
    2. **麥克風不可用**: 確認麥克風已連接並在 Windows 設定中啟用
    3. **語音合成無聲音**: 檢查系統音量和音頻輸出設備
    4. **權限問題**: 允許瀏覽器使用麥克風權限
    """)
    
    # 測試功能
    st.markdown("**🧪 語音測試**")
    test_text = st.text_input("測試語音合成", value="您好，這是 Omniverse 語意整合平台的語音測試。")
    
    if st.button("🔊 測試語音播放", key="test_voice"):
        voice_manager.speak_text(test_text)
        st.success("🔊 測試語音播放中...")

# 語音指令處理器
class VoiceCommandProcessor:
    """語音指令處理器"""
    
    def __init__(self):
        self.commands = {
            "查詢": self._handle_query,
            "生成代碼": self._handle_code_generation,
            "停止": self._handle_stop,
            "清除": self._handle_clear,
            "幫助": self._handle_help,
        }
    
    def process_command(self, text: str) -> Dict[str, Any]:
        """
        處理語音指令
        
        Args:
            text: 識別到的語音文字
            
        Returns:
            處理結果字典
        """
        text = text.strip()
        
        for command, handler in self.commands.items():
            if command in text:
                return handler(text)
        
        # 如果沒有匹配到特定指令，當作一般查詢處理
        return self._handle_query(text)
    
    def _handle_query(self, text: str) -> Dict[str, Any]:
        """處理查詢指令"""
        return {
            "action": "query",
            "content": text,
            "message": f"正在查詢: {text}"
        }
    
    def _handle_code_generation(self, text: str) -> Dict[str, Any]:
        """處理代碼生成指令"""
        # 移除指令關鍵字，保留實際需求
        content = text.replace("生成代碼", "").strip()
        return {
            "action": "generate_code",
            "content": content,
            "message": f"正在生成代碼: {content}"
        }
    
    def _handle_stop(self, text: str) -> Dict[str, Any]:
        """處理停止指令"""
        return {
            "action": "stop",
            "content": "",
            "message": "已停止當前操作"
        }
    
    def _handle_clear(self, text: str) -> Dict[str, Any]:
        """處理清除指令"""
        return {
            "action": "clear",
            "content": "",
            "message": "已清除輸入內容"
        }
    
    def _handle_help(self, text: str) -> Dict[str, Any]:
        """處理幫助指令"""
        help_text = """
        可用的語音指令：
        • 查詢 + 問題：進行語意查詢
        • 生成代碼 + 需求：生成 Omniverse 代碼
        • 停止：停止當前操作
        • 清除：清除輸入內容
        • 幫助：顯示此幫助信息
        """
        return {
            "action": "help",
            "content": help_text,
            "message": "語音指令幫助"
        } 