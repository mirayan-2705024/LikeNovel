/**
 * 主应用逻辑
 */

// 全局状态
let currentNovelId = null;
let graphVisualizer = null;
let emotionChart = null;

// DOM 元素
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const uploadStatus = document.getElementById('uploadStatus');
const novelSelect = document.getElementById('novelSelect');

// 初始化应用
document.addEventListener('DOMContentLoaded', async () => {
    console.log('LikeNovel 应用初始化...');

    // 初始化图谱可视化器
    graphVisualizer = new GraphVisualizer('cy');

    // 绑定事件
    bindEvents();

    // 加载小说列表
    await loadNovels();

    // 健康检查
    try {
        const health = await apiClient.healthCheck();
        console.log('后端服务状态:', health);
    } catch (error) {
        showStatus('无法连接到后端服务，请确保服务已启动', 'error');
    }
});

/**
 * 绑定事件处理器
 */
function bindEvents() {
    // 上传按钮
    uploadBtn.addEventListener('click', handleUpload);

    // 小说选择
    novelSelect.addEventListener('change', handleNovelSelect);

    // 标签切换
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.dataset.tab;
            switchTab(tabName);
        });
    });

    // 时间线筛选
    const showMainPlotOnly = document.getElementById('showMainPlotOnly');
    if (showMainPlotOnly) {
        showMainPlotOnly.addEventListener('change', filterTimeline);
    }

    const chapterFilter = document.getElementById('chapterFilter');
    if (chapterFilter) {
        chapterFilter.addEventListener('change', filterTimeline);
    }

    // 监听节点选择事件
    document.addEventListener('nodeSelected', handleNodeSelected);
}

/**
 * 处理文件上传
 */
async function handleUpload() {
    const file = fileInput.files[0];

    if (!file) {
        showStatus('请选择文件', 'error');
        return;
    }

    if (!file.name.endsWith('.txt')) {
        showStatus('目前只支持 TXT 格式', 'error');
        return;
    }

    try {
        uploadBtn.disabled = true;
        showStatus('正在上传...', 'info');

        // 上传文件
        const uploadResult = await apiClient.uploadFile(file);
        console.log('上传成功:', uploadResult);

        showStatus('上传成功，开始分析...', 'info');
        
        // 显示进度条
        progressContainer.style.display = 'block';
        updateProgress(0, '正在初始化...');

        // 启动异步分析
        const taskInfo = await apiClient.analyzeNovelAsync(uploadResult.filepath);
        console.log('分析任务已启动:', taskInfo);
        
        // 轮询任务状态
        const analysisResult = await pollTaskStatus(taskInfo.task_id);
        console.log('分析完成:', analysisResult);

        showStatus(`分析完成！发现 ${analysisResult.statistics.characters} 个人物，${analysisResult.statistics.events} 个事件`, 'success');

        // 重新加载小说列表
        await loadNovels();

        // 自动选择刚上传的小说
        currentNovelId = analysisResult.novel_id;
        novelSelect.value = currentNovelId;
        await loadNovelData(currentNovelId);

    } catch (error) {
        console.error('上传或分析失败:', error);
        showStatus(`错误: ${error.message}`, 'error');
    } finally {
        uploadBtn.disabled = false;
        // 延迟隐藏进度条
        setTimeout(() => {
            progressContainer.style.display = 'none';
            updateProgress(0, '');
        }, 3000);
    }
}

/**
 * 轮询任务状态
 */
async function pollTaskStatus(taskId) {
    return new Promise((resolve, reject) => {
        const interval = setInterval(async () => {
            try {
                const task = await apiClient.getTaskStatus(taskId);
                updateProgress(task.progress, task.message);

                if (task.status === 'completed') {
                    clearInterval(interval);
                    resolve(task.result);
                } else if (task.status === 'failed') {
                    clearInterval(interval);
                    reject(new Error(task.error || '分析失败'));
                }
            } catch (error) {
                clearInterval(interval);
                reject(error);
            }
        }, 1000); // 每秒轮询一次
    });
}

/**
 * 更新进度条
 */
