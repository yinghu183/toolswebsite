from pyzerox import zerox
# --- START MODIFICATION ---
# 1. 导入我们要修改的类
from pyzerox.models.modellitellm import litellmmodel
# --- END MODIFICATION ---
import os
import asyncio
import logging
import traceback
import uuid

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def process_file(file_path, api_key, api_base, model):
    
    # --- START MODIFICATION ---
    # 2. 定义一个什么都不做的“傀儡”验证函数
    def do_nothing(self):
        logger.debug("Skipping the original validate_model() check.")
        pass

    # 3. 保存原始的验证函数
    original_validate_model = litellmmodel.validate_model
    # 4. 用我们的“傀儡”替换掉原始的验证函数
    litellmmodel.validate_model = do_nothing
    # --- END MODIFICATION ---

    try:
        logger.debug(f"Starting to process file: {file_path}")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_size = os.path.getsize(file_path)
        if file_size > 52428800:  # 50MB
            raise ValueError("File size exceeds limit")
        
        logger.debug(f"File size: {file_size} bytes")

        os.environ["OPENAI_API_KEY"] = api_key
        os.environ["OPENAI_API_BASE"] = api_base
        
        os.environ["VERTEXAI_PROJECT"] = "dummy-project"
        os.environ["VERTEXAI_LOCATION"] = "dummy-location"

        output_dir = "./output"
        custom_system_prompt = None
        select_pages = None

        os.makedirs(output_dir, exist_ok=True)

        kwargs = {
            "temperature": 0,
            "max_tokens": 16384,
        }

        logger.debug(f"Calling zerox with model: {model}")
        
        # 5. 现在这个调用将不会再执行那个烦人的验证了
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
        # --- START MODIFICATION ---
        # 6. 无论成功还是失败，最后都把原始的验证函数恢复回去
        # 这是一个好习惯，可以防止对程序的其他部分产生意想不到的影响
        litellmmodel.validate_model = original_validate_model
        logger.debug("Restored the original validate_model().")
        # --- END MODIFICATION ---

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