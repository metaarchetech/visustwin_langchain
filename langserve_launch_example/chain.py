"""This is a template for a custom chain.

Edit this file to implement your chain logic.
"""

from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.schema.runnable import Runnable
from langchain.schema.output_parser import StrOutputParser
from groq_config import engine_config


def get_chain() -> Runnable:
    """Return a chain for Omniverse semantic integration platform."""
    
    # 根據當前引擎選擇合適的提示模板
    if engine_config.get_current_engine() == "groq":
        # Groq 使用 ChatPromptTemplate
        prompt = ChatPromptTemplate.from_messages([
            ("system", """您是 Omniverse 語意整合平台的核心分析引擎，專門協助企業團隊深度理解與有效運用 Omniverse 技術生態系統。

請基於 Omniverse 平台的技術架構，提供專業的分析與建議：

            請根據以下框架提供專業分析（全部使用中文）：
            1. 技術架構：核心組件與依賴關係
            2. 實作策略：具體步驟與最佳實踐
            3. 整合方案：與其他 Omniverse 服務的協作方式
            4. 注意事項：開發時需關注的關鍵點"""),
            ("human", "{topic}")
        ])
    else:
        # Ollama 使用 PromptTemplate
        prompt = PromptTemplate(
            input_variables=["input"],
            template="""
            您現在是 Omniverse 語意整合平台的中文專屬助手，請嚴格使用中文回答所有問題。

            技術問題：{input}

            請根據以下框架提供專業分析（全部使用中文）：
            1. 技術架構：核心組件與依賴關係
            2. 實作策略：具體步驟與最佳實踐
            3. 整合方案：與其他 Omniverse 服務的協作方式
            4. 注意事項：開發時需關注的關鍵點

            回答時請避免混用英文，除非是專業術語（如 USD、RTX）。
            """
        )
    
    # 使用統一引擎配置創建模型實例
    model = engine_config.create_model_instance(
        task_type="semantic",
        temperature=0.7,
        max_tokens=1000
    )
    
    # 使用字串輸出解析器
    parser = StrOutputParser()
    
    return prompt | model | parser