function updateProgress(percent, message) {
    progressBar.style.width = `${percent}%`;
    progressText.textContent = `${percent}% - ${message}`;
}

/**
 * 加载小说列表
 */
async function loadNovels() {
    try {
        const novels = await apiClient.getNovels();
        console.log('小说列表:', novels);

        // 清空选择框
        novelSelect.innerHTML = '<option value="">选择小说...</option>';

        // 添加选项
        novels.forEach(novel => {
            const option = document.createElement('option');
            option.value = novel.id;
            option.textContent = `${novel.title} (${novel.chapters}章, ${novel.words}字)`;
            novelSelect.appendChild(option);
        });

    } catch (error) {
        console.error('加载小说列表失败:', error);
    }
}

/**
 * 处理小说选择
 */
async function handleNovelSelect(event) {
    const novelId = event.target.value;

    if (!novelId) {
        currentNovelId = null;
        clearAllData();
        return;
    }

    currentNovelId = novelId;
    await loadNovelData(novelId);
}

/**
 * 加载小说数据
 */
async function loadNovelData(novelId) {
    try {
        showStatus('正在加载数据...', 'info');

        // 并行加载所有数据
        const [characters, graphData, timeline, locations, emotions] = await Promise.all([
            apiClient.getCharacters(novelId),
            apiClient.getGraph(novelId),
            apiClient.getTimeline(novelId),
            apiClient.getLocations(novelId),
            apiClient.getEmotions(novelId)
        ]);

        console.log('数据加载完成');

        // 更新概览
        updateOverview({
            characters: characters.length,
            relations: graphData.edges.length,
            events: timeline.events.length,
            locations: locations.length
        });

        // 更新各个标签页
        updateCharactersTab(graphData, characters);
        updateTimelineTab(timeline);
        updateLocationsTab(locations);
        updateEmotionsTab(emotions);

        showStatus('数据加载完成', 'success');

    } catch (error) {
        console.error('加载数据失败:', error);
        showStatus(`加载失败: ${error.message}`, 'error');
    }
}

/**
 * 更新概览标签
 */
function updateOverview(stats) {
    document.getElementById('statChapters').textContent = stats.chapters || '-';
    document.getElementById('statWords').textContent = stats.words || '-';
    document.getElementById('statCharacters').textContent = stats.characters || 0;
    document.getElementById('statRelations').textContent = stats.relations || 0;
    document.getElementById('statEvents').textContent = stats.events || 0;
    document.getElementById('statLocations').textContent = stats.locations || 0;
}

/**
 * 更新人物关系标签
 */
function updateCharactersTab(graphData, characters) {
    // 更新图谱
    if (graphVisualizer) {
        graphVisualizer.update(graphData);
    }

    // 显示人物列表
    const detailPanel = document.getElementById('characterDetail');
    detailPanel.innerHTML = `
        <h4>人物列表 (${characters.length})</h4>
        <div class="character-list">
            ${characters.slice(0, 10).map(char => `
                <div class="character-item" style="padding: 10px; margin: 5px 0; background: #f8f9fa; border-radius: 6px; cursor: pointer;" data-name="${char.name}">
                    <strong>${char.name}</strong>
                    <div style="font-size: 0.9em; color: #7f8c8d; margin-top: 5px;">
                        重要度: ${(char.importance * 100).toFixed(1)}% |
                        出现: ${char.mention_count}次
                    </div>
                </div>
            `).join('')}
        </div>
        <p style="margin-top: 15px; color: #7f8c8d; font-size: 0.9em;">点击图谱节点或人物查看详情</p>
    `;

    // 绑定人物点击事件
    detailPanel.querySelectorAll('.character-item').forEach(item => {
        item.addEventListener('click', async () => {
            const name = item.dataset.name;
            await loadCharacterProfile(name);
        });
    });
}

/**
 * 更新时间线标签
 */
