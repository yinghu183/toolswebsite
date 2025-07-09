// static/js/zerox_ocr.js

document.addEventListener('DOMContentLoaded', function() {
    // DOM 元素引用
    const container = document.getElementById('ocr-container');
    const form = document.getElementById('ocrForm');
    const resetBtn = document.getElementById('reset-btn');
    const fileInput = document.getElementById('document'); // 提前获取，保持一致

    // 状态元素引用
    const processingFilename = document.getElementById('processing-filename');
    const errorMessage = document.getElementById('error-message');
    const downloadBtn = document.getElementById('download-btn');

    let processingInterval = null;

    // 表单提交事件
    form.addEventListener('submit', function(event) {
        event.preventDefault();

        if (!fileInput.files || fileInput.files.length === 0) {
            showError('请选择一个文件。');
            return;
        }

        const formData = new FormData(form);
        
        // 关键：保留您原始代码中的这行“魔法”代码！
        // 它会手动添加一个名为 'file' 的字段，确保与后端 app.py 的要求匹配。
        formData.append('file', fileInput.files[0]);

        // 立即更新UI，显示处理中
        processingFilename.textContent = fileInput.files[0].name;
        setContainerState('processing');

        // 使用setTimeout确保UI渲染后再发起请求
        setTimeout(() => {
            fetch('/zerox_ocr', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
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
                    // 从返回的URL中解析出文件名用于轮询
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
        }, 50);
    });

    // --- 后续所有函数（轮询、状态切换等）均与您提供的原始可用JS文件保持一致 ---

    function startStatusCheck(filename) {
        if (processingInterval) clearInterval(processingInterval);
        processingInterval = setInterval(async () => {
            try {
                const response = await fetch(`/check_ocr_status/${filename}`);
                if (!response.ok) { return; }
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

    function setContainerState(state) {
        container.classList.remove('is-processing', 'is-successful', 'is-error');
        if (state) {
            container.classList.add(`is-${state}`);
        }
    }

    function showError(message) {
        if (processingInterval) clearInterval(processingInterval);
        setContainerState('error');
        errorMessage.textContent = message;
    }
    
    function setupDownloadButton(filename, downloadUrl) {
        downloadBtn.onclick = function() {
            // 直接跳转下载，比创建a元素更稳定
            window.location.href = downloadUrl;
        };
    }

    resetBtn.addEventListener('click', () => {
        setContainerState(null);
        form.reset();
    });
});