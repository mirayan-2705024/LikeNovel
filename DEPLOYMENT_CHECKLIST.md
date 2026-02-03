# LikeNovel v0.4.0 - 部署检查清单

## ✅ 文件完整性检查

### 后端文件
- [x] `backend/app.py` - Flask 应用主入口
- [x] `backend/api/routes.py` - API 路由（10+ 端点）
- [x] `backend/analyzers/` - 7 个分析器
- [x] `backend/database/` - Neo4j 客户端
- [x] `backend/extractors/` - 实体提取器
- [x] `backend/parsers/` - TXT 解析器
- [x] `config/config.py` - 配置文件

### 前端文件
- [x] `frontend/index.html` - 主页面
- [x] `frontend/css/style.css` - 样式表（600+ 行）
- [x] `frontend/js/api-client.js` - API 客户端
- [x] `frontend/js/graph-visualizer.js` - 图谱可视化
- [x] `frontend/js/app.js` - 主应用逻辑（500+ 行）

### 配置文件
- [x] `docker-compose.yml` - Docker 配置
- [x] `requirements.txt` - Python 依赖
- [x] `.env.example` - 环境变量模板

### 启动脚本
- [x] `start.bat` - Windows 启动脚本
- [x] `stop.bat` - Windows 停止脚本

### 文档
- [x] `README.md` - 项目说明（已更新到 v0.4.0）
- [x] `USAGE.md` - 使用指南（全新）
- [x] `PROJECT_SUMMARY.md` - 项目总结（全新）

---

## 🚀 启动前检查

### 1. 环境要求
- [ ] Python 3.10+ 已安装
- [ ] Docker Desktop 已安装并启动
- [ ] Git 已安装（可选）

### 2. 依赖安装
```bash
# 检查 Python 版本
python --version

# 安装依赖
pip install -r requirements.txt
```

### 3. 环境配置
```bash
# 复制环境变量配置
cp .env.example .env

# 或手动创建 .env 文件，内容：
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
FLASK_ENV=development
FLASK_DEBUG=True
UPLOAD_FOLDER=data/novels
MAX_CONTENT_LENGTH=104857600
MIN_CHARACTER_MENTIONS=3
MIN_RELATION_STRENGTH=0.3
```

---

## 🎯 启动步骤

### 方式一：一键启动（推荐）
```bash
# Windows 用户
start.bat
```

### 方式二：手动启动
```bash
# 1. 启动 Neo4j
docker-compose up -d

# 2. 等待 10 秒让 Neo4j 就绪
# （或使用 docker logs 查看启动状态）

# 3. 启动 Flask
python backend/app.py

# 4. 打开浏览器
# http://localhost:5000
```

---

## ✅ 功能测试清单

### 1. 服务健康检查
- [ ] 访问 http://localhost:5000 能看到界面
- [ ] 访问 http://localhost:5000/health 返回健康状态
- [ ] 访问 http://localhost:7474 能打开 Neo4j 浏览器

### 2. 文件上传测试
- [ ] 点击"选择文件"能打开文件选择器
- [ ] 选择 TXT 文件后显示文件名
- [ ] 点击"上传并分析"开始上传
- [ ] 显示"正在上传..."状态
- [ ] 显示"上传成功，开始分析..."状态
- [ ] 分析完成后显示统计信息

### 3. 概览标签测试
- [ ] 6 个统计卡片显示正确数据
- [ ] 章节数、字数、人物数等数据正确

### 4. 人物关系标签测试
- [ ] 图谱正确渲染
- [ ] 节点大小反映重要性
- [ ] 点击节点显示详情
- [ ] 双击节点能居中
- [ ] 拖拽节点能移动
- [ ] 鼠标滚轮能缩放
- [ ] 右侧显示人物列表

### 5. 时间线标签测试
- [ ] 事件列表正确显示
- [ ] 主线事件有绿色标识
- [ ] "只显示主线事件"筛选有效
- [ ] 章节筛选有效
- [ ] 参与人物标签显示

### 6. 地点标签测试
- [ ] 地点卡片网格显示
- [ ] 地点类型标签显示
- [ ] 重要度和事件数正确

### 7. 情感标签测试
- [ ] 情感曲线图正确渲染
- [ ] 图表可以交互（悬停查看数值）
- [ ] 情感统计卡片显示数据

### 8. 小说切换测试
- [ ] 下拉菜单显示已分析小说
- [ ] 切换小说后数据正确更新
- [ ] 所有标签页数据同步更新

---

## 🐛 常见问题排查

### 问题 1: 无法访问 http://localhost:5000
**检查：**
```bash
# 检查 Flask 是否运行
# Windows: 查看是否有 Python 进程
tasklist | findstr python

# 检查端口是否被占用
netstat -ano | findstr :5000
```

### 问题 2: 上传失败
**检查：**
- 文件格式是否为 TXT
- 文件编码是否为 UTF-8 或 GBK
- 文件大小是否 < 100MB
- 浏览器控制台是否有错误

### 问题 3: 图谱不显示
**检查：**
- 浏览器控制台是否有 JavaScript 错误
- Cytoscape.js 是否加载成功
- 网络请求是否成功

### 问题 4: Neo4j 连接失败
**检查：**
```bash
# 检查 Neo4j 容器状态
docker ps

# 查看 Neo4j 日志
docker logs novelanalys-neo4j-1

# 重启 Neo4j
docker-compose restart
```

### 问题 5: 分析时间过长
**正常情况：**
- 短篇（< 10万字）：10-30秒
- 中篇（10-50万字）：30-120秒
- 长篇（> 50万字）：2-5分钟

**如果超时：**
- 检查 CPU 使用率
- 检查内存使用情况
- 尝试分章节上传

---

## 📊 性能基准测试

### 测试小说
使用 `data/sample_novels/example.txt` 进行测试

**预期结果：**
- 上传时间：< 1 秒
- 分析时间：10-30 秒
- 人物数：5-15 个
- 关系数：10-30 个
- 事件数：20-50 个
- 地点数：5-15 个

---

## 🔧 开发者检查

### API 端点测试
```bash
# 健康检查
curl http://localhost:5000/health

# 获取小说列表
curl http://localhost:5000/api/novels

# 获取人物列表（需要先上传小说）
curl http://localhost:5000/api/novel/{novel_id}/characters
```

### Neo4j 查询测试
访问 http://localhost:7474，执行：
```cypher
// 查看所有节点
MATCH (n) RETURN count(n)

// 查看所有关系
MATCH ()-[r]->() RETURN count(r)

// 查看人物节点
MATCH (c:Character) RETURN c LIMIT 10
```

---

## ✅ 部署完成确认

- [ ] 所有文件已创建
- [ ] 依赖已安装
- [ ] 服务能正常启动
- [ ] 界面能正常访问
- [ ] 文件上传功能正常
- [ ] 所有标签页功能正常
- [ ] 图谱可视化正常
- [ ] Neo4j 连接正常

---

## 🎉 部署成功！

如果所有检查项都通过，恭喜你！LikeNovel v0.4.0 已成功部署。

**下一步：**
1. 上传你的第一部小说
2. 探索各种分析功能
3. 查看 USAGE.md 了解更多用法
4. 遇到问题查看 README.md 或提交 Issue

**享受使用！** 📚✨
