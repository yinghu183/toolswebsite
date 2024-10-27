document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('image');
    const fileNameSpan = document.querySelector('.file-name');
    const previewImage = document.getElementById('previewImage');
    const toolForm = document.getElementById('toolForm');
    const resultArea = document.getElementById('resultArea');
    const resultMessage = document.getElementById('resultMessage');
    const downloadBtn = document.getElementById('downloadBtn');

    fileInput.addEventListener('change', function(e) {
        if (this.files && this.files[0]) {
            const file = this.files[0];
            fileNameSpan.textContent = file.name;
            const reader = new FileReader();
            reader.onload = function(e) {
                previewImage.src = e.target.result;
            }
            reader.readAsDataURL(file);
        } else {
            fileNameSpan.textContent = '未选择文件';
            previewImage.src = '';
        }
    });

    ['size', 'opacity', 'angle'].forEach(id => {
        const element = document.getElementById(id);
        const valueSpan = document.getElementById(`${id}Value`);
        element.addEventListener('input', function() {
            valueSpan.textContent = this.value;
        });
    });

    toolForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(toolForm);

        fetch('/add_watermark', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                resultMessage.textContent = data.error;
                downloadBtn.style.display = 'none';
            } else {
                resultMessage.textContent = '水印添加成功！';
                downloadBtn.style.display = 'inline-block';
                downloadBtn.onclick = function() {
                    window.location.href = `/download/${data.result}`;
                };
                // 更新预览图为处理后的图片
                previewImage.src = `/download/${data.result}`;
            }
            resultArea.style.display = 'block';
        })
        .catch(error => {
            console.error('Error:', error);
            resultMessage.textContent = '操作出错，请重试';
            downloadBtn.style.display = 'none';
            resultArea.style.display = 'block';
        });
    });
});
