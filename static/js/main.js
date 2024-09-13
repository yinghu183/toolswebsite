document.addEventListener('DOMContentLoaded', function() {
    const toolsContainer = document.getElementById('tools');
    const aiToolsContainer = document.getElementById('ai-tools');
    const externalLinksContainer = document.getElementById('external-links');
    const resultDiv = document.getElementById('result');

    toolsContainer.addEventListener('click', function(e) {
        const card = e.target.closest('.card');
        if (card) {
            const toolName = card.dataset.tool;
            loadToolInterface(toolName);
        }
    });

    function loadToolInterface(toolName) {
        resultDiv.innerHTML = `
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

    // Add AI tools
    const aiTools = [
        { name: 'AI Assistant', id: 'Jwla83F8CmWY0S3M' },
        // Add more AI tools here
    ];

    aiTools.forEach(tool => {
        aiToolsContainer.innerHTML += `
            <div class="card ai-tool" data-tool-id="${tool.id}">
                <h2>${tool.name}</h2>
                <button>打开</button>
            </div>
        `;
    });

    // Add external links
    const externalLinks = [
        { name: '百度', url: 'https://www.baidu.com' },
        { name: 'Google', url: 'https://www.google.com' },
        // Add more external links here
    ];

    externalLinks.forEach(link => {
        externalLinksContainer.innerHTML += `
            <div class="card external-link">
                <h2>${link.name}</h2>
                <a href="${link.url}" target="_blank">访问</a>
            </div>
        `;
    });

    // Event listener for AI tools
    aiToolsContainer.addEventListener('click', function(e) {
        if (e.target.tagName === 'BUTTON') {
            const card = e.target.closest('.card');
            if (card) {
                const toolId = card.dataset.toolId;
                openAITool(toolId);
            }
        }
    });

    function openAITool(toolId) {
        resultDiv.innerHTML = `
            <div id="ai-tool-container" style="width: 100%; height: 500px;"></div>
        `;
        // Reset any existing chatbot
        if (window.DifyChat) {
            window.DifyChat.destroy();
        }
        // Initialize new chatbot
        window.difyChatbotConfig = {
            token: toolId,
            baseUrl: 'http://dify.141010.xyz',
            containerSelector: '#ai-tool-container'
        };
        // Load the Dify script dynamically
        const script = document.createElement('script');
        script.src = 'http://dify.141010.xyz/embed.min.js';
        script.onload = function() {
            window.DifyChat.init(window.difyChatbotConfig);
        };
        document.body.appendChild(script);
    }

    // ... existing code for regular tools ...
});