document.addEventListener('DOMContentLoaded', function() {
    const toolsContainer = document.getElementById('tools');
    const aiToolsContainer = document.getElementById('ai-tools');
    const modal = document.getElementById('modal');
    const modalBody = document.getElementById('modal-body');
    const closeBtn = document.getElementsByClassName('close')[0];

    toolsContainer.addEventListener('click', function(e) {
        const card = e.target.closest('.card');
        if (card) {
            const toolName = card.dataset.tool;
            if (toolName === 'Zerox OCR') {
                window.open('/zerox_ocr', '_blank');
            } else {
                loadToolInterface(toolName);
                modal.style.display = 'block';
            }
        }
    });

    aiToolsContainer.addEventListener('click', function(e) {
        const card = e.target.closest('.card');
        if (card) {
            const aiTool = card.dataset.aiTool;
            loadAITool(aiTool);
            modal.style.display = 'block';
        }
    });

    closeBtn.onclick = function() {
        modal.style.display = 'none';
        modalBody.innerHTML = '';
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
            modalBody.innerHTML = '';
        }
    }

    function loadToolInterface(toolName) {
        modalBody.innerHTML = '';
        
        if (toolName === 'Irr Calculator') {
            modalBody.innerHTML = `
                <h2>信用卡账单分期真实利率计算器</h2>
                <div class="tool-container irr-calculator">
                    <form id="toolForm" class="tool-form">
                        <div class="input-group">
                            <label for="principal">分期本金</label>
                            <input type="number" id="principal" name="principal" step="0.01" required>
                        </div>
                        <div class="input-group">
                            <label for="payment">每期还款本息</label>
                            <input type="number" id="payment" name="payment" step="0.01" required>
                        </div>
                        <div class="input-group">
                            <label for="periods">还款期数</label>
                            <input type="number" id="periods" name="periods" step="1" required>
                        </div>
                        <button type="submit" class="submit-btn">计算</button>
                    </form>
                    <div id="toolResult" class="tool-result">
                        <div class="result-item">
                            <span>年化真实利率</span>
                            <span id="annualRate"></span>
                        </div>
                        <div class="result-item">
                            <span>月化真实利率</span>
                            <span id="monthlyRate"></span>
                        </div>
                    </div>
                </div>
            `;
        } else if (toolName === 'Pinyin Converter') {
            modalBody.innerHTML = `
                <h2>姓名转拼音</h2>
                <div class="tool-container pinyin-converter">
                    <form id="toolForm" class="tool-form">
                        <div class="input-group">
                            <label for="text">输入姓名(以空格分开)</label>
                            <textarea id="text" name="text" required></textarea>
                        </div>
                        <button type="submit" class="submit-btn">转换</button>
                    </form>
                    <div id="toolResult" class="tool-result"></div>
                </div>
            `;
        } else if (toolName === 'Image Watermark') {
            modalBody.innerHTML = `
                <h2 class="watermark-title">图片水印</h2>
                <div class="tool-container image-watermark">
                    <div class="watermark-layout">
                        <div class="watermark-preview">
                            <canvas id="previewCanvas"></canvas>
                        </div>
                        <div class="watermark-form">
                            <form id="toolForm" class="tool-form">
                                <div class="input-group">
                                    <label for="image"><i class="fas fa-image"></i> 选择图片</label>
                                    <input type="file" id="image" name="image" accept="image/*" required>
                                </div>
                                <div class="input-group">
                                    <label for="mark"><i class="fas fa-font"></i> 水印文字</label>
                                    <input type="text" id="mark" name="mark" required>
                                </div>
                                <div class="input-group">
                                    <label for="color"><i class="fas fa-palette"></i> 水印颜色</label>
                                    <input type="color" id="color" name="color" value="#000000">
                                </div>
                                <div class="input-group">
                                    <label for="size"><i class="fas fa-text-height"></i> 字体大小: <span id="sizeValue">50</span></label>
                                    <input type="range" id="size" name="size" min="10" max="100" value="50">
                                </div>
                                <div class="input-group">
                                    <label for="opacity"><i class="fas fa-low-vision"></i> 透明度: <span id="opacityValue">0.5</span></label>
                                    <input type="range" id="opacity" name="opacity" min="0" max="1" step="0.1" value="0.5">
                                </div>
                                <div class="input-group">
                                    <label for="angle"><i class="fas fa-redo"></i> 旋转角度: <span id="angleValue">30</span>°</label>
                                    <input type="range" id="angle" name="angle" min="0" max="360" value="30">
                                </div>
                                <button type="submit" class="submit-btn"><i class="fas fa-magic"></i> 添加水印</button>
                            </form>
                        </div>
                    </div>
                    <div id="toolResult" class="tool-result"></div>
                </div>
            `;

            const imageInput = document.getElementById('image');
            const previewCanvas = document.getElementById('previewCanvas');
            const ctx = previewCanvas.getContext('2d');
            let originalImage = new Image();

            imageInput.addEventListener('change', function(e) {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        originalImage.src = e.target.result;
                        originalImage.onload = function() {
                            updatePreview();
                        }
                    }
                    reader.readAsDataURL(file);
                }
            });

            function updatePreview() {
                const mark = document.getElementById('mark').value;
                const color = document.getElementById('color').value;
                const size = document.getElementById('size').value;
                const opacity = document.getElementById('opacity').value;
                const angle = document.getElementById('angle').value;

                // 设置画布大小
                const maxWidth = 400;
                const maxHeight = 400;
                let scale = Math.min(maxWidth / originalImage.width, maxHeight / originalImage.height);
                previewCanvas.width = originalImage.width * scale;
                previewCanvas.height = originalImage.height * scale;

                // 绘制原始图片
                ctx.drawImage(originalImage, 0, 0, previewCanvas.width, previewCanvas.height);

                // 添加水印
                ctx.save();
                ctx.globalAlpha = opacity;
                ctx.fillStyle = color;
                ctx.font = `${size * scale / 2}px Arial`;
                ctx.translate(previewCanvas.width / 2, previewCanvas.height / 2);
                ctx.rotate(angle * Math.PI / 180);
                ctx.fillText(mark, 0, 0);
                ctx.restore();
            }

            // 为所有输入添加事件监听器
            ['mark', 'color', 'size', 'opacity', 'angle'].forEach(id => {
                const element = document.getElementById(id);
                element.addEventListener('input', function() {
                    if (id === 'size' || id === 'opacity' || id === 'angle') {
                        document.getElementById(`${id}Value`).textContent = this.value;
                    }
                    updatePreview();
                });
            });

            const toolForm = document.getElementById('toolForm');
            toolForm.addEventListener('submit', function(e) {
                e.preventDefault();
                const formData = new FormData(toolForm);

                fetch('/add_watermark', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    const toolResult = document.getElementById('toolResult');
                    if (data.error) {
                        toolResult.innerHTML = `<p class="error">${data.error}</p>`;
                    } else {
                        toolResult.innerHTML = `
                            <p>水印添加成功！</p>
                            <a href="/download/${data.result}" class="download-btn">下载处理后的图片</a>
                        `;
                    }
                    toolResult.style.display = 'block';
                })
                .catch(error => {
                    console.error('Error:', error);
                    document.getElementById('toolResult').innerHTML = '<p class="error">操作出错，请重试</p>';
                });
            });
        }

        const toolForm = document.getElementById('toolForm');

        toolForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(toolForm);
            const data = Object.fromEntries(formData.entries());

            if (toolName === 'Irr Calculator') {
                data.principal = parseFloat(data.principal);
                data.payment = parseFloat(data.payment);
                data.periods = parseInt(data.periods);
            }

            let endpoint = toolName === 'Pinyin Converter' ? '/convert_pinyin' : '/calculate_irr';

            fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            })
            .then(response => response.json())
            .then(data => {
                const toolResult = document.getElementById('toolResult');
                if (data.error) {
                    toolResult.innerHTML = `<p class="error">${data.error}</p>`;
                } else {
                    if (toolName === 'Pinyin Converter') {
                        toolResult.innerHTML = Array.isArray(data.result) ? data.result.join('<br>') : data.result;
                    } else if (toolName === 'Irr Calculator') {
                        document.getElementById('annualRate').textContent = data.result.annual_irr;
                        document.getElementById('monthlyRate').textContent = data.result.monthly_irr;
                    }
                }
                toolResult.style.display = 'block';
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('toolResult').innerHTML = '<p class="error">操作出错，请重试</p>';
            });
        });
    }

    function loadAITool(aiTool) {
        modalBody.innerHTML = ''; // 清空模态框内容

        let token;
        let title;
        switch(aiTool) {
            case 'a':
                token = 'XGNUclyu0yzj5eMm';
                title = '作文润色';
                break;
            case 'b':
                token = 'Jwla83F8CmWY0S3M';
                title = '英语词典';
                break;
            case 'c':
                token = 'YTsXdjIJmlspSSA1';
                title = '多语言翻译';
                break;
        }
        
        let iframe = document.createElement('iframe');
        iframe.src = `https://dify.141010.xyz/chatbot/${token}`;
        iframe.style.width = '100%';
        iframe.style.height = '100%';
        iframe.style.border = 'none';
        iframe.allow = 'microphone';
        
        let titleElement = document.createElement('h2');
        titleElement.textContent = title;
        titleElement.style.textAlign = 'center';
        titleElement.style.marginBottom = '20px';
        
        modalBody.appendChild(titleElement);
        modalBody.appendChild(iframe);
    }
});
