// static/js/zerox_ocr.js

document.addEventListener('DOMContentLoaded', function() {
    // DOM 元素引用
    const container = document.getElementById('ocr-container');
    const form = document.getElementById('ocrForm');
    const resetBtn = document.getElementById('reset-btn');

    // 状态元素引用
    const processingFilename = document.getElementById('processing-filename');
    const errorMessage = document.getElementById('error-message');
    const downloadBtn = document.getElementById('download-btn');

    let processingInterval = null;

    // 表单提交事件
    form.addEventListener('submit', function(event) {
        event.preventDefault();

        const fileInput = document.getElementById('document');
        if (!fileInput.files || fileInput.files.length === 0) {
            showError('请选择一个文件。');
            return;
        }
        
        const formData = new FormData(form);
        // 注意：这里的 name="file" 应该与 HTML 中的 <input name="file"> 对应
        // 如果 HTML 中是 name="document"，JS 会因为找不到 'file' 而出错。
        // 我们已经在上一个版本的 HTML 中统一为 name="file"
        
        // --- 核心修正开始 ---

        // 步骤 1: 立刻更新UI，让用户马上看到“处理中”的状态
        processingFilename.textContent = fileInput.files[0].name;
        setContainerState('processing');

        // 步骤 2: 使用 setTimeout 将耗时的网络请求推迟到下一个事件循环
        // 这能保证浏览器有足够的时间来渲染上面的UI更新
        setTimeout(() => {
            fetch('/zerox_ocr', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    // 尝试解析JSON错误，如果失败则使用通用错误
                    return response.json().catch(() => {
                        throw new Error(`服务器响应错误: ${response.status}`);
                    }).then(errorData => {
                        throw new Error(errorData.error || `服务器响应错误: ${response.status}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                if (data.download_url) {
                    const filename = data.download_url.split('/').pop();
                    startStatusCheck(filename);
                } else {
                    throw new Error('服务器未返回有效的下载链接。');
                }
            })
            .catch(error => {
                console.error('处理过程中发生错误:', error);
                showError(error.message);
            });
        }, 50); // 使用一个极短的延时（50毫秒）即可

        // --- 核心修正结束 ---
    });

    // 开始轮询检查状态 (此函数保持不变)
    function startStatusCheck(filename) {
        if (processingInterval) clearInterval(processingInterval);

        processingInterval = setInterval(async () => {
            try {
                const response = await fetch(`/check_ocr_status/${filename}`);
                if (!response.ok) {
                    console.error('检查状态失败，将在2秒后重试。');
                    return;
                }
                const data = await response.json();
                
                if (data.status === 'completed') {
                    clearInterval(processingInterval);
                    setContainerState('successful');
                    setupDownloadButton(filename, data.download_url);
                }
            } catch (error) {
                console.error('检查状态时出错:', error);
            }
        }, 2000);

        setTimeout(() => {
            if (processingInterval) {
                clearInterval(processingInterval);
                if (container.classList.contains('is-processing')) {
                    showError('处理时间过长，请刷新页面重试。');
                }
            }
        }, 30 * 60 * 1000);
    }

    // 设置容器状态的辅助函数 (此函数保持不变)
    function setContainerState(state) {
        container.classList.remove('is-processing', 'is-successful', 'is-error');
        if (state) {
            container.classList.add(`is-${state}`);
        }
    }

    // 显示错误的辅助函数 (此函数保持不变)
    function showError(message) {
        if (processingInterval) clearInterval(processingInterval);
        setContainerState('error');
        errorMessage.textContent = message;
    }
    
    // 设置下载按钮 (此函数保持不变)
    function setupDownloadButton(filename, downloadUrl) {
        downloadBtn.onclick = function() {
            window.location.href = downloadUrl;
        };
    }

    // 重试按钮事件 (此函数保持不变)
    resetBtn.addEventListener('click', () => {
        setContainerState(null);
        form.reset();
        fileName.textContent = '未选择文件'; // 如果有文件名显示的话
    });
});