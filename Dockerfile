FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# 更新 pip 并安装 requirements.txt 中的依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir py-zerox && \
    pip install --no-cache-dir --upgrade litellm

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