function updateTimelineTab(timelineData) {
    window.timelineData = timelineData; // 保存到全局以便筛选

    // 填充章节筛选器
    const chapterFilter = document.getElementById('chapterFilter');
    if (chapterFilter && timelineData.events.length > 0) {
        const chapters = [...new Set(timelineData.events.map(e => e.chapter))].sort((a, b) => a - b);
        chapterFilter.innerHTML = '<option value="all">全部章节</option>' +
            chapters.map(ch => `<option value="${ch}">第 ${ch} 章</option>`).join('');
    }

    renderTimeline(timelineData.events);
}

/**
 * 渲染时间线
 */
function renderTimeline(events) {
    const container = document.getElementById('timelineContainer');

    if (!events || events.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #7f8c8d;">暂无事件数据</p>';
        return;
    }

    const mainPlotIds = window.timelineData?.main_plot_events || [];

    container.innerHTML = events.map(event => {
        const isMainPlot = mainPlotIds.includes(event.id);
        return `
            <div class="timeline-event ${isMainPlot ? 'main-plot' : ''}">
                <h4>${event.description}</h4>
                <div class="event-meta">
                    <span>📖 第 ${event.chapter} 章</span>
                    <span>🔢 序号: ${event.sequence}</span>
                    <span>📊 重要度: ${(event.importance_score * 100).toFixed(0)}%</span>
                    <span>🎯 类型: ${event.event_type}</span>
                </div>
                ${event.participants && event.participants.length > 0 ? `
                    <div class="event-participants">
                        ${event.participants.map(p => `<span class="participant-tag">${p}</span>`).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');
}

/**
 * 筛选时间线
 */
function filterTimeline() {
    if (!window.timelineData) return;

    const showMainPlotOnly = document.getElementById('showMainPlotOnly').checked;
    const chapterFilter = document.getElementById('chapterFilter').value;
    const mainPlotIds = window.timelineData.main_plot_events || [];

    let filteredEvents = window.timelineData.events;

    // 筛选主线
    if (showMainPlotOnly) {
        filteredEvents = filteredEvents.filter(e => mainPlotIds.includes(e.id));
    }

    // 筛选章节
    if (chapterFilter !== 'all') {
        const chapter = parseInt(chapterFilter);
        filteredEvents = filteredEvents.filter(e => e.chapter === chapter);
    }

    renderTimeline(filteredEvents);
}

/**
 * 更新地点标签
 */
function updateLocationsTab(locations) {
    const container = document.getElementById('locationList');

    if (!locations || locations.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #7f8c8d;">暂无地点数据</p>';
        return;
    }

    container.innerHTML = locations.map(loc => `
        <div class="location-card">
            <h4>${loc.name}</h4>
            <span class="location-type">${loc.type}</span>
            <div class="location-meta">
                <span>重要度: ${(loc.importance * 100).toFixed(0)}%</span>
                <span>事件数: ${loc.event_count}</span>
            </div>
        </div>
    `).join('');
}

/**
 * 更新情感标签
 */
function updateEmotionsTab(emotionData) {
    // 渲染情感曲线图
    renderEmotionChart(emotionData.emotion_curve);

    // 显示情感统计
    const detailsContainer = document.getElementById('emotionDetails');
    if (emotionData.statistics) {
        const stats = emotionData.statistics;
        detailsContainer.innerHTML = `
            <div class="emotion-card">
                <h4>平均情感值</h4>
                <div class="emotion-value">${stats.average_sentiment.toFixed(2)}</div>
            </div>
            <div class="emotion-card">
                <h4>情感波动</h4>
                <div class="emotion-value">${stats.sentiment_variance.toFixed(2)}</div>
            </div>
            <div class="emotion-card">
                <h4>情感高峰</h4>
                <div class="emotion-value">${emotionData.emotional_peaks?.length || 0}</div>
            </div>
        `;
    }
}

/**
 * 渲染情感曲线图
 */
function renderEmotionChart(emotionCurve) {
    const canvas = document.getElementById('emotionCurveChart');
    const ctx = canvas.getContext('2d');

    // 销毁旧图表
    if (emotionChart) {
        emotionChart.destroy();
    }

    if (!emotionCurve || emotionCurve.length === 0) {
        return;
    }

    emotionChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: emotionCurve.map(point => `第${point.chapter}章`),
            datasets: [{
                label: '情感值',
                data: emotionCurve.map(point => point.sentiment),
                borderColor: '#4a90e2',
                backgroundColor: 'rgba(74, 144, 226, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                title: {
                    display: true,
                    text: '章节情感曲线'
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: '情感值'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: '章节'
                    }
                }
            }
        }
    });
}

