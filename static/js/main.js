let selectedFile = null;
let parseAPIs = [];
let translateAPIs = [];
let selectedParseAPI = null;
let selectedTranslateAPI = null;

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeUpload();
    initializeConfig();
    loadAPIsFromStorage();
});

// 初始化上传功能
function initializeUpload() {
    const uploadBox = document.getElementById('uploadBox');
    const fileInput = document.getElementById('fileInput');
    const selectFileBtn = document.getElementById('selectFileBtn');

    // 触发文件选择（兼容移动端）
    function triggerFileInput(e) {
        e.preventDefault();
        e.stopPropagation();
        fileInput.click();
    }

    // 点击上传区域
    uploadBox.addEventListener('click', triggerFileInput);
    
    // 点击按钮（移动端友好）
    if (selectFileBtn) {
        selectFileBtn.addEventListener('click', triggerFileInput);
        selectFileBtn.addEventListener('touchend', triggerFileInput);
    }

    // 文件选择
    fileInput.addEventListener('change', function(e) {
        if (e.target.files && e.target.files[0]) {
            handleFileSelect(e.target.files[0]);
        }
    });

    // 拖拽上传（桌面端）
    uploadBox.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadBox.classList.add('dragover');
    });

    uploadBox.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadBox.classList.remove('dragover');
    });

    uploadBox.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadBox.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });
    
    // 防止移动端长按弹出菜单
    uploadBox.addEventListener('contextmenu', function(e) {
        e.preventDefault();
    });
}

// 初始化配置
function initializeConfig() {
    // 默认展开配置
    document.getElementById('configContent').classList.add('show');
    document.getElementById('toggleIcon').classList.add('rotate');
}

// 切换配置显示
function toggleConfig() {
    const configContent = document.getElementById('configContent');
    const toggleIcon = document.getElementById('toggleIcon');
    
    configContent.classList.toggle('show');
    toggleIcon.classList.toggle('rotate');
}

// 处理文件选择
function handleFileSelect(file) {
    if (!file) return;

    // 检查文件类型
    if (!file.name.endsWith('.pdf')) {
        showMessage('请选择 PDF 文件', 'error');
        return;
    }

    // 检查文件大小
    if (file.size > 50 * 1024 * 1024) {
        showMessage('文件大小不能超过 50MB', 'error');
        return;
    }

    selectedFile = file;

    // 显示文件信息
    document.getElementById('uploadBox').style.display = 'none';
    document.getElementById('fileInfo').style.display = 'block';
    document.getElementById('fileName').textContent = file.name;
    document.getElementById('fileSize').textContent = formatFileSize(file.size);
    document.getElementById('translateBtn').disabled = false;

    // 隐藏之前的结果
    document.getElementById('progressSection').style.display = 'none';
    document.getElementById('resultSection').style.display = 'none';
}

// 移除文件
function removeFile() {
    selectedFile = null;
    document.getElementById('uploadBox').style.display = 'block';
    document.getElementById('fileInfo').style.display = 'none';
    document.getElementById('translateBtn').disabled = true;
    document.getElementById('fileInput').value = '';
    
    document.getElementById('progressSection').style.display = 'none';
    document.getElementById('resultSection').style.display = 'none';
}

// API管理
function loadAPIsFromStorage() {
    const savedParseAPIs = localStorage.getItem('parseAPIs');
    const savedTranslateAPIs = localStorage.getItem('translateAPIs');
    
    if (savedParseAPIs) {
        parseAPIs = JSON.parse(savedParseAPIs);
        renderParseAPIs();
    }
    
    if (savedTranslateAPIs) {
        translateAPIs = JSON.parse(savedTranslateAPIs);
        renderTranslateAPIs();
    }
}

function saveAPIsToStorage() {
    localStorage.setItem('parseAPIs', JSON.stringify(parseAPIs));
    localStorage.setItem('translateAPIs', JSON.stringify(translateAPIs));
}

// 添加解析API
function addParseAPI() {
    const api = {
        id: Date.now(),
        name: `API Key ${parseAPIs.length + 1}`,
        token: ''
    };
    
    parseAPIs.push(api);
    saveAPIsToStorage();
    renderParseAPIs();
}

