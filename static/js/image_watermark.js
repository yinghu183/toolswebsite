// static/js/image_watermark.js

document.addEventListener('DOMContentLoaded', function() {
    // 获取所有需要的DOM元素
    const imageInput = document.getElementById('imageFile');
    const fileNameSpan = document.getElementById('fileName');
    const canvas = document.getElementById('previewCanvas');
    const ctx = canvas.getContext('2d');
    const toolForm = document.getElementById('toolForm');
    const resultArea = document.getElementById('resultArea');
    const resultMessage = document.getElementById('resultMessage');
    const downloadBtn = document.getElementById('downloadBtn');

    // 存储原始图片对象，以便重绘
    let originalImage = null;

    // 监听所有会影响水印效果的输入控件
    const controls = ['mark', 'color', 'size', 'opacity', 'angle', 'space'];
    controls.forEach(id => {
        const element = document.getElementById(id);
        element.addEventListener('input', () => {
            // 更新滑块旁边的数值显示
            const valueSpan = document.getElementById(`${id}Value`);
            if (valueSpan) {
                valueSpan.textContent = element.value;
            }
            // 实时更新水印预览
            drawWatermarkPreview();
        });
    });

    // 监听文件上传
    imageInput.addEventListener('change', function(e) {
        if (this.files && this.files[0]) {
            const file = this.files[0];
            fileNameSpan.textContent = file.name;

            const reader = new FileReader();
            reader.onload = function(event) {
                const img = new Image();
                img.onload = function() {
                    originalImage = img; // 保存原始图片
                    drawWatermarkPreview(); // 首次绘制预览
                };
                img.src = event.target.result;
            };
            reader.readAsDataURL(file);
        }
    });

    /**
     * 核心函数：绘制带水印的预览图
     * 这个函数会在任何参数变化时被调用
     */
    function drawWatermarkPreview() {
        if (!originalImage) return;

        // 1. 根据原图比例设置canvas尺寸
        const canvasContainer = document.querySelector('.canvas-container');
        const containerWidth = canvasContainer.offsetWidth;
        const scale = containerWidth / originalImage.width;
        canvas.width = containerWidth;
        canvas.height = originalImage.height * scale;

        // 2. 清空画布并绘制原始图片
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(originalImage, 0, 0, canvas.width, canvas.height);

        // 3. 获取所有水印参数
        const markText = document.getElementById('mark').value;
        const color = document.getElementById('color').value;
        const opacity = parseFloat(document.getElementById('opacity').value);
        // 注意：字体大小和间距需要根据画布缩放比例进行调整
        const fontSize = parseInt(document.getElementById('size').value) * scale;
        const angle = parseInt(document.getElementById('angle').value);
        const space = parseInt(document.getElementById('space').value) * scale;
        
        if (!markText) return; // 如果没有水印文字，则不绘制

        // 4. 设置水印样式
        ctx.font = `${fontSize}px Arial`;
        ctx.fillStyle = color;
        ctx.globalAlpha = opacity;
        
        // 5. 计算并平铺水印
        // 保存当前画布状态
        ctx.save();
        
        // 将画布中心设为旋转中心
        ctx.translate(canvas.width / 2, canvas.height / 2);
        ctx.rotate(angle * Math.PI / 180);
        ctx.translate(-canvas.width / 2, -canvas.height / 2);
        
        const textMetrics = ctx.measureText(markText);
        const textWidth = textMetrics.width;
        
        // 使用一个足够大的范围来确保水印覆盖整个旋转后的画布
        for (let y = -canvas.height; y < canvas.height * 2; y += (fontSize + space)) {
            for (let x = -canvas.width; x < canvas.width * 2; x += (textWidth + space)) {
                ctx.fillText(markText, x, y);
            }
        }

        // 恢复画布状态
        ctx.restore();
    }
    
    // 监听表单提交，用于最终生成图片
    toolForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // 确保用户已上传文件
        if (!imageInput.files || imageInput.files.length === 0) {
            alert('请先选择一张图片！');
            return;
        }

        const formData = new FormData(toolForm);
        resultMessage.textContent = '正在处理中，请稍候...';
        resultArea.style.display = 'block';
        downloadBtn.style.display = 'none';

        fetch('/add_watermark', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                resultMessage.textContent = `处理失败: ${data.error}`;
                downloadBtn.style.display = 'none';
            } else {
                resultMessage.textContent = '水印添加成功！点击下方按钮下载。';
                downloadBtn.href = `/download/${data.result}`;
                downloadBtn.style.display = 'inline-block';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            resultMessage.textContent = '操作出错，请检查网络或联系管理员。';
            downloadBtn.style.display = 'none';
        });
    });
});