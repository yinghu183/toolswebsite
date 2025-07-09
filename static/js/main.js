// static/js/main.js

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
            
            // --- START MODIFICATION ---
            // Changed the logic to open pages in a new tab.
            switch (toolName) {
                case 'Image Watermark':
                    window.open('/image_watermark', '_blank');
                    break;
                case 'Zerox OCR':
                    window.open('/zerox_ocr', '_blank');
                    break;
                case 'Irr Calculator':
                    window.open('/irr_calculator', '_blank');
                    break;
                case 'Pinyin Converter':
                    window.open('/pinyin_converter', '_blank');
                    break;
                default:
                    // Fallback or for other tools you might add
                    console.log("Tool not configured for new tab yet:", toolName);
                    break;
            }
            // --- END MODIFICATION ---
        }
    });

    // AI tools still use the modal, so this logic remains.
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

    // This function is now only used for AI tools.
    function loadAITool(aiTool) {
        modalBody.innerHTML = ''; // Clear modal content

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