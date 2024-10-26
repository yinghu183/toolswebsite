from pyzerox import zerox
import os
import asyncio

def process_file(file_path):
    # 设置环境变量（请确保在生产环境中安全地管理这些密钥和 URL）
    os.environ["OPENAI_API_KEY"] = "sk-FccRgIDYhi5ObIfF40D63dD5A8Ad4e20A549F63973681e69"
    os.environ["OPENAI_API_BASE"] = "https://api.141010.xyz/v1"  # 设置自定义的 base URL
    
    async def run_zerox():
        result = await zerox(
            file_path=file_path,
            model="gpt-4o-mini",
            output_dir="./output"
        )
        return result

    return asyncio.run(run_zerox())
