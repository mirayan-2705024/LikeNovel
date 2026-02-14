/**
 * API 客户端 - 处理与后端的所有通信
 */

const API_BASE_URL = 'http://localhost:5000/api';

class APIClient {
    /**
     * 上传文件
     * @param {File} file - 要上传的文件
     * @returns {Promise<Object>} 上传结果
     */
    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || '上传失败');
        }

        return await response.json();
    }

    /**
     * 分析小说
     * @param {string} filepath - 文件路径
     * @returns {Promise<Object>} 分析结果
     */
    async analyzeNovel(filepath) {
        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ filepath })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || '分析失败');
        }

        return await response.json();
    }

    /**
     * 异步分析小说
     * @param {string} filepath - 文件路径
     * @returns {Promise<Object>} 任务信息 {message, task_id}
     */
    async analyzeNovelAsync(filepath) {
        const response = await fetch(`${API_BASE_URL}/analyze/async`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ filepath })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || '分析启动失败');
        }

        return await response.json();
    }

    /**
     * 获取任务状态
     * @param {string} taskId - 任务ID
     * @returns {Promise<Object>} 任务状态
     */
    async getTaskStatus(taskId) {
        const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`);

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || '获取任务状态失败');
        }

        return await response.json();
    }

    /**
     * 获取小说列表
     * @returns {Promise<Array>} 小说列表
     */
    async getNovels() {
        const response = await fetch(`${API_BASE_URL}/novels`);

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || '获取小说列表失败');
        }

        const data = await response.json();
        return data.novels;
    }

    /**
     * 获取人物列表
     * @param {string} novelId - 小说ID
     * @returns {Promise<Array>} 人物列表
     */
    async getCharacters(novelId) {
        const response = await fetch(`${API_BASE_URL}/novel/${novelId}/characters`);

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || '获取人物列表失败');
        }

        const data = await response.json();
        return data.characters;
    }

    /**
     * 获取关系图谱数据
     * @param {string} novelId - 小说ID
     * @returns {Promise<Object>} 图谱数据 {nodes, edges}
     */
    async getGraph(novelId) {
        const response = await fetch(`${API_BASE_URL}/novel/${novelId}/graph`);

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || '获取图谱数据失败');
        }

        return await response.json();
    }

    /**
     * 获取时间线数据
     * @param {string} novelId - 小说ID
     * @returns {Promise<Object>} 时间线数据
     */
    async getTimeline(novelId) {
        const response = await fetch(`${API_BASE_URL}/novel/${novelId}/timeline`);

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || '获取时间线失败');
        }

        return await response.json();
    }

    /**
     * 获取地点数据
     * @param {string} novelId - 小说ID
     * @returns {Promise<Array>} 地点列表
     */
    async getLocations(novelId) {
        const response = await fetch(`${API_BASE_URL}/novel/${novelId}/locations`);

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || '获取地点数据失败');
        }

        const data = await response.json();
        return data.locations;
    }

    /**
     * 获取情感数据
     * @param {string} novelId - 小说ID
     * @returns {Promise<Object>} 情感数据
     */
    async getEmotions(novelId) {
        const response = await fetch(`${API_BASE_URL}/novel/${novelId}/emotions`);

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || '获取情感数据失败');
        }

        return await response.json();
    }

    /**
     * 获取人物详细信息
     * @param {string} novelId - 小说ID
     * @param {string} characterName - 人物名称
     * @returns {Promise<Object>} 人物详细信息
     */
    async getCharacterProfile(novelId, characterName) {
        const encodedName = encodeURIComponent(characterName);
        const response = await fetch(`${API_BASE_URL}/character/${novelId}/${encodedName}`);

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || '获取人物信息失败');
        }

        return await response.json();
    }

    /**
     * 健康检查
     * @returns {Promise<Object>} 健康状态
     */
    async healthCheck() {
        const response = await fetch('http://localhost:5000/health');

        if (!response.ok) {
            throw new Error('服务不可用');
        }

        return await response.json();
    }
}

// 导出单例
const apiClient = new APIClient();
