from pyzerox import zerox
import os
import asyncio
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def process_file(file_path):
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # 检查文件大小
        if os.path.getsize(file_path) > 52428800:  # 50MB
            raise ValueError("File size exceeds limit")

        # 设置环境变量
        os.environ["OPENAI_API_KEY"] = "sk-2jIu4cwmA58sWUeM170bC42a2bAd433dA84296Be9fC025E3"
        os.environ["OPENAI_API_BASE"] = "https://burn.hair/v1"

        async def run_zerox():
            try:
                result = await zerox(
                    file_path=file_path,
                    model="gpt-4o-mini",
                    output_dir="./output"
                )
                if result is None:
                    raise ValueError("Zerox returned None result")
                return result
            except Exception as e:
                logger.error(f"Error in zerox: {str(e)}")
                raise

        return asyncio.run(run_zerox())
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise
