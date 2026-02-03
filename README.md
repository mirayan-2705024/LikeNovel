# 小说脉络分析系统 (Novel Analysis Agent)

基于Neo4j图数据库的智能小说分析系统，支持人物关系、情节时间线、世界观结构等多维度分析。

## 功能特性

- 📚 **多格式支持**: TXT、EPUB、PDF、在线网文
- 👥 **人物关系分析**: 自动识别人物及其关系网络
- ⏱️ **时间线构建**: 事件层级分析和主线贡献度计算
- 🌍 **世界观构建**: 支持修仙等级、宫斗官职等类型特定结构
- 💭 **情感分析**: 追踪人物情感变化和章节情感曲线
- 🔍 **多维度索引**: 从分析结果快速追溯到原文
- 🎨 **可视化展示**: Web界面交互式图谱展示

## 技术栈

- **后端**: Python 3.10+, Flask
- **数据库**: Neo4j 5.15
- **NLP**: jieba, SnowNLP
- **前端**: HTML/CSS/JavaScript, Cytoscape.js
- **部署**: Docker, Docker Compose

## 快速开始

### 1. 环境要求

- Python 3.10+
- Docker 和 Docker Compose
- Git

### 2. 安装步骤

```bash
# 克隆仓库
git clone <your-repo-url>
cd novelanalys

# 复制环境变量配置
cp .env.example .env

# 启动Neo4j数据库
docker-compose up -d

# 安装Python依赖
pip install -r requirements.txt

# 初始化数据库
python scripts/init_db.py

# 启动Flask服务
python backend/app.py
```

### 3. 访问系统

- Web界面: http://localhost:5000
- Neo4j浏览器: http://localhost:7474
  - 用户名: neo4j
  - 密码: password

## 项目结构

```
novelanalys/
├── backend/          # 后端代码
│   ├── analyzers/   # 分析器模块
│   ├── database/    # 数据库操作
│   ├── parsers/     # 文件解析器
│   └── api/         # API接口
├── frontend/         # 前端代码
├── data/            # 数据文件
├── tests/           # 测试代码
└── scripts/         # 工具脚本
```

## 使用示例

### 上传并分析小说

```python
from backend.parsers.txt_parser import TxtParser
from backend.analyzers.character_analyzer import CharacterAnalyzer

# 解析小说文件
parser = TxtParser()
novel_data = parser.parse('data/sample_novels/example.txt')

# 分析人物关系
analyzer = CharacterAnalyzer()
characters = analyzer.analyze(novel_data)
```

### 查询Neo4j图谱

```cypher
// 查询人物关系网络
MATCH (c:Character)-[r:KNOWS]->(other:Character)
RETURN c, r, other

// 查询主线事件
MATCH (e:Event)
WHERE e.contribution_score > 0.7
RETURN e.description, e.chapter
ORDER BY e.chapter
```

## 开发路线图

- [x] 项目初始化
- [ ] Milestone 1: 基础框架
- [ ] Milestone 2: 核心分析功能
- [ ] Milestone 3: 扩展分析功能
- [ ] Milestone 4: Web界面
- [ ] Milestone 5: 多格式支持
- [ ] Milestone 6: 优化和完善

## 贡献指南

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交Issue。