// 渲染解析API列表
function renderParseAPIs() {
    const list = document.getElementById('parseAPIList');
    
    if (parseAPIs.length === 0) {
        list.innerHTML = '<div style="text-align: center; color: var(--gray-400); padding: 1rem; font-size: 0.875rem;">暂无配置，使用默认Key</div>';
        selectedParseAPI = null;
        return;
    }
    
    // 如果没有选中的API，默认选择第一个
    if (!selectedParseAPI && parseAPIs.length > 0) {
        selectedParseAPI = parseAPIs[0].id;
    }
    
    list.innerHTML = parseAPIs.map(api => `
        <div class="api-item ${selectedParseAPI === api.id ? 'api-item-selected' : ''}" data-id="${api.id}">
            <div class="api-item-header">
                <div class="api-item-title-group">
                    <label class="radio-label">
                        <input type="radio" name="parseAPI" value="${api.id}" 
                               ${selectedParseAPI === api.id ? 'checked' : ''} 
                               onchange="selectParseAPI(${api.id})">
                        <span class="radio-custom"></span>
                        <span class="api-item-title">${api.name}</span>
                    </label>
                </div>
                <div class="api-item-actions">
                    <button class="btn-api-action" onclick="removeParseAPI(${api.id})" title="删除">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                    </button>
                </div>
            </div>
            <div class="api-item-content">
                <div class="api-input-group">
                    <label>名称（可选）</label>
                    <input type="text" class="api-input" placeholder="如：主Key、备用Key" value="${api.name}" onchange="updateParseAPI(${api.id}, 'name', this.value)">
                </div>
                <div class="api-input-group">
                    <label>API Key</label>
                    <input type="password" class="api-input" placeholder="输入解析API密钥" value="${api.token}" onchange="updateParseAPI(${api.id}, 'token', this.value)">
                </div>
            </div>
        </div>
    `).join('');
}

// 选择解析API
function selectParseAPI(id) {
    selectedParseAPI = id;
    renderParseAPIs();
    showMessage('已选择此解析API', 'success');
}

function updateParseAPI(id, field, value) {
    const api = parseAPIs.find(a => a.id === id);
    if (api) {
        api[field] = value;
        saveAPIsToStorage();
    }
}

function removeParseAPI(id) {
    if (confirm('确定要删除这个API配置吗？')) {
        parseAPIs = parseAPIs.filter(a => a.id !== id);
        saveAPIsToStorage();
        renderParseAPIs();
    }
}

// 添加翻译API
function addTranslateAPI() {
    const api = {
        id: Date.now(),
        name: `翻译AI ${translateAPIs.length + 1}`,
        url: '',
        apiKey: '',
        model: ''
    };
    
    translateAPIs.push(api);
    saveAPIsToStorage();
    renderTranslateAPIs();
}

// 渲染翻译API列表
function renderTranslateAPIs() {
    const list = document.getElementById('translateAPIList');
    
    if (translateAPIs.length === 0) {
        list.innerHTML = '<div style="text-align: center; color: var(--gray-400); padding: 1rem; font-size: 0.875rem;">暂无配置，使用默认配置</div>';
        selectedTranslateAPI = null;
        return;
    }
    
    // 如果没有选中的API，默认选择第一个
    if (!selectedTranslateAPI && translateAPIs.length > 0) {
        selectedTranslateAPI = translateAPIs[0].id;
    }
    
    list.innerHTML = translateAPIs.map(api => `
        <div class="api-item ${selectedTranslateAPI === api.id ? 'api-item-selected' : ''}" data-id="${api.id}">
            <div class="api-item-header">
                <div class="api-item-title-group">
                    <label class="radio-label">
                        <input type="radio" name="translateAPI" value="${api.id}" 
                               ${selectedTranslateAPI === api.id ? 'checked' : ''} 
                               onchange="selectTranslateAPI(${api.id})">
                        <span class="radio-custom"></span>
                        <span class="api-item-title">${api.name}</span>
                    </label>
                </div>
                <div class="api-item-actions">
                    <button class="btn-api-action" onclick="removeTranslateAPI(${api.id})" title="删除">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                    </button>
                </div>
            </div>
            <div class="api-item-content">
                <div class="api-input-group">
                    <label>名称</label>
                    <input type="text" class="api-input" placeholder="如：Claude 4.5" value="${api.name}" onchange="updateTranslateAPI(${api.id}, 'name', this.value)">
                </div>
                <div class="api-input-group">
                    <label>API URL (OpenAI兼容)</label>
                    <input type="text" class="api-input" placeholder="https://b4u.qzz.io/" value="${api.url}" onchange="updateTranslateAPI(${api.id}, 'url', this.value)">
                </div>
                <div class="api-input-group">
                    <label>API Key</label>
                    <input type="password" class="api-input" placeholder="sk-..." value="${api.apiKey}" onchange="updateTranslateAPI(${api.id}, 'apiKey', this.value)">
                </div>
                <div class="api-input-group">
                    <label>模型名称</label>
                    <input type="text" class="api-input" placeholder="claude-4.5-sonnet-think" value="${api.model}" onchange="updateTranslateAPI(${api.id}, 'model', this.value)">
                </div>
            </div>
        </div>
    `).join('');
}

