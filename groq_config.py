"""
統一 AI 引擎配置管理器
支援 Groq 雲端服務和 Ollama 本地服務的動態切換
"""

from groq import Groq
from typing import Optional, Dict, Any
import os
import time

try:
    from langchain_community.llms import Ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

try:
    from langchain_groq import ChatGroq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False


class UnifiedEngineConfig:
    """統一 AI 引擎配置管理器"""
    
    def __init__(self):
        # 當前引擎設定
        self.current_engine = "groq"  # 預設使用 Groq
        
        # Groq 配置
        self.groq_api_key = "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"
        self.groq_models = {
            "default": "llama3-8b-8192",
            "fast": "llama3-8b-8192",
            "code": "llama3-70b-8192",
            "semantic": "llama3-8b-8192"
        }
        
        # Ollama 配置
        self.ollama_models = {
            "default": "llama3.2:3b",
            "fast": "llama3.2:3b", 
            "code": "llama3.2:3b",
            "semantic": "llama3.2:3b"
        }
        self.ollama_base_url = "http://localhost:11434"
        
        # 通用生成參數
        self.default_params = {
            "temperature": 0.7,
            "max_tokens": 1000,
            "top_p": 1,
            "stream": False
        }
        
        # 初始化客戶端
        self._groq_client = None
        self._ollama_available = OLLAMA_AVAILABLE
        self._groq_available = GROQ_AVAILABLE
        
        # 連接狀態緩存 (避免頻繁測試)
        self._connection_cache = {}
        self._cache_duration = 30  # 緩存30秒
        self._last_cache_time = {}
    
    @property
    def groq_client(self) -> Optional[Groq]:
        """取得 Groq 客戶端"""
        if not self._groq_client and self._groq_available:
            try:
                self._groq_client = Groq(api_key=self.groq_api_key)
            except Exception as e:
                print(f"Groq 客戶端初始化失敗: {e}")
        return self._groq_client
    
    def _is_cache_valid(self, engine_name: str) -> bool:
        """檢查緩存是否仍然有效"""
        if engine_name not in self._last_cache_time:
            return False
        return time.time() - self._last_cache_time[engine_name] < self._cache_duration
    
    def _get_cached_status(self, engine_name: str) -> Optional[bool]:
        """獲取緩存的連接狀態"""
        if self._is_cache_valid(engine_name):
            return self._connection_cache.get(engine_name)
        return None
    
    def _cache_status(self, engine_name: str, status: bool):
        """緩存連接狀態"""
        self._connection_cache[engine_name] = status
        self._last_cache_time[engine_name] = time.time()
    
    def get_available_engines(self, force_test: bool = False) -> Dict[str, bool]:
        """取得可用的引擎列表"""
        engines = {}
        
        # 只測試當前引擎，其他引擎使用緩存或假設不可用
        if self.current_engine == "groq":
            # 當前使用 Groq，優先測試 Groq
            groq_status = self._get_cached_status("groq") if not force_test else None
            if groq_status is None:
                groq_status = self._groq_available and self.test_groq_connection()
                self._cache_status("groq", groq_status)
            engines["groq"] = groq_status
            
            # Ollama 使用緩存狀態，不頻繁測試
            ollama_status = self._get_cached_status("ollama")
            if ollama_status is None:
                # 只有在強制測試或者第一次時才測試 Ollama
                if force_test:
                    ollama_status = self._ollama_available and self.test_ollama_connection()
                    self._cache_status("ollama", ollama_status)
                else:
                    ollama_status = False  # 假設不可用，避免測試延遲
            engines["ollama"] = ollama_status
            
        else:  # 當前使用 Ollama
            # 當前使用 Ollama，優先測試 Ollama
            ollama_status = self._get_cached_status("ollama") if not force_test else None
            if ollama_status is None:
                ollama_status = self._ollama_available and self.test_ollama_connection()
                self._cache_status("ollama", ollama_status)
            engines["ollama"] = ollama_status
            
            # Groq 使用緩存狀態
            groq_status = self._get_cached_status("groq")
            if groq_status is None:
                if force_test:
                    groq_status = self._groq_available and self.test_groq_connection()
                    self._cache_status("groq", groq_status)
                else:
                    groq_status = True if self._groq_available else False  # 假設可用
            engines["groq"] = groq_status
        
        return engines
    
    def switch_engine(self, engine_name: str) -> bool:
        """切換 AI 引擎"""
        if engine_name not in ["groq", "ollama"]:
            return False
        
        # 強制測試目標引擎
        if engine_name == "groq":
            if not self._groq_available:
                return False
            # 測試 Groq 連接
            if not self.test_groq_connection():
                return False
        else:  # ollama
            if not self._ollama_available:
                return False
            # 測試 Ollama 連接
            if not self.test_ollama_connection():
                return False
        
        self.current_engine = engine_name
        # 清除緩存以強制重新測試
        self._connection_cache.clear()
        self._last_cache_time.clear()
        return True
    
    def get_current_engine(self) -> str:
        """取得當前引擎名稱"""
        return self.current_engine
    
    def get_model(self, task_type: str = "default") -> str:
        """根據當前引擎和任務類型選擇模型"""
        if self.current_engine == "groq":
            return self.groq_models.get(task_type, self.groq_models["default"])
        else:  # ollama
            return self.ollama_models.get(task_type, self.ollama_models["default"])
    
    def create_model_instance(self, task_type: str = "default", **kwargs):
        """創建模型實例"""
        model_name = self.get_model(task_type)
        params = self.default_params.copy()
        params.update(kwargs)
        
        if self.current_engine == "groq":
            if not self._groq_available:
                raise RuntimeError("Groq 不可用")
            return ChatGroq(
                groq_api_key=self.groq_api_key,
                model_name=model_name,
                temperature=params.get("temperature", 0.7),
                max_tokens=params.get("max_tokens", 1000)
            )
        else:  # ollama
            if not self._ollama_available:
                raise RuntimeError("Ollama 不可用")
            return Ollama(
                model=model_name,
                base_url=self.ollama_base_url,
                temperature=params.get("temperature", 0.7)
            )
    
    def test_groq_connection(self) -> bool:
        """測試 Groq 連接"""
        if not self._groq_available:
            return False
            
        try:
            client = self.groq_client
            if not client:
                return False
                
            response = client.chat.completions.create(
                model=self.groq_models["fast"],
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            print(f"Groq 連接測試失敗: {e}")
            return False
    
    def test_ollama_connection(self) -> bool:
        """測試 Ollama 連接"""
        if not self._ollama_available:
            return False
            
        try:
            import requests
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"Ollama 連接測試失敗: {e}")
            return False
    
    def get_engine_status(self, force_refresh: bool = False) -> Dict[str, Any]:
        """取得引擎詳細狀態"""
        available_engines = self.get_available_engines(force_test=force_refresh)
        
        return {
            "current_engine": self.current_engine,
            "current_model": self.get_model("semantic"),
            "available_engines": available_engines,
            "engine_details": {
                "groq": {
                    "available": available_engines.get("groq", False),
                    "models": self.groq_models,
                    "status": "雲端推理服務" if available_engines.get("groq", False) else "離線",
                    "cached": self._is_cache_valid("groq")
                },
                "ollama": {
                    "available": available_engines.get("ollama", False), 
                    "models": self.ollama_models,
                    "status": "本地推理服務" if available_engines.get("ollama", False) else "離線",
                    "cached": self._is_cache_valid("ollama")
                }
            }
        }
    
    def test_connection(self) -> bool:
        """測試當前引擎連接"""
        # 先檢查緩存
        cached_status = self._get_cached_status(self.current_engine)
        if cached_status is not None:
            return cached_status
        
        # 如果沒有緩存，則進行實際測試
        if self.current_engine == "groq":
            result = self.test_groq_connection()
        else:
            result = self.test_ollama_connection()
        
        # 緩存結果
        self._cache_status(self.current_engine, result)
        return result


# 全域配置實例
engine_config = UnifiedEngineConfig()

# 向後相容性
groq_config = engine_config  # 保持舊的介面