/**
 * 处理节点选择
 */
async function handleNodeSelected(event) {
    const nodeData = event.detail;
    console.log('选中节点:', nodeData);

    if (currentNovelId && nodeData.label) {
        await loadCharacterProfile(nodeData.label);
    }
}

/**
 * 加载人物详细信息
 */
async function loadCharacterProfile(characterName) {
    if (!currentNovelId) return;

    try {
        const profile = await apiClient.getCharacterProfile(currentNovelId, characterName);
        console.log('人物详情:', profile);

        displayCharacterProfile(profile);

    } catch (error) {
        console.error('加载人物详情失败:', error);
    }
}

/**
 * 显示人物详细信息
 */
function displayCharacterProfile(profile) {
    const detailPanel = document.getElementById('characterDetail');

    const basic = profile.basic_info;
    const relations = profile.relations || [];

    detailPanel.innerHTML = `
        <div class="character-profile">
            <h3>${basic.name}</h3>

            <h4>基本信息</h4>
            <div class="info-item">
                <span class="info-label">重要度:</span>
                <span class="info-value">${(basic.importance * 100).toFixed(1)}%</span>
            </div>
            <div class="info-item">
                <span class="info-label">出现次数:</span>
                <span class="info-value">${basic.mention_count}</span>
            </div>
            <div class="info-item">
                <span class="info-label">首次出现:</span>
                <span class="info-value">第 ${basic.first_appearance} 章</span>
            </div>
            <div class="info-item">
                <span class="info-label">中心度:</span>
                <span class="info-value">${(basic.degree_centrality * 100).toFixed(1)}%</span>
            </div>

            <h4>人物关系 (${relations.length})</h4>
            ${relations.length > 0 ? relations.map(rel => {
                const otherPerson = rel.from === basic.name ? rel.to : rel.from;
                return `
                    <div class="relation-item">
                        <strong>${otherPerson}</strong>
                        <span class="relation-type">${rel.relationship_type}</span>
                        <div style="font-size: 0.85em; color: #7f8c8d; margin-top: 5px;">
                            强度: ${(rel.strength * 100).toFixed(0)}%
                        </div>
                    </div>
                `;
            }).join('') : '<p style="color: #7f8c8d;">暂无关系数据</p>'}
        </div>
    `;
}

/**
 * 切换标签
 */
function switchTab(tabName) {
    // 更新按钮状态
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.tab === tabName) {
            btn.classList.add('active');
        }
    });

    // 更新内容显示
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });

    const targetContent = document.getElementById(tabName);
    if (targetContent) {
        targetContent.classList.add('active');

        // 如果切换到人物关系标签，调整图谱大小
        if (tabName === 'characters' && graphVisualizer) {
            setTimeout(() => {
                graphVisualizer.fit();
            }, 100);
        }
    }
}

/**
 * 清空所有数据
 */
function clearAllData() {
    updateOverview({});
    document.getElementById('characterDetail').innerHTML = '<p>点击图谱中的节点查看详情</p>';
    document.getElementById('timelineContainer').innerHTML = '';
    document.getElementById('locationList').innerHTML = '';
    document.getElementById('emotionDetails').innerHTML = '';

    if (graphVisualizer) {
        graphVisualizer.destroy();
        graphVisualizer = new GraphVisualizer('cy');
    }

    if (emotionChart) {
        emotionChart.destroy();
        emotionChart = null;
    }
}

/**
 * 显示状态消息
 */
function showStatus(message, type = 'info') {
    uploadStatus.textContent = message;
    uploadStatus.className = `status-message ${type}`;

    // 3秒后自动清除成功消息
    if (type === 'success') {
        setTimeout(() => {
            uploadStatus.textContent = '';
            uploadStatus.className = 'status-message';
        }, 3000);
    }
}
