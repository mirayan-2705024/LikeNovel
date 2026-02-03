# LikeNovel API 文档

## 📡 API 概览

LikeNovel 提供 RESTful API 用于小说分析和数据查询。

**Base URL**: `http://localhost:5000`

**API Prefix**: `/api`

---

## 🔐 认证

当前版本无需认证（开发环境）。

---

## 📋 端点列表

### 1. 健康检查

#### `GET /health`

检查服务健康状态。

**请求示例：**
```bash
curl http://localhost:5000/health
```

**响应示例：**
```json
{
  "status": "healthy",
  "version": "0.4.0",
  "service": "LikeNovel Analysis System"
}
```

---

### 2. 上传文件

#### `POST /api/upload`

上传小说文件到服务器。

**请求参数：**
- `file` (multipart/form-data): 小说文件（TXT 格式）

**请求示例：**
```bash
curl -X POST \
  http://localhost:5000/api/upload \
  -F "file=@/path/to/novel.txt"
```

**响应示例：**
```json
{
  "message": "File uploaded successfully",
  "filename": "novel.txt",
  "filepath": "D:\\novelanalys\\data\\novels\\novel.txt"
}
```

**错误响应：**
```json
{
  "error": "No file provided"
}
```

**状态码：**
- `200`: 上传成功
- `400`: 请求错误（无文件、文件类型不支持等）
- `500`: 服务器错误

---

### 3. 分析小说

#### `POST /api/analyze`

分析上传的小说文件。

**请求参数：**
```json
{
  "filepath": "D:\\novelanalys\\data\\novels\\novel.txt"
}
```

**请求示例：**
```bash
curl -X POST \
  http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"filepath": "D:\\novelanalys\\data\\novels\\novel.txt"}'
```

**响应示例：**
```json
{
  "message": "Analysis completed",
  "novel_id": "novel",
  "statistics": {
    "chapters": 10,
    "words": 50000,
    "characters": 15,
    "relations": 25,
    "events": 40,
    "locations": 8
  }
}
```

**错误响应：**
```json
{
  "error": "File not found"
}
```

**状态码：**
- `200`: 分析成功
- `404`: 文件不存在
- `500`: 分析失败

**注意：**
- 分析时间取决于小说长度（10秒 - 5分钟）
- 结果会缓存在内存中

---

### 4. 获取小说列表

#### `GET /api/novels`

获取已分析的小说列表。

**请求示例：**
```bash
curl http://localhost:5000/api/novels
```

**响应示例：**
```json
{
  "novels": [
    {
      "id": "novel1",
      "title": "示例小说",
      "author": "作者名",
      "chapters": 10,
      "words": 50000
    },
    {
      "id": "novel2",
      "title": "另一部小说",
      "author": "未知",
      "chapters": 20,
      "words": 100000
    }
  ]
}
```

**状态码：**
- `200`: 成功
- `500`: 服务器错误

---

### 5. 获取人物列表

#### `GET /api/novel/{novel_id}/characters`

获取指定小说的人物列表。

**路径参数：**
- `novel_id`: 小说 ID

**请求示例：**
```bash
curl http://localhost:5000/api/novel/example/characters
```

**响应示例：**
```json
{
  "characters": [
    {
      "id": "char_1",
      "name": "张三",
      "importance": 0.95,
      "mention_count": 150,
      "first_appearance": 1,
      "degree_centrality": 0.85
    },
    {
      "id": "char_2",
      "name": "李四",
      "importance": 0.75,
      "mention_count": 80,
      "first_appearance": 2,
      "degree_centrality": 0.60
    }
  ]
}
```

**状态码：**
- `200`: 成功
- `404`: 小说不存在
- `500`: 服务器错误

---

### 6. 获取关系图谱

#### `GET /api/novel/{novel_id}/graph`

获取人物关系图谱数据（用于可视化）。

**路径参数：**
- `novel_id`: 小说 ID

**请求示例：**
```bash
curl http://localhost:5000/api/novel/example/graph
```

**响应示例：**
```json
{
  "nodes": [
    {
      "id": "char_1",
      "label": "张三",
      "importance": 0.95,
      "type": "main"
    },
    {
      "id": "char_2",
      "label": "李四",
      "importance": 0.75,
      "type": "supporting"
    }
  ],
  "edges": [
    {
      "id": "edge_0",
      "source": "char_1",
      "target": "char_2",
      "label": "朋友",
      "strength": 0.8
    }
  ]
}
```

