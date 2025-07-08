# 使用一个稳定且包含常用工具的官方镜像作为基础
# Debian "Bookworm" 是一个很好的选择，因为它有较新的软件包
FROM python:3.10-slim-bookworm

# 声明维护者信息（可选）
LABEL maintainer="yinghu183@163.com"

# 设置一个环境变量，防止安装过程中出现交互式提示
ENV DEBIAN_FRONTEND=noninteractive

# 设置工作目录，后续所有操作都在此目录下进行
WORKDIR /app

# 核心步骤：更新软件包列表并一次性安装所有系统级依赖
# --no-install-recommends 参数可以显著减小最终镜像的体积
# 1. libreoffice: 用于将 Office 文档 (docx, xlsx, pptx) 无头转换为 PDF
# 2. poppler-utils: 包含 pdftoppm 工具，用于将 PDF 转换为图片
# 3. graphicsmagick: 一个强大的图像处理工具，Zerox 可能用它来优化图片
# 最后清理 apt 缓存，进一步减小镜像大小
RUN apt-get update && apt-get install -y --no-install-recommends \
    libreoffice \
    poppler-utils \
    graphicsmagick \
    && rm -rf /var/lib/apt/lists/*

# 将 Python 依赖定义文件复制到工作目录
COPY ./requirements.txt /app/requirements.txt

# 使用 pip 安装 Python 依赖
# --no-cache-dir 选项可以减少镜像层的大小
RUN pip install --no-cache-dir -r /app/requirements.txt

# 将项目中的所有其他文件复制到工作目录
COPY . /app/

# 声明服务将要监听的端口（仅为文档目的，实际端口映射在 docker-compose.yml 中定义）
EXPOSE 8000

# 定义容器启动时要执行的命令
# 请根据您的实际情况修改此行。这里以 gunicorn 为例，它是生产环境常用的 WSGI 服务器。
# 如果您在开发环境中直接运行 `flask run`，请相应调整。
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:8000", "app:app"]