from pyzerox import zerox
from pyzerox.models.modellitellm import litellmmodel
import os
import asyncio
import logging
import traceback
import uuid

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def process_file(file_path, api_key, api_base, model):
    
    # 猴子补丁仍然需要保留，以跳过模型列表的检查
    def do_nothing(self):
        logger.debug("Skipping the original validate_model() check via monkey patch.")
        pass

    original_validate_model = litellmmodel.validate_model
    litellmmodel.validate_model = do_nothing
    
    try:
        logger.debug(f"Starting to process file: {file_path}")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_size = os.path.getsize(file_path)
        if file_size > 52428800:
            raise ValueError("File size exceeds limit")
        
        logger.debug(f"File size: {file_size} bytes")

        # 环境变量方式作为备用，但直接传参是关键
        os.environ["OPENAI_API_KEY"] = api_key
        os.environ["OPENAI_API_BASE"] = api_base
        os.environ["VERTEXAI_PROJECT"] = "dummy-project"
        os.environ["VERTEXAI_LOCATION"] = "dummy-location"

        output_dir = "./output"
        custom_system_prompt = None
        select_pages = None
        os.makedirs(output_dir, exist_ok=True)

        # 准备传递给zerox的参数
        kwargs = {
            "temperature": 0,
            "max_tokens": 16384,
            # --- START FINAL MODIFICATION ---
            # 釜底抽薪：将api_key和api_base作为直接参数传递
            # 这会强制LiteLLM在所有API请求（包括内部的validate_access测试）中
            # 都使用您自己的聚合服务地址和密钥，而不是OpenAI官方地址。
            "api_key": api_key,
            "api_base": api_base
            # --- END FINAL MODIFICATION ---
        }

        logger.debug(f"Calling zerox with model: {model} and direct api_base/api_key.")
        
        result = await zerox(
            file_path=file_path,
            model=model,
            output_dir=output_dir,
            custom_system_prompt=custom_system_prompt,
            select_pages=select_pages,
            **kwargs
        )
        
        logger.debug(f"Zerox result: pages={len(result.pages)}, completion_time={result.completion_time}")
        for i, page in enumerate(result.pages):
            logger.debug(f"Page {i+1} content length: {len(page.content)}")

        return result

    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        logger.error(traceback.format_exc())
        raise
    finally:
        # 恢复原始的验证函数
        litellmmodel.validate_model = original_validate_model
        logger.debug("Restored the original validate_model().")


# process_file_sync 函数保持不变
def process_file_sync(file_path, api_key, api_base, model, output_path):
    try:
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)

        result = asyncio.run(process_file(file_path, api_key, api_base, model))
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# OCR 结果\n\n")
            f.write(f"文件名: {os.path.basename(file_path)}\n")
            f.write(f"处理时间: {result.completion_time/1000:.2f} 秒\n")
            f.write(f"输入 tokens: {result.input_tokens}\n")
            f.write(f"输出 tokens: {result.output_tokens}\n\n")
            
            for page in result.pages:
                f.write(f"## 第 {page.page} 页\n\n")
                f.write(page.content + "\n\n")
        
        return {'filename': os.path.basename(output_path), 'result': result}
        
    except Exception as e:
        logging.error(f"处理文件时出错: {str(e)}")
        logging.error(traceback.format_exc())
        raise