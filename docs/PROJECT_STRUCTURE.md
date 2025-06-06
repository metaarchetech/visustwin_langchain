# 專案結構說明

## 📁 目錄結構

```
visustwin_langchain/
├── src/                          # 源代碼目錄
│   ├── api/                      # API 相關模組
│   │   ├── __init__.py
│   │   ├── api_models.py         # Pydantic 數據模型
│   │   ├── fastapi_server.py     # FastAPI 主服務器
│   │   └── streamlit_api.py      # Streamlit API 介面
│   ├── config/                   # 配置模組
│   │   ├── __init__.py
│   │   └── groq_config.py        # AI 引擎配置
│   ├── generators/               # 代碼生成器模組
│   │   ├── __init__.py
│   │   └── omniverse_code_generator.py  # Omniverse 代碼生成器
│   ├── ui/                       # 用戶界面模組
│   │   ├── __init__.py
│   │   └── streamlit_app.py      # Streamlit 主應用
│   └── __init__.py
├── docs/                         # 文檔目錄
│   ├── extension_lang_api_dev.md # API 開發指南
│   ├── GIT_GUIDE.md             # Git 使用指南
│   ├── OMNIVERSE_EXEC_AI_README.md  # Omniverse 執行 AI 說明
│   ├── README_LANGSERVE.md      # LangServe 說明
│   └── PROJECT_STRUCTURE.md     # 本文件
├── scripts/                      # 腳本目錄
│   └── start_omniverse_exec_ai.bat  # 啟動腳本
├── docker/                       # Docker 配置
│   ├── docker-compose.yml
│   └── Dockerfile
├── tests/                        # 測試目錄
├── langserve_launch_example/     # LangServe 範例
├── .vscode/                      # VS Code 配置
├── .github/                      # GitHub 配置
├── requirements.txt              # 完整依賴清單
├── requirements_simple.txt       # 簡化依賴清單
├── pyproject.toml               # Python 專案配置
├── poetry.lock                  # Poetry 鎖定文件
├── poetry.toml                  # Poetry 配置
├── Makefile                     # 構建腳本
├── LICENSE                      # 授權文件
├── README.md                    # 主要說明文件
└── .gitignore                   # Git 忽略文件
```

## 🚀 啟動方式

### 方法 1：使用啟動腳本（推薦）
```bash
# 在專案根目錄執行
scripts\start_omniverse_exec_ai.bat
```

### 方法 2：手動啟動
```bash
# 1. 啟動 FastAPI 後端
python -m src.api.fastapi_server

# 2. 啟動 Streamlit 前端（新命令行視窗）
streamlit run src\ui\streamlit_app.py
```

## 📦 模組說明

### API 模組 (`src/api/`)
- **api_models.py**: 定義 API 請求/回應的 Pydantic 模型
- **fastapi_server.py**: 核心 FastAPI 服務器，處理代碼執行請求
- **streamlit_api.py**: 為 Streamlit 提供 API 介面

### 配置模組 (`src/config/`)
- **groq_config.py**: 統一的 AI 引擎配置管理

### 生成器模組 (`src/generators/`)
- **omniverse_code_generator.py**: Omniverse 代碼生成核心邏輯

### UI 模組 (`src/ui/`)
- **streamlit_app.py**: 主要的 Streamlit 用戶界面

## 🔧 開發注意事項

1. **導入路徑**: 使用相對導入 (如 `from ..config.groq_config import ...`)
2. **模組化**: 每個功能區塊都有獨立的 `__init__.py` 文件
3. **配置管理**: 所有配置集中在 `src/config/` 目錄
4. **文檔**: 開發相關文檔統一放在 `docs/` 目錄

## 📝 更新記錄

- **2024-01**: 重新組織專案結構，提高代碼可維護性
- 將原本根目錄的散亂文件按功能分類到對應目錄
- 更新所有導入路徑以適應新結構
- 修改啟動腳本以支援新的文件位置 