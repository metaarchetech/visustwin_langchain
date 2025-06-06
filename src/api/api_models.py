from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ExecutionStatus(str, Enum):
    """執行狀態枚舉"""
    PENDING = "pending"     # 等待執行
    RUNNING = "running"     # 執行中  
    SUCCESS = "success"     # 執行成功
    ERROR = "error"         # 執行錯誤

class CodeExecuteRequest(BaseModel):
    """代碼執行請求模型"""
    code: str = Field(..., description="要執行的 Python 代碼", min_length=1)
    user_id: Optional[str] = Field(None, description="用戶 ID（可選）")
    timeout: Optional[int] = Field(30, description="執行超時時間（秒）", ge=1, le=300)
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "print('Hello Omniverse!')",
                "user_id": "user_001",
                "timeout": 30
            }
        }

class ExecutionResult(BaseModel):
    """執行結果模型"""
    task_id: str = Field(..., description="任務 ID")
    status: ExecutionStatus = Field(..., description="執行狀態")
    output: Optional[str] = Field(None, description="執行輸出")
    error_message: Optional[str] = Field(None, description="錯誤訊息")
    execution_time: Optional[float] = Field(None, description="執行時間（秒）")
    timestamp: datetime = Field(default_factory=datetime.now, description="時間戳")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task_12345",
                "status": "success",
                "output": "Hello Omniverse!",
                "error_message": None,
                "execution_time": 0.05,
                "timestamp": "2024-01-01T12:00:00"
            }
        }

class HealthResponse(BaseModel):
    """健康檢查回應模型"""
    status: str = Field("healthy", description="服務狀態")
    timestamp: datetime = Field(default_factory=datetime.now, description="檢查時間")
    version: str = Field("1.0.0", description="API 版本")
    
class ErrorResponse(BaseModel):
    """錯誤回應模型"""
    error: str = Field(..., description="錯誤類型")
    message: str = Field(..., description="錯誤描述")
    task_id: Optional[str] = Field(None, description="相關任務 ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="錯誤時間") 