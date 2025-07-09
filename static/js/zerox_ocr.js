document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('ocrForm');
    const resultDiv = document.getElementById('result');
    const loadingDiv = document.getElementById('loading');
    const markdownContent = document.getElementById('markdown-content');
    const downloadBtn = document.getElementById('download-btn');

    form.addEventListener('submit', function(event) {
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

        loadingDiv.style.display = 'block';
        resultDiv.style.display = 'none';
        markdownContent.textContent = '';
        downloadBtn.style.display = 'none';

        // 设置较长的超时时间（3分钟）
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 180000);

        fetch('/zerox_ocr', {
            method: 'POST',
            body: formData,
            signal: controller.signal
        })
        .then(async response => {
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                const text = await response.text();
                throw new Error(text || '服务器响应错误');
            }
            
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                throw new Error('服务器返回了非JSON格式的数据');
            }
            
            return response.json();
        })
        .then(data => {
            loadingDiv.style.display = 'none';
            resultDiv.style.display = 'block';
            
            if (data.error) {
                throw new Error(data.error);
            }

            if (data.success && data.download_url) {
                markdownContent.innerHTML = `
                    <div class="success">
                        <p>${data.message}</p>
                        <p>文件已准备就绪，请点击下方按钮下载：</p>
                    </div>
                `;
                downloadBtn.style.display = 'inline-block';
                downloadBtn.onclick = function() {
                    window.location.href = data.download_url;
                };
            } else {
                throw new Error('处理成功但未获得下载链接');
            }
        })
        .catch(error => {
            clearTimeout(timeoutId);
            console.error('处理过程中发生错误:', error);
            loadingDiv.style.display = 'none';
            resultDiv.style.display = 'block';
            
            let errorMessage = error.message;
            if (error.name === 'AbortError') {
                errorMessage = '请求超时，请重试';
            } else if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
                errorMessage = '网络连接错误，请检查网络后重试';
            }
            
            markdownContent.innerHTML = `<div class="error"><strong>错误:</strong> ${errorMessage}</div>`;
            downloadBtn.style.display = 'none';
        });
    });
});