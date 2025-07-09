// static/js/main.js

document.addEventListener('DOMContentLoaded', function() {
    const toolsContainer = document.getElementById('tools');
    const aiToolsContainer = document.getElementById('ai-tools');

    // “实用工具”的点击逻辑（保持不变）
    toolsContainer.addEventListener('click', function(e) {
        const card = e.target.closest('.card');
        if (card) {
            const toolName = card.dataset.tool;
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
                    console.log("未知的实用工具:", toolName);
                    break;
            }
        }
    });

    // --- START: 修改 AI 工具的点击逻辑 ---
    // 不再使用弹窗，而是直接打开新标签页
    aiToolsContainer.addEventListener('click', function(e) {
        const card = e.target.closest('.card');
        if (card) {
            const aiTool = card.dataset.aiTool;
            let targetUrl = '';
            switch (aiTool) {
                case 'a': // 作文润色
                    targetUrl = '/ai/essay_polishing';
                    break;
                case 'b': // 英语词典
                    targetUrl = '/ai/english_dictionary';
                    break;
                case 'c': // 多语言翻译
                    targetUrl = '/ai/multi_language_translator';
                    break;
                default:
                    console.log("未知的AI工具:", aiTool);
                    return; // 如果没有匹配的工具，则不执行任何操作
            }
            window.open(targetUrl, '_blank');
        }
    });
    // --- END: 修改 AI 工具的点击逻辑 ---

    // 注意：所有与 modal, closeBtn, loadAITool, window.onclick 相关的代码块现在都可以安全地删除了，
    // 因为它们不再被使用，这会让您的代码更加干净。
});