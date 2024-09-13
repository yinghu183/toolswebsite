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
            loadToolInterface(toolName);
            modal.style.display = 'block';
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
        modalBody.innerHTML = `
            <h3>${toolName}</h3>
            <form id="toolForm">
                <div id="inputFields"></div>
                <button type="submit">执行</button>
            </form>
            <div id="toolResult"></div>
        `;

        const inputFields = document.getElementById('inputFields');
        const toolForm = document.getElementById('toolForm');

        if (toolName === 'Pinyin Converter') {
            inputFields.innerHTML = `
                <label for="text">输入汉字:</label>
                <textarea id="text" name="text" required></textarea><br>
            `;
        } else if (toolName === 'Irr Calculator') {
            inputFields.innerHTML = `
                <label for="principal">本金:</label>
                <input type="number" id="principal" name="principal" step="0.01" required><br>
                <label for="payment">每期还款额:</label>
                <input type="number" id="payment" name="payment" step="0.01" required><br>
                <label for="periods">还款期数:</label>
                <input type="number" id="periods" name="periods" step="1" required><br>
            `;
        }

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
                    toolResult.innerHTML = `<p style="color: red;">${data.error}</p>`;
                } else {
                    let result = '';
                    if (toolName === 'Pinyin Converter') {
                        result = Array.isArray(data.result) ? data.result.join('<br>') : data.result;
                    } else if (toolName === 'Irr Calculator') {
                        result = `年化IRR: ${data.result.annual_irr}<br>月化IRR: ${data.result.monthly_irr}`;
                    }
                    toolResult.innerHTML = `<p>${result}</p>`;
                }
                toolResult.style.display = 'block';
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('toolResult').innerHTML = '<p style="color: red;">操作出错，请重试</p>';
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
        iframe.src = `http://dify.141010.xyz/chatbot/${token}`;
        iframe.style.width = '100%';
        iframe.style.height = '700px';
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