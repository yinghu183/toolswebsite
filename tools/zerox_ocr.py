from pyzerox import zerox
import os
import asyncio
import logging

logging.basicConfig(level=logging.DEBUG)

def process_file(file_path):
    # 设置环境变量（请确保在生产环境中安全地管理这些密钥和 URL）
    os.environ["OPENAI_API_KEY"] = "sk-FccRgIDYhi5ObIfF40D63dD5A8Ad4e20A549F63973681e69"
    os.environ["OPENAI_API_BASE"] = "https://api.141010.xyz/v1"  # 设置自定义的 base URL
    
    output_dir = "./output"
    os.makedirs(output_dir, exist_ok=True)
    
    async def run_zerox():
        try:
            logging.debug(f"Processing file: {file_path}")
            result = await zerox(
                file_path=file_path,
                model="gpt-4o-mini",
                output_dir=output_dir
            )
            logging.debug(f"Zerox result: {result}")
            return result
        except Exception as e:
            logging.error(f"Error in zerox: {str(e)}")
            return None

    return asyncio.run(run_zerox())
