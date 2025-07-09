from pyzerox import zerox
import os
import asyncio
import logging
import traceback

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def process_file(file_path, api_key, api_base, model):
    try:
        logger.debug(f"Starting to process file: {file_path}")

        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # 检查文件大小
        file_size = os.path.getsize(file_path)
        if file_size > 52428800:  # 50MB
            raise ValueError("File size exceeds limit")
        
        logger.debug(f"File size: {file_size} bytes")

        # 设置环境变量
        os.environ["OPENAI_API_KEY"] = api_key
        os.environ["OPENAI_API_BASE"] = api_base

        # 设置模型和其他参数
        output_dir = "./output"
        custom_system_prompt = None  # 可以根据需要设置
        select_pages = None  # 可以根据需要设置

        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        # 额外的参数
        kwargs = {
            "temperature": 0,  # 使用确定性输出
            "max_tokens": 16384,  # 确保有足够的输出空间
        }

        logger.debug(f"Calling zerox with model: {model}")
        result = await zerox(
            file_path=file_path,
            model=model,
            output_dir=output_dir,
            custom_system_prompt=custom_system_prompt,
            select_pages=select_pages,
            **kwargs
        )

        # 验证结果
        logger.debug(f"Zerox result: pages={len(result.pages)}, completion_time={result.completion_time}")
        for i, page in enumerate(result.pages):
            logger.debug(f"Page {i+1} content length: {len(page.content)}")

        return result

    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        logger.error(traceback.format_exc())
        raise

# 如果需要在非异步环境中调用
def process_file_sync(file_path, api_key, api_base, model):
    try:
        return asyncio.run(process_file(file_path, api_key, api_base, model))
    except Exception as e:
        logger.error(f"Error in process_file_sync: {str(e)}")
        logger.error(traceback.format_exc())
        raise
