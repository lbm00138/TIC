# 使用官方 Python 3.12 的 slim-buster 基礎映像
FROM python:3.12-slim

# 設定工作目錄為 /app
WORKDIR /app

# 將 requirements.txt 複製到容器中
# 這樣做可以在安裝依賴時利用 Docker 的緩存機制
COPY requirements.txt .

# 安裝所有 Python 依賴
# --no-cache-dir 避免在容器中創建額外的緩存，減小映像大小
RUN pip install --no-cache-dir -r requirements.txt

# 將您的 FastAPI 應用程式碼和前端 HTML 檔案複製到容器中
# 假設 api.py 和 test1.html 在 Dockerfile 的同一層目錄
COPY api.py .
COPY test1.html . # <-- 確保這個檔案與 Dockerfile 在同一層級

# 如果您還有其他靜態檔案 (例如 CSS 或 JS 檔案，並且在 test1.html 中有引用)
# 並且這些檔案在一個名為 'static' 的資料夾中，您需要將其複製進來
# 例如：COPY static/ ./static/

# 定義應用程式運行的端口
# Cloud Run 服務會監聽這個端口
ENV PORT 8080

# 運行 Gunicorn 伺服器來啟動 FastAPI 應用
# api:app 表示運行 api.py 中的 app 實例
# --workers 1 表示使用一個 worker 進程 (對於簡單應用足夠)
# --bind 0.0.0.0:${PORT} 綁定到所有網路接口和指定的端口
# --worker-class uvicorn.workers.UvicornWorker 使用 Uvicorn worker 類別，因為 FastAPI 依賴 Uvicorn
CMD ["gunicorn", "api:app", "--workers", "1", "--bind", "0.0.0.0:8080", "--worker-class", "uvicorn.workers.UvicornWorker"]