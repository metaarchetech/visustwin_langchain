"""This is a template for a custom chain.

Edit this file to implement your chain logic.
"""

from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import Runnable
from langchain.schema.output_parser import StrOutputParser


def get_chain() -> Runnable:
    """Return a chain for Omniverse semantic integration platform."""
    
    # 創建 Omniverse 語意整合平台的提示模板
    prompt = PromptTemplate.from_template(
        """您是 Omniverse 語意整合平台的核心分析引擎，專門協助企業團隊深度理解與有效運用 Omniverse 技術生態系統。

技術查詢：{topic}

請基於 Omniverse 平台的技術架構，提供專業的分析與建議：

1. 技術架構分析：識別相關的核心組件、API 介面與系統依賴關係
2. 實作策略建議：提供具體的技術實作路徑與最佳實踐方案  
3. 整合方案設計：說明與其他 Omniverse 服務的協作整合模式
4. 開發指導原則：基於企業級開發標準的技術規範與注意事項

針對不同技術領域（USD、RTX Rendering、Physics Simulation、Extension Development、Connector Integration），請提供深度的技術洞察與實用的開發指引。

系統回應："""
    )
    
    # 使用 Ollama 本地模型 (llama3.2:3b 已下載完成)
    model = Ollama(model="llama3.2:3b")
    
    # 使用字串輸出解析器
    parser = StrOutputParser()
    
    return prompt | model | parser
