/**
 * Zerox OCR 前端交互脚本
 * 功能：处理表单提交、显示加载状态、解析后端响应（成功或失败）、渲染结果并提供下载功能。
 */
 document.addEventListener('DOMContentLoaded', function() {
    // 1. 获取所有需要操作的 HTML 元素
    const form = document.getElementById('ocrForm');
    const resultDiv = document.getElementById('result');
    const loadingDiv = document.getElementById('loading');
    const markdownContent = document.getElementById('markdown-content');
    const downloadBtn = document.getElementById('download-btn');
    
    // 2. 声明一个变量，用于存储从后端获取的完整 Markdown 文本
    let fullMarkdown = '';

    // 3. 监听表单的提交事件
    form.addEventListener('submit', function(event) {
        event.preventDefault(); // 阻止表单的默认GET/POST跳转行为

        const formData = new FormData(form);
        const fileInput = document.getElementById('document');

        // 客户端基础验证：确保用户已选择文件
        if (!fileInput.files || fileInput.files.length === 0) {
            resultDiv.style.display = 'block';
            markdownContent.innerHTML = `<div class="error">请先选择一个文件再提交。</div>`;
            return;
        }

        // 4. 更新UI：显示加载动画，隐藏旧的结果
        loadingDiv.style.display = 'block';
        resultDiv.style.display = 'none';
        markdownContent.textContent = '';
        downloadBtn.style.display = 'none';

        // 5. 使用 Fetch API 发送异步请求到后端
        fetch('/zerox_ocr/process', {
            method: 'POST',
            body: formData, // FormData 会自动处理文件上传的编码
        })
        .then(response => {
            // 6. 核心处理：检查HTTP响应状态码
            // 如果状态码不是 2xx (e.g., 400, 500)，说明是后端预知的错误
            if (!response.ok) {
                // 尝试解析响应体中的JSON错误信息，并将其抛出到.catch块
                return response.json().then(errorData => {
                    throw new Error(errorData.error || '服务器返回了一个未知错误。');
                });
            }
            // 如果状态码是 2xx，说明请求成功，正常解析JSON数据
            return response.json();
        })
        .then(data => {
            // 7. 处理成功获取的数据
            loadingDiv.style.display = 'none';
            resultDiv.style.display = 'block';

            // 确认返回的数据中包含我们需要的 markdown 字段
            if (data.markdown) {
                fullMarkdown = data.markdown; // 保存结果用于下载

                // 使用 marked.js 库将 Markdown 字符串渲染为漂亮的 HTML
                // (如果HTML中没有引入marked.js, 会优雅地降级)
                if (window.marked) {
                    markdownContent.innerHTML = marked.parse(fullMarkdown);
                } else {
                    // 如果没有 marked.js, 直接以纯文本形式显示
                    markdownContent.textContent = fullMarkdown;
                }
                downloadBtn.style.display = 'inline-block'; // 显示下载按钮
            } else {
                // 处理服务器返回200但数据格式不符的情况
                throw new Error('服务器响应成功，但返回的数据格式不正确。');
            }
        })
        .catch(error => {
            // 8. 统一的错误处理中心
            // 无论是网络问题、服务器错误还是数据解析错误，都会在这里被捕获
            console.error('OCR 处理过程中发生错误:', error);
            loadingDiv.style.display = 'none';
            resultDiv.style.display = 'block';
            // 将错误信息清晰地展示给用户
            markdownContent.innerHTML = `<div class="error"><strong>处理失败:</strong><br>${error.message}</div>`;
            downloadBtn.style.display = 'none';
        });
    });

    // 9. 为下载按钮绑定点击事件
    downloadBtn.addEventListener('click', function() {
        if (fullMarkdown) {
            // 创建一个包含 Markdown 文本的 Blob 对象
            const blob = new Blob([fullMarkdown], { type: 'text/markdown;charset=utf-8' });
            // 创建一个指向该 Blob 的临时 URL
            const url = URL.createObjectURL(blob);
            // 创建一个隐藏的 <a> 标签用于触发下载
            const a = document.createElement('a');
            a.href = url;
            a.download = 'ocr_result.md'; // 设置下载文件的默认名称
            document.body.appendChild(a);
            a.click(); // 模拟点击
            document.body.removeChild(a); // 清理DOM
            URL.revokeObjectURL(url); // 释放内存
        }
    });
});