**节点类型：**
- `main`: 主要人物
- `supporting`: 次要人物

**状态码：**
- `200`: 成功
- `404`: 小说不存在
- `500`: 服务器错误

---

### 7. 获取时间线

#### `GET /api/novel/{novel_id}/timeline`

获取事件时间线数据。

**路径参数：**
- `novel_id`: 小说 ID

**请求示例：**
```bash
curl http://localhost:5000/api/novel/example/timeline
```

**响应示例：**
```json
{
  "events": [
    {
      "id": "event_1",
      "description": "张三遇到李四",
      "chapter": 1,
      "sequence": 1,
      "event_type": "相遇",
      "importance_score": 0.85,
      "contribution_score": 0.90,
      "participants": ["张三", "李四"]
    }
  ],
  "main_plot_events": ["event_1", "event_5", "event_10"]
}
```

**事件类型：**
- 相遇、冲突、合作、分离、转折等

**状态码：**
- `200`: 成功
- `404`: 小说不存在
- `500`: 服务器错误

---

### 8. 获取地点列表

#### `GET /api/novel/{novel_id}/locations`

获取地点分析数据。

**路径参数：**
- `novel_id`: 小说 ID

**请求示例：**
```bash
curl http://localhost:5000/api/novel/example/locations
```

**响应示例：**
```json
{
  "locations": [
    {
      "id": "loc_1",
      "name": "京城",
      "type": "城市",
      "importance": 0.90,
      "event_count": 25
    },
    {
      "id": "loc_2",
      "name": "天山",
      "type": "山脉",
      "importance": 0.70,
      "event_count": 15
    }
  ]
}
```

**地点类型：**
- 城市、山脉、建筑、房间、其他

**状态码：**
- `200`: 成功
- `404`: 小说不存在
- `500`: 服务器错误

---

### 9. 获取情感数据

#### `GET /api/novel/{novel_id}/emotions`

获取情感分析数据。

**路径参数：**
- `novel_id`: 小说 ID

**请求示例：**
```bash
curl http://localhost:5000/api/novel/example/emotions
```

**响应示例：**
```json
{
  "chapter_emotions": [
    {
      "chapter": 1,
      "sentiment": 0.65,
      "emotions": {
        "joy": 0.7,
        "sadness": 0.1,
        "anger": 0.05,
        "fear": 0.05,
        "surprise": 0.05,
        "disgust": 0.05
      }
    }
  ],
  "emotion_curve": [
    {
      "chapter": 1,
      "sentiment": 0.65
    },
    {
      "chapter": 2,
      "sentiment": 0.45
    }
  ],
  "emotional_peaks": [
    {
      "chapter": 5,
      "sentiment": 0.95,
      "type": "high"
    }
  ],
  "statistics": {
    "average_sentiment": 0.55,
    "sentiment_variance": 0.12,
    "positive_chapters": 7,
    "negative_chapters": 3
  }
}
```

**情感值范围：**
- `-1.0` 到 `1.0`
- 正值：积极情感
- 负值：消极情感

**状态码：**
- `200`: 成功
- `404`: 小说不存在
- `500`: 服务器错误

---

### 10. 获取人物详情

#### `GET /api/character/{novel_id}/{character_name}`

获取指定人物的详细信息。

**路径参数：**
- `novel_id`: 小说 ID
- `character_name`: 人物名称（需要 URL 编码）

**请求示例：**
```bash
curl http://localhost:5000/api/character/example/%E5%BC%A0%E4%B8%89
```

**响应示例：**
```json
{
  "basic_info": {
    "id": "char_1",
    "name": "张三",
    "importance": 0.95,
    "mention_count": 150,
    "first_appearance": 1,
    "degree_centrality": 0.85
  },
  "relations": [
    {
      "from": "张三",
      "to": "李四",
      "relationship_type": "朋友",
      "strength": 0.8
    }
  ],
  "locations": [
    {
      "location": "京城",
      "visit_count": 20,
      "chapters": [1, 2, 3, 5, 8]
    }
  ],
  "emotions": [
    {
      "chapter": 1,
      "sentiment": 0.7,
      "dominant_emotion": "joy"
    }
  ],
  "states": [
    {
      "chapter": 1,
      "state_type": "health",
      "value": 0.9
    }
  ]
}
```

