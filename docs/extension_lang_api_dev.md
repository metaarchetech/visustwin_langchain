# **Omniverse FastAPI 整合式系統開發指南**

## **📂 專案結構**
### **1. LangChain + FastAPI 控制平台**
```
langchain-fastapi-controller/
├── api_models.py            # Pydantic 模型（指令結構、錯誤訊息）
├── fastapi_server.py        # FastAPI 主伺服器（指令接收、回應控制）
├── error_handler.py         # 錯誤攔截與標準化回應
├── server_config.py         # 系統設定與安全參數
├── command_queue.py         # 非同步任務處理（可選）
├── shared_schema.json       # API 輸入/輸出格式說明
└── requirements.txt         # 依賴套件清單
```

### **2. Omniverse Extension 插件端**
```
omniverse-langchain-extension/
├── omni_extension/
│   ├── extension.toml        # Omniverse Extension 註冊資訊
│   ├── main.py               # 啟動點（API 連線與指令執行）
│   ├── ui.py                 # GUI 元件（可選）
│   └── executor.py           # 安全執行函數 `safe_exec(code: str)`
└── README.md
```

---

## **🚀 功能端點與流程**
### **FastAPI 端點**
- **`POST /execute`**：提交 Python 指令並立即執行。
- **`GET /last_status`**：查詢最後執行狀態。
- **`POST /queue`**：非同步任務排程。
- **`GET /healthz`**：健康檢查。

### **Omniverse Extension 流程**
1. 啟動時輪詢 FastAPI 的 `/next_code` 或使用 Socket。
2. 呼叫 `executor.safe_exec(code)` 執行指令。
3. 回傳狀態至 `/status_update` 或共享暫存檔。

---

## **🔒 安全性機制**
- **代碼執行**：AST 解析 + 禁用危險關鍵字（如 `os.system`）。
- **API 認證**：IP/token 驗證。
- **執行限制**：時間、字數、重試次數。

---

## **📌 開發步驟**
### **Phase 1: 核心功能 (優先實作) ✅**
1. **FastAPI 最小架構**  
   - ✅ `api_models.py` - 基礎 Pydantic 模型（ExecutionStatus, CodeExecuteRequest, ExecutionResult）
   - ✅ `fastapi_server.py` - 核心 API 端點 (`POST /execute`, `GET /status/{task_id}`, `GET /healthz`)
   - ✅ `requirements_simple.txt` - 簡化版依賴清單
2. **基礎測試**  
   - 🔄 本地 FastAPI 服務測試（待測試）

### **Phase 2: Extension 整合 (次要)**
3. **Omniverse Extension**  
   - ⏳ `extension.toml`、`main.py`、`executor.py`
4. **端到端測試**  
   - ⏳ FastAPI ↔ Omniverse 通訊測試

### **Phase 3: 進階功能 (可選)**
5. **安全與穩定**  
   - ⏳ `error_handler.py` - 錯誤處理
   - ⏳ `server_config.py` - 安全設定
6. **效能優化**  
   - ⏳ `command_queue.py` - 非同步處理

---

## **📝 備註**
- 安全性機制需優先實作。
- 建議使用 Git 分支管理（如 `omniverse_exec_ai`）。
- 詳細設計請參考原始提案。

---

## **⚠️ 注意**
此文件由 GPT 提供開發思路與架構建議，實際開發時請根據專案當下需求與技術環境調整配置。 