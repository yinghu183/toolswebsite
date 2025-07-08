# ==============================================================================
# Dockerfile for the Flask Toolbox App
# ==============================================================================

# 修正：将基础镜像从 python:3.10 升级到 python:3.12，以满足 py-zerox 的依赖要求
FROM python:3.12-slim-bookworm

# 设置一个环境变量，防止在安装系统包时出现交互式弹窗
ENV DEBIAN_FRONTEND=noninteractive

# 设置容器内的工作目录
WORKDIR /app

# 核心步骤：安装所有必需的系统级依赖，以支持多种文件格式的转换
# - libreoffice: 用于将 Office 文档 (docx, xlsx, pptx) 无头模式转换为 PDF
# - poppler-utils: 包含 pdftoppm 等工具，用于将 PDF 转换为图片
# - graphicsmagick: 强大的图像处理库，用于优化图片
# 使用 --no-install-recommends 减少不必要的包，清理 apt 缓存以减小镜像体积
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice \
    poppler-utils \
    graphicsmagick \
    && rm -rf /var/lib/apt/lists/*

# 将 Python 依赖定义文件复制到工作目录
COPY ./requirements.txt /app/requirements.txt

# 安装所有 Python 依赖
# --no-cache-dir 选项可以减小镜像层的大小
# 因为 Python 版本已升级，此步骤现在可以成功安装 py-zerox
RUN pip install --no-cache-dir -r /app/requirements.txt

# 将项目中的所有其他文件（app.py, templates/, static/ 等）复制到工作目录
COPY . /app/

# 声明服务将要监听的端口（这主要用于文档目的）
EXPOSE 8000

# 定义容器启动时要执行的默认命令（生产环境推荐使用 Gunicorn）
# 你可以根据实际情况修改此命令
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:8000", "app:app"]