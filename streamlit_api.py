from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from langserve_launch_example.chain import get_chain
import threading
import asyncio

# 創建 FastAPI 應用
app = FastAPI(
    title="Omniverse Semantic API",
    description="為 Omniverse Extension 提供 API 介面",
    version="1.0.0"
)

# 設置 CORS 中間件，允許來自 Omniverse 的請求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生產環境中應該限制為特定來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 請求模型
class QueryRequest(BaseModel):
    query: str
    context: dict = {}

class QueryResponse(BaseModel):
    response: str
    status: str
    execution_time: float

# 初始化 AI 鏈
chain = get_chain()

@app.get("/health")
async def health_check():
    """健康檢查端點"""
    return {"status": "healthy", "service": "omniverse-semantic-api"}

@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """處理語意查詢請求"""
    try:
        import time
        start_time = time.time()
        
        # 調用 AI 鏈處理查詢
        response = chain.invoke({"topic": request.query})
        
        execution_time = time.time() - start_time
        
        return QueryResponse(
            response=response,
            status="success",
            execution_time=execution_time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query processing failed: {str(e)}"
        )

@app.get("/api/status")
async def get_service_status():
    """獲取服務狀態"""
    return {
        "service": "omniverse-semantic-api",
        "status": "running",
        "ai_model": "ollama-llama3.2:3b",
        "features": {
            "semantic_analysis": True,
            "knowledge_integration": True,
            "collaborative_development": True
        }
    }

@app.post("/api/scene/analyze")
async def analyze_scene_context(scene_data: dict):
    """分析場景上下文並提供建議"""
    try:
        # 基於場景資料生成語意查詢
        scene_summary = f"場景包含 {len(scene_data.get('objects', []))} 個物件"
        query = f"分析以下 Omniverse 場景並提供優化建議：{scene_summary}"
        
        response = chain.invoke({"topic": query})
        
        return {
            "analysis": response,
            "scene_objects_count": len(scene_data.get('objects', [])),
            "recommendations": [
                "考慮使用 LOD (Level of Detail) 優化渲染效能",
                "檢查材質節點的複雜度",
                "確保物理屬性設定正確"
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Scene analysis failed: {str(e)}"
        )

def run_api_server():
    """在背景執行 API 服務器"""
    uvicorn.run(app, host="localhost", port=8503, log_level="info")

if __name__ == "__main__":
    # 直接運行 API 服務器
    run_api_server()
else:
    # 當作為模組導入時，在背景線程運行
    api_thread = threading.Thread(target=run_api_server, daemon=True)
    api_thread.start() 