// 选择翻译API
function selectTranslateAPI(id) {
    selectedTranslateAPI = id;
    renderTranslateAPIs();
    showMessage('已选择此翻译API', 'success');
}

function updateTranslateAPI(id, field, value) {
    const api = translateAPIs.find(a => a.id === id);
    if (api) {
        api[field] = value;
        saveAPIsToStorage();
    }
}

function removeTranslateAPI(id) {
    if (confirm('确定要删除这个API配置吗？')) {
        translateAPIs = translateAPIs.filter(a => a.id !== id);
        saveAPIsToStorage();
        renderTranslateAPIs();
    }
}

// 翻译PDF
async function translatePDF() {
    if (!selectedFile) return;

    const translateBtn = document.getElementById('translateBtn');
    const progressSection = document.getElementById('progressSection');
    const progressFill = document.getElementById('progressFill');
    const progressText = document.getElementById('progressText');
    const resultSection = document.getElementById('resultSection');

    translateBtn.disabled = true;

    try {
        progressSection.style.display = 'block';
        resultSection.style.display = 'none';

        // 创建FormData
        const formData = new FormData();
        formData.append('file', selectedFile);

        // 添加配置参数
        formData.append('is_ocr', document.getElementById('is_ocr').checked);
        formData.append('include_image_base64', document.getElementById('include_image_base64').checked);
        formData.append('formula_enable', document.getElementById('formula_enable').checked);
        formData.append('table_enable', document.getElementById('table_enable').checked);
        formData.append('layout_model', document.getElementById('layout_model').value);
        formData.append('output_format', 'md');
        
        // 添加翻译模式
        formData.append('translation_mode', document.getElementById('translation_mode').value);

        const endPages = document.getElementById('end_pages').value.trim();
        if (endPages) {
            formData.append('end_pages', endPages);
        }

        // 添加选中的API配置
        if (selectedParseAPI) {
            const parseAPI = parseAPIs.find(api => api.id === selectedParseAPI);
            if (parseAPI && parseAPI.token) {
                formData.append('parse_api_token', parseAPI.token);
            }
        }
        
        if (selectedTranslateAPI) {
            const translateAPI = translateAPIs.find(api => api.id === selectedTranslateAPI);
            if (translateAPI) {
                formData.append('translate_api_url', translateAPI.url);
                formData.append('translate_api_key', translateAPI.apiKey);
                formData.append('translate_api_model', translateAPI.model);
            }
        }

        // 进度模拟
        let progress = 0;
        const progressInterval = setInterval(() => {
            if (progress < 90) {
                progress += Math.random() * 10;
                if (progress > 90) progress = 90;
                progressFill.style.width = progress + '%';
                
                if (progress < 30) {
                    progressText.textContent = '上传中...';
                } else if (progress < 60) {
                    progressText.textContent = '解析中...';
                } else {
                    progressText.textContent = '翻译中...';
                }
            }
        }, 500);

        // 发送请求
        const response = await fetch('/translate', {
            method: 'POST',
            body: formData
        });

        clearInterval(progressInterval);

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || '翻译失败');
        }

        progressFill.style.width = '100%';
        progressText.textContent = '生成PDF...';

        // 下载文件
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `translated_${selectedFile.name}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        // 显示成功
        progressSection.style.display = 'none';
        resultSection.style.display = 'block';

        setTimeout(() => {
            translateBtn.disabled = false;
            translateBtn.textContent = '重新翻译';
        }, 1000);

    } catch (error) {
        console.error('Error:', error);
        showMessage('翻译失败: ' + error.message, 'error');
        
        progressSection.style.display = 'none';
        translateBtn.disabled = false;
    }
}

// 显示消息
function showMessage(message, type = 'info') {
    // 创建toast元素
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    // 设置图标
    let icon = '';
    switch(type) {
        case 'success':
            icon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>';
            break;
        case 'error':
            icon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>';
            break;
        case 'warning':
            icon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>';
            break;
        default:
            icon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>';
    }
    
    toast.innerHTML = `
        <div class="toast-icon">${icon}</div>
        <div class="toast-message">${message}</div>
    `;
    
    document.body.appendChild(toast);
    
    // 触发动画
    setTimeout(() => toast.classList.add('toast-show'), 10);
    
    // 3秒后移除
    setTimeout(() => {
        toast.classList.remove('toast-show');
        setTimeout(() => document.body.removeChild(toast), 300);
    }, 3000);
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}