**状态码：**
- `200`: 成功
- `404`: 小说或人物不存在
- `500`: 服务器错误

---

## 📊 数据模型

### Character（人物）
```typescript
{
  id: string,              // 人物 ID
  name: string,            // 人物名称
  importance: number,      // 重要性 (0-1)
  mention_count: number,   // 出现次数
  first_appearance: number,// 首次出现章节
  degree_centrality: number// 网络中心度 (0-1)
}
```

### Relation（关系）
```typescript
{
  from: string,           // 源人物
  to: string,             // 目标人物
  relationship_type: string, // 关系类型
  strength: number        // 关系强度 (0-1)
}
```

### Event（事件）
```typescript
{
  id: string,             // 事件 ID
  description: string,    // 事件描述
  chapter: number,        // 所在章节
  sequence: number,       // 序号
  event_type: string,     // 事件类型
  importance_score: number,    // 重要性 (0-1)
  contribution_score: number,  // 主线贡献度 (0-1)
  participants: string[]  // 参与人物
}
```

### Location（地点）
```typescript
{
  id: string,             // 地点 ID
  name: string,           // 地点名称
  type: string,           // 地点类型
  importance: number,     // 重要性 (0-1)
  event_count: number     // 事件数量
}
```

---

## 🔧 错误处理

### 错误响应格式
```json
{
  "error": "错误描述"
}
```

### 常见错误码
- `400 Bad Request`: 请求参数错误
- `404 Not Found`: 资源不存在
- `500 Internal Server Error`: 服务器内部错误

---

## 💡 使用示例

### JavaScript (Fetch API)
```javascript
// 上传文件
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const uploadResponse = await fetch('http://localhost:5000/api/upload', {
  method: 'POST',
  body: formData
});
const uploadData = await uploadResponse.json();

// 分析小说
const analyzeResponse = await fetch('http://localhost:5000/api/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    filepath: uploadData.filepath
  })
});
const analyzeData = await analyzeResponse.json();

// 获取人物列表
const charactersResponse = await fetch(
  `http://localhost:5000/api/novel/${analyzeData.novel_id}/characters`
);
const charactersData = await charactersResponse.json();
```

### Python (requests)
```python
import requests

# 上传文件
with open('novel.txt', 'rb') as f:
    files = {'file': f}
    upload_response = requests.post(
        'http://localhost:5000/api/upload',
        files=files
    )
    upload_data = upload_response.json()

# 分析小说
analyze_response = requests.post(
    'http://localhost:5000/api/analyze',
    json={'filepath': upload_data['filepath']}
)
analyze_data = analyze_response.json()

# 获取人物列表
characters_response = requests.get(
    f"http://localhost:5000/api/novel/{analyze_data['novel_id']}/characters"
)
characters_data = characters_response.json()
```

### cURL
```bash
# 完整工作流
# 1. 上传
curl -X POST http://localhost:5000/api/upload \
  -F "file=@novel.txt"

# 2. 分析
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"filepath": "D:\\novelanalys\\data\\novels\\novel.txt"}'

# 3. 获取数据
curl http://localhost:5000/api/novel/novel/characters
curl http://localhost:5000/api/novel/novel/graph
curl http://localhost:5000/api/novel/novel/timeline
```

---

## 📝 注意事项

1. **文件格式**: 目前只支持 TXT 格式
2. **文件大小**: 建议 < 100MB
3. **编码**: UTF-8 或 GBK
4. **缓存**: 分析结果缓存在内存中，重启后清空
5. **并发**: 当前版本不支持并发分析
6. **超时**: 大文件分析可能需要几分钟

---

## 🔄 版本历史

### v0.4.0 (2026-02-03)
- ✅ 完整的 RESTful API
- ✅ 10+ 个端点
- ✅ 完整的错误处理

---

## 📧 支持

遇到问题？
- GitHub Issues: https://github.com/mirayan-2705024/LikeNovel/issues
- 项目主页: https://github.com/mirayan-2705024/LikeNovel
