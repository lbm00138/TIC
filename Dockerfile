# 使用官方的 Python 基礎映象
FROM python:3.12-slim

# 設定容器內的工作目錄
WORKDIR /app

# 將當前主機目錄下的所有檔案 (包括 api.py) 複製到容器的 /app 目錄中
COPY . /app

# 安裝所有必要的 Python 依賴
# 請保持這行，因為您沒有使用 requirements.txt：
RUN pip install fastapi uvicorn

# 暴露應用程式將監聽的埠號
# Cloud Run 預設要求服務監聽 $PORT 環境變數指定的埠號，通常是 8080
ENV PORT 8080
EXPOSE ${PORT}

# 當容器啟動時運行您的 FastAPI 應用程式
# Cloud Run 會將流量路由到此埠
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8080"]