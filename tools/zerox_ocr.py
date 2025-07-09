from pyzerox import zerox
import os
import asyncio
import logging
import traceback
import uuid

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
        # 确保输出目录存在并有正确的权限
        output_dir = os.path.join(os.getcwd(), 'output')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, mode=0o777)
        else:
            os.chmod(output_dir, 0o777)

        # 处理文件
        result = asyncio.run(process_file(file_path, api_key, api_base, model))
        
        # 生成唯一的输出文件名
        output_filename = f"{str(uuid.uuid4()).replace('-', '_')}_{os.path.splitext(os.path.basename(file_path))[0]}.md"
        output_path = os.path.join(output_dir, output_filename)
        
        # 写入结果并设置正确的权限
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# OCR 结果\n\n")
            f.write(f"文件名: {os.path.basename(file_path)}\n")
            f.write(f"处理时间: {result.completion_time/1000:.2f} 秒\n")
            f.write(f"输入 tokens: {result.input_tokens}\n")
            f.write(f"输出 tokens: {result.output_tokens}\n\n")
            
            for page in result.pages:
                f.write(f"## 第 {page.page} 页\n\n")
                f.write(page.content + "\n\n")
        
        # 设置文件权限
        os.chmod(output_path, 0o666)
        
        return result
        
    except Exception as e:
        logging.error(f"处理文件时出错: {str(e)}")
        logging.error(traceback.format_exc())
        raise
