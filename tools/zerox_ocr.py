from pyzerox import zerox
import os
import asyncio
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def process_file(file_path):
    try:
        logger.debug(f"Starting to process file: {file_path}")

        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # 检查文件大小
        if os.path.getsize(file_path) > 52428800:  # 50MB
            raise ValueError("File size exceeds limit")

        # 设置环境变量
        os.environ["OPENAI_API_KEY"] = "sk-2jIu4cwmA58sWUeM170bC42a2bAd433dA84296Be9fC025E3"
        os.environ["OPENAI_API_BASE"] = "https://burn.hair/v1"

        # 设置模型和其他参数
        model = "gpt-4o-mini"  # 或者您选择的其他模型
        output_dir = "./output"
        custom_system_prompt = None  # 可以根据需要设置
        select_pages = None  # 可以根据需要设置

        # 额外的参数
        kwargs = {}

        result = await zerox(
            file_path=file_path,
            model=model,
            output_dir=output_dir,
            custom_system_prompt=custom_system_prompt,
            select_pages=select_pages,
            **kwargs
        )

        logger.debug(f"Zerox result: {result}")
        return result

    except Exception as e:
        logger.error(f"Error processing file: {str(e)}", exc_info=True)
        raise

# 如果需要在非异步环境中调用
def process_file_sync(file_path):
    return asyncio.run(process_file(file_path))
