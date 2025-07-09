document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('ocrForm');
    const resultDiv = document.getElementById('result');
    const loadingDiv = document.getElementById('loading');
    const markdownContent = document.getElementById('markdown-content');
    const downloadBtn = document.getElementById('download-btn');

    form.addEventListener('submit', async function(event) {
        event.preventDefault();

        const formData = new FormData();
        formData.append('apiKey', document.getElementById('apiKey').value);
        formData.append('apiBase', document.getElementById('apiBase').value);
        formData.append('model', document.getElementById('model').value);
        const fileInput = document.getElementById('document');
        if (!fileInput.files || fileInput.files.length === 0) {
            resultDiv.innerHTML = `<div class="error">请选择一个文件。</div>`;
            resultDiv.style.display = 'block';
            return;
        }
        formData.append('file', fileInput.files[0]);

        try {
            loadingDiv.style.display = 'block';
            resultDiv.style.display = 'block';
            markdownContent.innerHTML = '<div class="info">正在上传文件...</div>';
            downloadBtn.style.display = 'none';

            const response = await fetch('/zerox_ocr', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`服务器响应错误: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }

            // 显示处理中的状态
            markdownContent.innerHTML = `
                <div class="info">
                    <p>${data.message || '文件已上传，正在处理中...'}</p>
                    <div class="spinner"></div>
                </div>
            `;

            // 开始轮询检查处理状态
            if (data.download_url) {
                const filename = data.download_url.split('/').pop();
                checkStatus(filename);
            } else {
                throw new Error('服务器未返回有效的下载链接');
            }

        } catch (error) {
            console.error('处理过程中发生错误:', error);
            loadingDiv.style.display = 'none';
            markdownContent.innerHTML = `<div class="error"><strong>错误:</strong> ${error.message}</div>`;
            downloadBtn.style.display = 'none';
        }
    });

    function checkStatus(filename) {
        const checkInterval = setInterval(async () => {
            try {
                const response = await fetch(`/check_ocr_status/${filename}`);
                if (!response.ok) {
                    throw new Error('检查状态失败');
                }
                const data = await response.json();
                
                if (data.status === 'completed') {
                    clearInterval(checkInterval);
                    loadingDiv.style.display = 'none';
                    markdownContent.innerHTML = `
                        <div class="success">
                            <p>OCR处理完成！</p>
                            <p>文件已准备就绪，请点击下方按钮下载：</p>
                        </div>
                    `;
                    downloadBtn.style.display = 'inline-block';
                    downloadBtn.onclick = function() {
                        window.location.href = data.download_url;
                    };
                }
            } catch (error) {
                console.error('检查状态时出错:', error);
                markdownContent.innerHTML = `<div class="error"><strong>错误:</strong> ${error.message}</div>`;
            }
        }, 2000); // 每2秒检查一次

        // 设置30分钟后停止检查
        setTimeout(() => {
            clearInterval(checkInterval);
            if (loadingDiv.style.display !== 'none') {
                loadingDiv.style.display = 'none';
                markdownContent.innerHTML = `
                    <div class="error">
                        <strong>错误:</strong> 处理时间过长，请刷新页面重试
                    </div>
                `;
            }
        }, 30 * 60 * 1000);
    }
});