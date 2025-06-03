"""
Groq API 配置文件
管理 Groq LLM 服務的連接和設定
"""

from groq import Groq
from typing import Optional


class GroqConfig:
    """Groq API 配置管理器"""
    
    def __init__(self, api_key: Optional[str] = None):
        # 使用提供的 API Key
        self.api_key = api_key or "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"
        self.client = Groq(api_key=self.api_key)
        
        # 模型配置 - 使用確定可用的模型
        self.default_model = "llama3-8b-8192"    # 輕量級高效模型
        self.fast_model = "llama3-8b-8192"       # 快速回應模型  
        self.code_model = "llama3-70b-8192"      # 程式碼生成專用大模型
        
        # 生成參數
        self.default_params = {
            "temperature": 0.7,
            "max_tokens": 1000,
            "top_p": 1,
            "stream": False
        }
    
    def get_client(self) -> Groq:
        """取得 Groq 客戶端"""
        return self.client
    
    def get_model(self, task_type: str = "default") -> str:
        """根據任務類型選擇適合的模型"""
        model_mapping = {
            "default": self.default_model,
            "fast": self.fast_model,
            "code": self.code_model,
            "semantic": self.default_model,
            "generation": self.code_model
        }
        return model_mapping.get(task_type, self.default_model)
    
    def get_params(self, **overrides) -> dict:
        """取得生成參數（可覆蓋預設值）"""
        params = self.default_params.copy()
        params.update(overrides)
        return params
    
    def test_connection(self) -> bool:
        """測試 Groq API 連接"""
        try:
            response = self.client.chat.completions.create(
                model=self.fast_model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            print(f"Groq 連接測試失敗: {e}")
            return False


# 全域配置實例
groq_config = GroqConfig()
