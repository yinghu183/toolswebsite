document.addEventListener('DOMContentLoaded', function() {
    // DOM 元素引用
    const ocrForm = document.getElementById('ocrForm');
    const resultContainer = document.getElementById('resultContainer');
    
    // 状态视图元素
    const processingView = document.getElementById('ocr-processing');
    const successView = document.getElementById('ocr-success');
    const errorView = document.getElementById('ocr-error');
    
    // 动态内容元素
    const processingFilename = document.getElementById('processing-filename');
    const errorMessage = document.getElementById('error-message');
    const downloadBtn = document.getElementById('download-btn');
    const resetBtn = document.getElementById('reset-btn');

    let processingInterval = null;

    // --- 状态管理函数 ---
    
    // 显示特定状态视图
    function showStateView(viewToShow) {
        resultContainer.style.display = 'block';
        ocrForm.style.display = 'none';
        
        // 隐藏所有状态视图
        [processingView, successView, errorView].forEach(view => view.style.display = 'none');
        
        // 显示指定的状态视图
        if (viewToShow) {
            viewToShow.style.display = 'block';
        }
    }
    
    // 显示处理中状态
    function showProcessingState(filename) {
        processingFilename.textContent = filename;
        showStateView(processingView);
    }

    // 显示成功状态
    function showSuccessState() {
        if (processingInterval) clearInterval(processingInterval);
        showStateView(successView);
    }
    
    // 显示错误状态
    function showErrorState(message) {
        if (processingInterval) clearInterval(processingInterval);
        errorMessage.textContent = message;
        showStateView(errorView);
    }
    
    // 重置到初始状态
    function resetToInitialState() {
        resultContainer.style.display = 'none';
        ocrForm.style.display = 'block';
        ocrForm.reset();
        if (processingInterval) clearInterval(processingInterval);
    }


    // --- 事件监听器 ---

    // 表单提交事件
    ocrForm.addEventListener('submit', async function(event) {
        event.preventDefault();

        const fileInput = document.getElementById('document');
        if (!fileInput.files || fileInput.files.length === 0) {
            alert('请选择一个文件。'); // 使用简单的alert提示
            return;
        }
        
        const formData = new FormData(ocrForm);
        const filename = fileInput.files[0].name;

        // 进入处理中状态
        showProcessingState(filename);

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
                const taskFilename = data.download_url.split('/').pop();
                startStatusCheck(taskFilename, data.download_url);
            } else {
                throw new Error('服务器未返回有效的下载链接。');
            }

        } catch (error) {
            console.error('处理过程中发生错误:', error);
            showErrorState(error.message);
        }
    });

    // 开始轮询检查状态
    function startStatusCheck(filename, finalDownloadUrl) {
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
                    showSuccessState();
                    setupDownloadButton(filename, finalDownloadUrl);
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
                if (processingView.style.display === 'block') {
                    showErrorState('处理时间过长，请刷新页面重试。');
                }
            }
        }, 30 * 60 * 1000);
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
    resetBtn.addEventListener('click', resetToInitialState);
});