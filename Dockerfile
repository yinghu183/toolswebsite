# ==============================================================================
# Dockerfile for the Flask Toolbox App (Final Version)
# ==============================================================================

# 基础镜像保持不变
FROM python:3.12-slim-bookworm

# 设置一个环境变量，防止在安装系统包时出现交互式弹窗
ENV DEBIAN_FRONTEND=noninteractive

# 设置容器内的工作目录
WORKDIR /app

# --- START MODIFICATION ---
# 核心步骤：安装所有必需的系统级依赖
# 增加了字体相关的包，以确保 Office 文档能被正确渲染
# - ttf-mscorefonts-installer: 包含 Times New Roman, Arial 等微软核心字体
# - fonts-wqy-zenhei: 包含文泉驿正黑，一个高质量的开源中文字体
# - fonts-noto-cjk: Google Noto 字体，覆盖中日韩字符
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libreoffice \
    poppler-utils \
    graphicsmagick \
    ttf-mscorefonts-installer \
    fonts-wqy-zenhei \
    fonts-noto-cjk \
    && echo "ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true" | debconf-set-selections \
    && apt-get install -y --no-install-recommends ttf-mscorefonts-installer \
    && rm -rf /var/lib/apt/lists/*
# --- END MODIFICATION ---

# 将 Python 依赖定义文件复制到工作目录
COPY ./requirements.txt /app/requirements.txt

# 安装所有 Python 依赖
RUN pip install --no-cache-dir -r /app/requirements.txt

# 将项目中的所有其他文件（app.py, templates/, static/ 等）复制到工作目录
COPY . /app/

# 声明服务将要监听的端口
EXPOSE 8000

# 定义容器启动时要执行的默认命令
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:8000", "app:app"]