document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('ocrForm');
    const resultDiv = document.getElementById('result');
    const loadingDiv = document.getElementById('loading');
    const markdownContent = document.getElementById('markdown-content');
    const downloadBtn = document.getElementById('download-btn');
    let fullMarkdown = '';

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

        fetch('/zerox_ocr', {
            method: 'POST',
            body: formData
        })
        .then(async response => {
            console.log('Response status:', response.status);
            console.log('Response headers:', Object.fromEntries(response.headers.entries()));
            
            const contentType = response.headers.get('content-type');
            console.log('Content-Type:', contentType);

            if (!response.ok) {
                if (contentType && contentType.includes('application/json')) {
                    const errorData = await response.json();
                    console.log('Error response data:', errorData);
                    throw new Error(errorData.error || '服务器处理失败');
                } else {
                    const text = await response.text();
                    console.log('Error response text:', text);
                    throw new Error('服务器响应错误');
                }
            }

            if (!contentType || !contentType.includes('application/json')) {
                const text = await response.text();
                console.log('Unexpected response text:', text);
                throw new Error('服务器返回了非JSON格式的数据');
            }

            try {
                const text = await response.text();
                console.log('Response text:', text);
                if (!text) {
                    throw new Error('服务器返回了空响应');
                }
                return JSON.parse(text);
            } catch (error) {
                console.error('JSON parse error:', error);
                throw new Error('JSON解析失败: ' + error.message);
            }
        })
        .then(data => {
            console.log('Parsed data:', data);
            loadingDiv.style.display = 'none';
            resultDiv.style.display = 'block';
            
            if (!data || typeof data !== 'object') {
                throw new Error('服务器返回了无效的数据格式');
            }

            if (data.error) {
                throw new Error(data.error);
            }

            if (data.markdown) {
                fullMarkdown = data.markdown;
                try {
                    if (window.marked) {
                        markdownContent.innerHTML = marked.parse(data.markdown);
                    } else {
                        markdownContent.textContent = data.markdown;
                    }
                    downloadBtn.style.display = 'inline-block';
                } catch (error) {
                    console.error('Markdown解析错误:', error);
                    markdownContent.textContent = data.markdown;
                }
            } else {
                throw new Error('服务器返回的数据中没有markdown内容');
            }
        })
        .catch(error => {
            console.error('处理过程中发生错误:', error);
            loadingDiv.style.display = 'none';
            resultDiv.style.display = 'block';
            markdownContent.innerHTML = `<div class="error"><strong>错误:</strong> ${error.message}</div>`;
            downloadBtn.style.display = 'none';
        });
    });

    downloadBtn.addEventListener('click', function() {
        if (fullMarkdown) {
            const blob = new Blob([fullMarkdown], { type: 'text/markdown;charset=utf-8' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'ocr_result.md';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    });
});