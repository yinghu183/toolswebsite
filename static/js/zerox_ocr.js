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
    form.addEventListener('submit', async function(event) {
        event.preventDefault();

        const fileInput = document.getElementById('document');
        if (!fileInput.files || fileInput.files.length === 0) {
            showError('请选择一个文件。');
            return;
        }
        
        // 准备表单数据
        const formData = new FormData(form);
        formData.append('file', fileInput.files[0]);

        // 进入处理中状态
        processingFilename.textContent = fileInput.files[0].name;
        setContainerState('processing');

        try {
            const response = await fetch('/zerox_ocr', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: `服务器响应错误: ${response.status}` }));
                throw new Error(errorData.error || `服务器响应错误: ${response.status}`);
            }

            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }

            if (data.download_url) {
                const filename = data.download_url.split('/').pop();
                startStatusCheck(filename);
            } else {
                throw new Error('服务器未返回有效的下载链接。');
            }

        } catch (error) {
            console.error('处理过程中发生错误:', error);
            showError(error.message);
        }
    });

    // 开始轮询检查状态
    function startStatusCheck(filename) {
        // 清除旧的定时器以防万一
        if (processingInterval) clearInterval(processingInterval);

        processingInterval = setInterval(async () => {
            try {
                const response = await fetch(`/check_ocr_status/${filename}`);
                if (!response.ok) {
                    // 如果检查失败，继续轮询，不直接报错
                    console.error('检查状态失败，将在2秒后重试。');
                    return;
                }
                const data = await response.json();
                
                if (data.status === 'completed') {
                    clearInterval(processingInterval);
                    setContainerState('successful');
                    setupDownloadButton(filename, data.download_url);
                }
                // 如果状态是 'processing'，则什么都不做，等待下一次轮询
            } catch (error) {
                console.error('检查状态时出错:', error);
                // 网络等问题也暂时不报错，让轮询继续
            }
        }, 2000); // 每2秒检查一次

        // 设置30分钟后超时
        setTimeout(() => {
            if (processingInterval) {
                clearInterval(processingInterval);
                // 检查是否仍处于处理中状态
                if (container.classList.contains('is-processing')) {
                    showError('处理时间过长，请刷新页面重试。');
                }
            }
        }, 30 * 60 * 1000);
    }

    // 设置容器状态的辅助函数
    function setContainerState(state) {
        container.classList.remove('is-processing', 'is-successful', 'is-error');
        if (state) {
            container.classList.add(`is-${state}`);
        }
    }

    // 显示错误的辅助函数
    function showError(message) {
        if (processingInterval) clearInterval(processingInterval);
        setContainerState('error');
        errorMessage.textContent = message;
    }
    
    // 设置下载按钮
    function setupDownloadButton(filename, downloadUrl) {
        downloadBtn.onclick = function() {
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        };
    }

    // 重试按钮事件
    resetBtn.addEventListener('click', () => {
        setContainerState(null); // 移除所有状态类，回到初始表单状态
        form.reset(); // 清空表单
    });
});