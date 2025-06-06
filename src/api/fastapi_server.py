from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import uuid
import time
import io
import sys
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict
import traceback

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.api.api_models import (
    CodeExecuteRequest, 
    ExecutionResult, 
    ExecutionStatus, 
    HealthResponse, 
    ErrorResponse
)

# FastAPI 應用初始化
app = FastAPI(
    title="Omniverse LangChain API", 
    description="LangChain 到 Omniverse 代碼執行 API",
    version="1.0.0"
)

# CORS 設定（開發用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生產環境請限制來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 內存存儲執行結果（簡單實作）
execution_results: Dict[str, ExecutionResult] = {}

def safe_execute_code(code: str, timeout: int = 30) -> tuple[str, str, float]:
    """
    安全執行 Python 代碼
    返回: (output, error, execution_time)
    """
    start_time = time.time()
    
    # 捕獲 stdout 和 stderr
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    try:
        # 簡單的代碼安全檢查
        dangerous_keywords = ['import os', 'import subprocess', '__import__', 'eval', 'exec']
        if any(keyword in code for keyword in dangerous_keywords):
            raise ValueError("代碼包含潛在危險的操作")
        
        # 執行代碼並捕獲輸出
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            exec(code)
            
        output = stdout_capture.getvalue()
        error = stderr_capture.getvalue()
        execution_time = time.time() - start_time
        
        return output, error, execution_time
        
    except Exception as e:
        error = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        execution_time = time.time() - start_time
        return "", error, execution_time

@app.post("/execute", response_model=ExecutionResult)
async def execute_code(request: CodeExecuteRequest, background_tasks: BackgroundTasks):
    """
    執行 Python 代碼
    """
    task_id = str(uuid.uuid4())
    
    # 立即返回任務 ID，實際執行在背景進行
    result = ExecutionResult(
        task_id=task_id,
        status=ExecutionStatus.PENDING
    )
    execution_results[task_id] = result
    
    # 背景執行任務
    background_tasks.add_task(execute_in_background, task_id, request.code, request.timeout)
    
    return result

async def execute_in_background(task_id: str, code: str, timeout: int):
    """背景執行代碼"""
    try:
        # 更新狀態為執行中
        execution_results[task_id].status = ExecutionStatus.RUNNING
        
        # 執行代碼
        output, error, exec_time = safe_execute_code(code, timeout)
        
        # 更新結果
        if error:
            execution_results[task_id].status = ExecutionStatus.ERROR
            execution_results[task_id].error_message = error
        else:
            execution_results[task_id].status = ExecutionStatus.SUCCESS
            execution_results[task_id].output = output
            
        execution_results[task_id].execution_time = exec_time
        
    except Exception as e:
        execution_results[task_id].status = ExecutionStatus.ERROR
        execution_results[task_id].error_message = str(e)

@app.get("/status/{task_id}", response_model=ExecutionResult)
async def get_execution_status(task_id: str):
    """
    查詢任務執行狀態
    """
    if task_id not in execution_results:
        raise HTTPException(status_code=404, detail="任務 ID 不存在")
    
    return execution_results[task_id]

@app.get("/healthz", response_model=HealthResponse)
async def health_check():
    """
    健康檢查端點
    """
    return HealthResponse()

@app.get("/")
async def root():
    """
    根端點
    """
    return {
        "message": "Omniverse LangChain API 服務運行中",
        "docs": "/docs",
        "health": "/healthz"
    }

if __name__ == "__main__":
    uvicorn.run("src.api.fastapi_server:app", host="0.0.0.0", port=8000, reload=True) 