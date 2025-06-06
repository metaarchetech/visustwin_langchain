# LangServe Launch Example (原始項目)

<!--- This is a LangChain project bootstrapped by [LangChain CLI](https://github.com/langchain-ai/langchain). --->

這是原始的 LangServe 範例項目，作為 Omniverse 語意整合平台的基礎框架。

## 🏗️ 項目結構

```
langserve_launch_example/
├── chain.py                      # AI 語意查詢鏈（已客製化為 Omniverse 專用）
├── server.py                     # FastAPI 服務器
└── __init__.py                   # 模組初始化
```

## ⚙️ 自定義修改

原始的 LangServe 範例已被客製化以支援 Omniverse 語意整合：

### `chain.py` 的修改
- **原始功能**：OpenAI 驅動的一般性對話
- **現在功能**：Groq 驅動的 Omniverse 專業技術查詢
- **語言模型**：從 OpenAI 改為 Groq (llama3-8b-8192 + llama3-70b-8192)
- **提示模板**：專門為 Omniverse 技術領域設計
- **查詢範圍**：支援 USD、RTX、Physics、Extensions、Connectors 等
- **技術深度**：提供企業級技術架構分析與實作建議
- **回應速度**：優化的提示模板確保專業且準確的技術回應

### `server.py` 的修改  
- **原始功能**：基本的 FastAPI 服務
- **現在功能**：支援 NVIDIA 風格的專業界面
- **路由設置**：保持與 LangServe Playground 的相容性

## 📚 原始安裝和使用方式

### 安裝依賴

使用 Poetry：
```bash
poetry install
```

使用 pip：
```bash
pip install .
```

### 使用方式

**注意**：原始版本需要 OpenAI API 金鑰，現在版本使用 Groq 不需要。

設置 OpenAI API 金鑰（原始版本）：
```bash
export OPENAI_API_KEY="sk-..."
```

啟動 LangServe 服務：
```bash
make start
# 或
python -m langserve_launch_example.server
```

這會在 port 8001 啟動 web 服務器。

### 使用 Docker

```bash
docker compose up
```

## 🚀 部署

### 建立 Docker 映像

```bash
docker build . -t langserve_launch_example:latest
```

### 運行映像

```bash
docker run -p 8001:8001 -e PORT=8001 langserve_launch_example:latest
```

### 部署到 GCP

創建 `.env.gcp.yaml` 檔案並填入相關資訊，然後執行：

```bash
make deploy_gcp
```

## 🔗 與 Omniverse 平台的關係

這個 LangServe 服務現在作為 Omniverse 語意整合平台的核心引擎：

- **API 端點**：`http://localhost:8001` - 提供 RESTful API
- **Playground**：`http://localhost:8001/playground/` - 互動式測試界面  
- **API 文檔**：`http://localhost:8001/docs` - 自動生成的 API 文檔

## 🎯 LangServe 功能

### 可用端點

- `GET /` - 服務資訊
- `POST /invoke` - 直接調用 AI 鏈
- `POST /batch` - 批量處理請求
- `POST /stream` - 串流回應
- `GET /playground/` - 互動式界面
- `GET /docs` - API 文檔

### 範例 API 調用

```python
import requests

# 直接調用 AI 鏈
response = requests.post(
    "http://localhost:8001/invoke",
    json={"input": {"topic": "USD 場景架構分析"}}
)

result = response.json()
print(result["output"])
```

## 📝 原始 LangChain CLI 指令

這個項目是使用以下指令創建的：

```bash
langchain app new my-app --package simple-chain
```

## 🤝 貢獻

關於如何設置開發環境和貢獻的資訊，請參閱 [CONTRIBUTING.md](.github/CONTRIBUTING.md)。

---

**注意**：這是原始 LangServe 範例的說明。如需 Omniverse 語意整合平台的完整功能，請參閱主要的 [README.md](README.md)。 