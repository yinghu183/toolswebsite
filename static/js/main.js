document.addEventListener('DOMContentLoaded', function() {
    const toolsContainer = document.getElementById('tools');
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
                <input type="number" id="principal" name="principal" required><br>
                <label for="payment">每期还款额:</label>
                <input type="number" id="payment" name="payment" required><br>
                <label for="periods">还款期数:</label>
                <input type="number" id="periods" name="periods" required><br>
            `;
        }

        toolForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(toolForm);
            const data = Object.fromEntries(formData.entries());

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
                if (data.error) {
                    document.getElementById('toolResult').innerHTML = `<p style="color: red;">${data.error}</p>`;
                } else {
                    let result = '';
                    if (Array.isArray(data.result)) {
                        result = data.result.join('<br>');
                    } else if (typeof data.result === 'object') {
                        result = `年化IRR: ${(data.result.annual_irr * 100).toFixed(2)}%<br>月化IRR: ${(data.result.monthly_irr * 100).toFixed(2)}%`;
                    } else {
                        result = data.result;
                    }
                    document.getElementById('toolResult').innerHTML = `<p>${result}</p>`;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                document.getElementById('toolResult').innerHTML = '<p style="color: red;">操作出错，请重试</p>';
            });
        });
    }
});