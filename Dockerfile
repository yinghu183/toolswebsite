FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

# 更新 pip 并安装 requirements.txt 中的依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 显式安装 pypinyin（如果还没有在 requirements.txt 中）
RUN pip install --no-cache-dir pypinyin

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
