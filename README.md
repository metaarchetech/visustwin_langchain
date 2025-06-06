# Omniverse Exec AI

<div align="center">

![Platform Logo](https://img.shields.io/badge/Omniverse-Semantic%20Platform-76B900?style=for-the-badge&logo=nvidia)
![Version](https://img.shields.io/badge/version-1.0.0-green?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.10+-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-ff4b4b?style=for-the-badge&logo=streamlit)

**AI 驅動的 Omniverse 自然語言執行平台**

</div>

## 📋 項目概述

Omniverse Exec AI 是一個革命性的自然語言驅動平台，專門為 NVIDIA Omniverse 生態系統設計。該平台將先進的 AI 語言模型與 Omniverse 無縫整合，實現：

- 🤖 **AI 驅動的代碼生成**：自然語言轉換為 Omniverse Python 腳本
- 🧠 **智能語意查詢**：深度理解技術文檔和 API 規格
- 🎨 **專業界面設計**：NVIDIA 風格的暗色主題界面
- 🔒 **安全執行環境**：沙盒化代碼執行與安全檢查

> **注意**：本平台基於 LangServe 框架開發。原始 LangServe 功能說明請參閱 [README_LANGSERVE.md](README_LANGSERVE.md)

## ✨ 核心功能

### 🎯 語意查詢引擎
- **技術文檔分析**：深度理解 USD、RTX、Physics 等技術領域
- **最佳實踐建議**：基於企業級開發標準的專業建議
- **上下文相關回應**：根據項目需求提供客製化解決方案

### 🤖 AI 代碼生成器
- **自然語言處理**：將需求描述轉換為可執行的 Python 代碼
- **內建 API 知識庫**：包含完整的 Omniverse API 參考和範例
- **多種生成模式**：支援幾何建模、場景設置、動畫創建等各種操作
- **代碼品質保證**：自動添加錯誤處理、註釋和最佳實踐

### 🛡️ 安全執行框架
- **沙盒環境**：隔離代碼執行，防止系統安全風險
- **代碼審查**：自動檢測潛在危險操作
- **執行記錄**：完整追蹤代碼生成和執行歷史

## 🚀 快速開始

### 系統需求

- **作業系統**：Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- **Python**：3.10 或更新版本
- **記憶體**：建議 8GB 以上
- **網路**：需要網路連接以下載語言模型

### 安裝步驟

1. **克隆專案**
   ```bash
   git clone <repository-url>
   cd omniverse-semantic-platform
   ```

2. **安裝依賴**
   ```bash
   # 使用 Poetry (推薦)
   poetry install
   
   # 或使用 pip
   pip install -r requirements.txt
   ```

3. **配置 Groq API 金鑰**
   ```bash
   # Groq API 已預配置，如需更換請編輯 groq_config.py
   # 或設置環境變數
   export GROQ_API_KEY="your_groq_api_key_here"
   ```

4. **啟動平台**
   ```bash
   # 啟動 Streamlit 主界面（推薦）
   streamlit run streamlit_app.py
   
   # 或啟動 LangServe API 服務
   python -m langserve_launch_example.server
   ```

5. **開啟瀏覽器**
   
   - **Streamlit 界面**：訪問 `http://localhost:8501`（推薦）
   - **LangServe API**：訪問 `http://localhost:8001/playground/`

## 🎮 使用指南

### 語意查詢

1. 進入「語意查詢」標籤頁
2. 輸入技術問題或選擇預設範例
3. 點擊「提交查詢」獲得智能分析

**範例查詢：**
- "分析 USD 場景的核心架構組件與層級結構設計原則"
- "說明 RTX 渲染管線的核心參數配置與優化策略"

### 代碼生成

1. 切換到「代碼生成器」標籤頁
2. 描述您需要的 Omniverse 操作
3. 選擇生成選項（安全模式、註釋等）
4. 點擊「生成 Python 代碼」

**範例需求：**
- "創建一個有10個隨機位置立方體的場景，每個立方體都有不同的顏色材質"
- "為場景中的物件創建旋轉動畫，並設置關鍵幀"

### 執行與管理

- **立即執行**：在平台內安全執行生成的代碼
- **複製使用**：將代碼複製到 Omniverse Kit 中執行
- **歷史記錄**：在「執行記錄」標籤頁查看所有生成的代碼

## 🏗️ 項目架構

```
omniverse-semantic-platform/
├── streamlit_app.py              # Streamlit 主應用程式
├── omniverse_code_generator.py   # AI 代碼生成核心
├── streamlit_api.py              # FastAPI 後端服務
├── langserve_launch_example/     # LangChain 服務模組（原始 LangServe）
│   ├── chain.py                  # 語意查詢鏈（已客製化）
│   ├── server.py                 # LangServe 服務器
│   └── __init__.py               # 模組初始化
├── tests/                        # 測試檔案
├── docs/                         # 文檔目錄
├── README.md                     # 項目說明（Omniverse 平台）
├── README_LANGSERVE.md          # 原始 LangServe 說明
├── GIT_GUIDE.md                 # Git 管理指南
├── pyproject.toml               # 項目配置
├── poetry.lock                  # 依賴鎖定
└── requirements.txt             # 相容性依賴列表
```

### 多界面架構

本平台提供兩種使用界面：

1. **Streamlit 界面** (主要推薦)
   - 完整的三標籤頁界面
   - NVIDIA 風格設計
   - 代碼生成和執行功能
   - 訪問：`http://localhost:8501`

2. **LangServe API 界面** (開發者使用)
   - RESTful API 端點
   - 自動生成的文檔
   - Playground 互動測試
   - 訪問：`http://localhost:8001`

## 🔧 環境配置

### 開發模式

```bash
# 啟動 Streamlit 開發服務器
streamlit run streamlit_app.py --server.runOnSave true

# 啟動 LangServe API 後端
python -m langserve_launch_example.server

# 啟動 FastAPI 後端 (可選)
python streamlit_api.py
```

### 生產環境

```bash
# 使用 Docker 部署
docker compose up -d

# 或使用 Poetry
poetry run streamlit run streamlit_app.py --server.port 8501
```

## 🧪 測試

```bash
# 運行單元測試
poetry run pytest tests/

# 運行特定測試
poetry run pytest tests/test_code_generator.py -v

# 生成測試報告
poetry run pytest --cov=. --cov-report=html
```

## 🔗 Omniverse 整合

### 模擬模式
- 在沒有安裝 Omniverse 的環境中運行
- 生成代碼可複製到真實環境執行
- 完整的界面和功能體驗

### 完整模式
- 需要安裝 Omniverse Kit 或相關 USD 套件
- 支援直接執行生成的代碼
- 實時場景操作和反饋

## 📚 API 參考

### 語意查詢 API

```python
from langserve_launch_example.chain import get_chain

chain = get_chain()
response = chain.invoke({"topic": "您的技術問題"})
```

### 代碼生成 API

```python
from omniverse_code_generator import omniverse_code_gen

result = omniverse_code_gen.generate_code("創建一個立方體")
if result["status"] == "success":
    print(result["code"])
```

### LangServe REST API

```python
import requests

# 調用語意查詢
response = requests.post(
    "http://localhost:8001/invoke",
    json={"input": {"topic": "USD 場景架構分析"}}
)
```

詳細 API 文檔請參閱：
- **Streamlit API**：內建於界面中
- **LangServe API**：`http://localhost:8001/docs`

## 🤝 參與貢獻

我們歡迎社群貢獻！請閱讀 [CONTRIBUTING.md](docs/CONTRIBUTING.md) 了解詳細流程。

### 開發流程

1. Fork 此專案
2. 創建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

## 📄 授權條款

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

## 🙏 致謝

- [NVIDIA Omniverse](https://www.nvidia.com/omniverse/) - 提供強大的 3D 協作平台
- [LangChain](https://langchain.com/) - 強大的語言模型應用框架
- [Groq](https://groq.ai/) - 本地語言模型推理引擎
- [Streamlit](https://streamlit.io/) - 優秀的 Python Web 應用框架

## 📞 聯絡資訊

- **專案維護者**：Omniverse Development Team
- **電子郵件**：support@omniverse-semantic.dev
- **問題回報**：[GitHub Issues](https://github.com/your-org/omniverse-semantic-platform/issues)
- **文檔**：[Wiki](https://github.com/your-org/omniverse-semantic-platform/wiki)

---

<div align="center">

**讓 AI 協助您更高效地開發 Omniverse 應用程序**

[![GitHub stars](https://img.shields.io/github/stars/your-org/omniverse-semantic-platform?style=social)](https://github.com/your-org/omniverse-semantic-platform)
[![Twitter Follow](https://img.shields.io/twitter/follow/OmniverseDev?style=social)](https://twitter.com/OmniverseDev)

</div>
