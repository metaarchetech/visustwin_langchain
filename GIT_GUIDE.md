# Git 管理指南

## 🚀 首次推送到 Git

### 1. 檢查當前狀態
```bash
git status
```

### 2. 添加所有新檔案
```bash
# 添加所有檔案（排除 .gitignore 中的項目）
git add .

# 或者選擇性添加核心檔案
git add streamlit_app.py
git add omniverse_code_generator.py
git add streamlit_api.py
git add README.md                    # Omniverse 平台主說明
git add README_LANGSERVE.md          # 原始 LangServe 說明
git add GIT_GUIDE.md                 # Git 管理指南
git add requirements.txt
git add pyproject.toml
```

### 3. 提交更改
```bash
git commit -m "feat: 完成 Omniverse 語意整合平台核心功能

- 新增 AI 驅動的代碼生成器
- 實作 Streamlit 專業界面（NVIDIA 風格）
- 整合 Ollama 本地語言模型
- 支援語意查詢和技術分析
- 新增安全執行環境和代碼審查
- 分離新舊 README 文檔結構
- 完善項目文檔和部署指南"
```

### 4. 設定遠端倉庫（如果還沒有）
```bash
# 添加 GitHub 遠端倉庫
git remote add origin https://github.com/your-username/omniverse-semantic-platform.git

# 檢查遠端設定
git remote -v
```

### 5. 推送到遠端倉庫
```bash
# 首次推送
git push -u origin main

# 或者如果主分支是 master
git push -u origin master
```

## 📁 建議的分支策略

### 主要分支
- `main/master` - 穩定版本
- `develop` - 開發版本

### 功能分支
- `feature/code-generator` - 代碼生成功能
- `feature/ui-improvements` - 界面改進
- `feature/omniverse-integration` - Omniverse 整合
- `feature/langserve-updates` - LangServe 原始功能更新

### 範例工作流程
```bash
# 創建功能分支
git checkout -b feature/new-feature

# 開發完成後合併回 develop
git checkout develop
git merge feature/new-feature

# 準備發布時合併到 main
git checkout main
git merge develop
git tag v1.0.0
```

## 🔍 檢查要推送的檔案

### 確認哪些檔案會被推送
```bash
git ls-files
```

### 檢查 .gitignore 是否正確
```bash
# 檢查被忽略的檔案
git status --ignored

# 測試特定檔案是否被忽略
git check-ignore OllamaSetup.exe
```

## 📋 提交訊息規範

### 格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

### 類型（Type）
- `feat`: 新功能
- `fix`: 錯誤修復
- `docs`: 文檔更新
- `style`: 代碼格式（不影響功能）
- `refactor`: 重構代碼
- `test`: 測試相關
- `chore`: 雜項任務

### 範例
```bash
git commit -m "feat(ui): 新增 NVIDIA 風格的深色主題

- 實作黑底綠色調配色方案
- 添加懸停動畫效果
- 優化按鈕和輸入框樣式
- 調整圓角半徑為 6px"

git commit -m "docs: 分離 README 結構

- 創建 README_LANGSERVE.md 說明原始功能
- 更新主 README.md 專注於 Omniverse 平台
- 添加多界面架構說明
- 優化文檔導航和參考連結"
```

## 🛡️ 推送前檢查清單

- [ ] 確認 .gitignore 設定正確
- [ ] 移除敏感資訊（API 金鑰、密碼等）
- [ ] 測試應用程式是否正常運行
- [ ] 檢查 README.md 內容是否完整
- [ ] 檢查 README_LANGSERVE.md 是否準確
- [ ] 確認所有依賴都在 requirements.txt 中
- [ ] 移除臨時檔案和調試代碼
- [ ] 測試兩種界面（Streamlit + LangServe）是否正常

## 📚 文檔管理策略

### 主要文檔
- `README.md` - Omniverse 語意整合平台（主要項目）
- `README_LANGSERVE.md` - 原始 LangServe 功能
- `GIT_GUIDE.md` - Git 工作流程指南

### 文檔更新規範
- 新功能必須同步更新相關文檔
- API 變更需要更新 README_LANGSERVE.md
- 界面變更需要更新主 README.md
- 重大變更需要更新兩份文檔的交叉引用

## 🔄 日常開發工作流程

```bash
# 1. 同步最新代碼
git pull origin main

# 2. 創建功能分支
git checkout -b feature/your-feature

# 3. 開發過程中的提交
git add .
git commit -m "feat: 實作某功能"

# 4. 推送功能分支
git push origin feature/your-feature

# 5. 在 GitHub 上創建 Pull Request

# 6. 合併後清理
git checkout main
git pull origin main
git branch -d feature/your-feature
```

## 🚨 緊急修復流程

```bash
# 1. 從 main 創建熱修復分支
git checkout main
git checkout -b hotfix/critical-bug

# 2. 修復並測試
# ... 修復代碼 ...

# 3. 提交修復
git commit -m "fix: 緊急修復關鍵錯誤"

# 4. 合併到 main 和 develop
git checkout main
git merge hotfix/critical-bug
git checkout develop
git merge hotfix/critical-bug

# 5. 清理
git branch -d hotfix/critical-bug
```

## 🏷️ 發布標籤管理

```bash
# 創建發布標籤
git tag -a v1.0.0 -m "發布 Omniverse 語意整合平台 v1.0.0

主要功能:
- AI 代碼生成器
- 語意查詢引擎  
- NVIDIA 風格界面
- 雙界面架構支援"

# 推送標籤
git push origin v1.0.0

# 查看所有標籤
git tag -l
``` 