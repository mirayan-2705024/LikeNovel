# LikeNovel - 小说脉络分析系统

基于Neo4j图数据库的智能小说分析系统，支持人物关系、情节时间线、地点场景、情感变化、状态追踪等多维度深度分析。

## ✨ 功能特性

### 核心功能（已实现）

- 📚 **文本解析**: 支持TXT格式，自动识别章节结构
- 👥 **人物分析**:
  - 自动提取人物及别名合并
  - 识别主要人物和次要人物
  - 计算人物重要性和网络中心度
  - 生成完整人物画像

- 🔗 **关系分析**:
  - 基于共现、模式匹配、对话的关系提取
  - 支持多种关系类型（亲属、朋友、师徒、恋人、敌人等）
  - 关系强度计算和网络密度分析
  - 社区检测和群组识别

- ⏱️ **时间线分析**:
  - 事件自动识别和提取
  - 事件层级结构（大事件和子事件）
  - 事件重要性评分
  - 主线贡献度计算
  - 因果关系分析
  - 时间标记提取（绝对和相对时间）

- 🗺️ **地点分析**:
  - 地点重要性计算
  - 场景转换追踪
  - 人物-地点映射和访问统计
  - 地点类型分类
  - 人物地点轨迹分析

- 💭 **情感分析**:
  - 章节级情感评分
  - 人物情感追踪
  - 人物间情感关系提取
  - 情感曲线构建
  - 情感高潮和低谷识别
  - 支持6种情感类型

- 📊 **状态追踪**:
  - 多维度状态追踪（健康、情绪、能力、社会地位）
  - 状态变化检测
  - 状态与事件关联
  - 状态演化时间线
  - 状态进展分析

- 🔍 **图数据库存储**:
  - 完整的Neo4j图模型
  - 10+种节点类型
  - 20+种关系类型
  - 支持复杂Cypher查询

### 计划中功能

- 🌍 **世界观构建**: 修仙等级、宫斗官职等类型特定结构
- 📖 **多格式支持**: EPUB、PDF、在线网文
- 🎨 **Web可视化**: 交互式图谱展示界面
- 🔍 **多维度索引**: 从分析结果追溯到原文

## 技术栈

- **后端**: Python 3.10+, Flask
- **数据库**: Neo4j 5.15
- **NLP**: jieba, SnowNLP
- **前端**: HTML/CSS/JavaScript, Cytoscape.js
- **部署**: Docker, Docker Compose

## 🚀 快速开始

### 1. 环境要求

- Python 3.10+
- Docker 和 Docker Compose
- Git

### 2. 安装步骤

```bash
# 克隆仓库
git clone https://github.com/mirayan-2705024/LikeNovel.git
cd novelanalys

# 复制环境变量配置
cp .env.example .env

# 启动Neo4j数据库
docker-compose up -d

# 安装Python依赖
pip install -r requirements.txt

# 初始化数据库（可选）
python scripts/init_db.py
```

### 3. 运行分析

```bash
# 运行完整分析演示（推荐）
python scripts/milestone3_demo.py

# 或运行基础演示
python scripts/demo_analysis.py

# 或运行Milestone 2演示
python scripts/full_analysis_demo.py
```

### 4. 访问系统

- Neo4j浏览器: http://localhost:7474
  - 用户名: neo4j
  - 密码: password
- Web界面: 开发中（Milestone 4）

## 📂 项目结构

```
novelanalys/
├── backend/                    # 后端代码
│   ├── analyzers/             # 分析器模块
│   │   ├── text_processor.py        # 文本处理（分词、分句）
│   │   ├── character_analyzer.py    # 人物关系分析
│   │   ├── timeline_analyzer.py     # 时间线分析
│   │   ├── event_analyzer.py        # 事件分析
│   │   ├── location_analyzer.py     # 地点分析
│   │   ├── emotion_analyzer.py      # 情感分析
│   │   └── state_tracker.py         # 状态追踪
│   ├── database/              # 数据库操作
│   │   ├── neo4j_client.py          # Neo4j客户端
│   │   └── graph_schema.py          # 图模型定义
│   ├── extractors/            # 实体提取
│   │   ├── entity_extractor.py      # 实体提取器
│   │   └── relation_extractor.py    # 关系提取器
│   ├── parsers/               # 文件解析器
│   │   └── txt_parser.py            # TXT解析器
│   ├── api/                   # API接口（开发中）
│   └── utils/                 # 工具函数
├── frontend/                   # 前端代码（开发中）
├── data/                      # 数据文件
│   ├── novels/                      # 上传的小说
│   ├── sample_novels/               # 示例小说
│   ├── stopwords.txt                # 停用词表
│   └── dictionaries/                # 词典（计划中）
├── scripts/                   # 工具脚本
│   ├── init_db.py                   # 数据库初始化
│   ├── demo_analysis.py             # 基础演示
│   ├── full_analysis_demo.py        # Milestone 2演示
│   └── milestone3_demo.py           # 完整演示
├── tests/                     # 测试代码
├── config/                    # 配置文件
│   └── config.py                    # 应用配置
├── docker-compose.yml         # Docker配置
├── requirements.txt           # Python依赖
└── README.md                  # 项目文档
```

## 📖 使用示例

### 基础使用

```python
from backend.parsers.txt_parser import TxtParser
from backend.extractors.entity_extractor import EntityExtractor
from backend.analyzers.character_analyzer import CharacterAnalyzer
from backend.analyzers.timeline_analyzer import TimelineAnalyzer

# 1. 解析小说
parser = TxtParser()
novel_data = parser.parse('data/sample_novels/example.txt')

# 2. 提取实体
extractor = EntityExtractor(min_mentions=2)
entities = extractor.extract_entities_from_novel(novel_data)

# 3. 分析人物关系
char_analyzer = CharacterAnalyzer()
char_analysis = char_analyzer.analyze(
    novel_data['chapters'],
    entities['characters']
)

# 4. 分析时间线
timeline_analyzer = TimelineAnalyzer()
timeline_analysis = timeline_analyzer.analyze(
    novel_data['chapters'],
    char_analysis['characters'],
    char_analysis['relations']
)

# 5. 查看结果
print(f"主要人物: {len(char_analysis['main_characters'])}")
print(f"关系数量: {len(char_analysis['relations'])}")
print(f"事件数量: {len(timeline_analysis['events'])}")
print(f"主线事件: {len(timeline_analysis['main_plot_events'])}")
```

### 完整分析（包含地点、情感、状态）

```python
from backend.analyzers.location_analyzer import LocationAnalyzer
from backend.analyzers.emotion_analyzer import EmotionAnalyzer
from backend.analyzers.state_tracker import StateTracker

# 地点分析
location_analyzer = LocationAnalyzer()
location_analysis = location_analyzer.analyze(
    novel_data['chapters'],
    entities['locations'],
    char_analysis['characters'],
    timeline_analysis['events']
)

# 情感分析
emotion_analyzer = EmotionAnalyzer()
emotion_analysis = emotion_analyzer.analyze(
    novel_data['chapters'],
    char_analysis['characters'],
    timeline_analysis['events']
)

# 状态追踪
state_tracker = StateTracker()
state_analysis = state_tracker.analyze(
    novel_data['chapters'],
    char_analysis['characters'],
    timeline_analysis['events']
)
```

### Neo4j查询示例

```cypher
// 查询人物关系网络
MATCH (c1:Character)-[r:KNOWS]->(c2:Character)
RETURN c1, r, c2

// 查询主线事件
MATCH (e:Event)
WHERE e.contribution_score > 0.7
RETURN e.description, e.chapter, e.contribution_score
ORDER BY e.chapter

// 查询事件时间线
MATCH (e1:Event)-[r:NEXT]->(e2:Event)
RETURN e1, r, e2
LIMIT 20

// 查询人物参与的事件
MATCH (c:Character {name: '张三'})-[:PARTICIPATES_IN]->(e:Event)
RETURN e.description, e.chapter, e.importance_score
ORDER BY e.chapter

// 查询人物情感关系
MATCH (c1:Character)-[r:EMOTION_TOWARDS]->(c2:Character)
RETURN c1.name, r.emotion_type, r.intensity, c2.name

// 查询地点信息
MATCH (l:Location)
RETURN l.name, l.type, l.event_count, l.importance
ORDER BY l.importance DESC

// 查询人物状态变化
MATCH (s:State {character_name: '张三'})
RETURN s.state_type, s.value, s.chapter
ORDER BY s.chapter
```

## 🗓️ 开发路线图

### 已完成

- [x] **Milestone 1: 基础框架** ✅
  - [x] 项目结构和配置
  - [x] Neo4j数据库集成
  - [x] TXT文件解析器
  - [x] 基础文本处理（分词、分句、词性标注）
  - [x] 实体提取（人物、地点）

- [x] **Milestone 2: 核心分析功能** ✅
  - [x] 关系提取（共现、模式、对话）
  - [x] 人物关系网络分析
  - [x] 事件识别和分析
  - [x] 时间线构建
  - [x] 事件层级和因果关系
  - [x] 主线贡献度计算

- [x] **Milestone 3: 扩展分析功能** ✅
  - [x] 地点分析和场景转换
  - [x] 情感分析和情感曲线
  - [x] 状态追踪和变化检测
  - [x] 完整人物画像生成

### 进行中

- [ ] **Milestone 4: Web界面** 🚧
  - [ ] Flask后端API
  - [ ] 前端界面设计
  - [ ] 图谱可视化（Cytoscape.js）
  - [ ] 交互式查询界面

### 计划中

- [ ] **Milestone 3.5: 小说特定结构** 📋
  - [ ] 小说类型识别
  - [ ] 修仙等级体系提取
  - [ ] 宫斗官职体系
  - [ ] 世界观构建（门派、势力）
  - [ ] 物品和技能系统

- [ ] **Milestone 5: 多格式支持** 📋
  - [ ] EPUB解析器
  - [ ] PDF解析器
  - [ ] 在线网文爬虫
  - [ ] 格式自动识别

- [ ] **Milestone 6: 优化和完善** 📋
  - [ ] 性能优化（缓存、异步）
  - [ ] 多维度索引系统
  - [ ] 测试覆盖
  - [ ] 文档完善

## 📊 当前功能统计

- ✅ **10+** 种节点类型（Character, Event, Location, State等）
- ✅ **20+** 种关系类型（KNOWS, PARTICIPATES_IN, EMOTION_TOWARDS等）
- ✅ **7** 个核心分析器
- ✅ **3** 个演示脚本
- ✅ **完整的** Neo4j图数据库集成
- ✅ **多维度** 分析能力（人物、事件、地点、情感、状态）

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发指南

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

### 代码规范

- 遵循PEP 8 Python代码规范
- 添加必要的文档字符串
- 编写单元测试
- 提交前运行测试

## 📄 许可证

MIT License

## 📧 联系方式

- GitHub Issues: https://github.com/mirayan-2705024/LikeNovel/issues
- 项目主页: https://github.com/mirayan-2705024/LikeNovel

## 🙏 致谢

- [Neo4j](https://neo4j.com/) - 图数据库
- [jieba](https://github.com/fxsjy/jieba) - 中文分词
- [SnowNLP](https://github.com/isnowfy/snownlp) - 中文情感分析

## 📝 更新日志

### v0.3.0 (2024-02-03)
- ✅ 完成Milestone 3：扩展分析功能
- ✨ 新增地点分析器
- ✨ 新增情感分析器
- ✨ 新增状态追踪器
- 🎨 完整人物画像生成

### v0.2.0 (2024-02-03)
- ✅ 完成Milestone 2：核心分析功能
- ✨ 新增关系提取器
- ✨ 新增人物关系分析
- ✨ 新增事件和时间线分析
- 🎨 主线贡献度计算

### v0.1.0 (2024-02-03)
- ✅ 完成Milestone 1：基础框架
- 🎉 项目初始化
- ✨ Neo4j数据库集成
- ✨ TXT文件解析
- ✨ 基础实体提取

---

⭐ 如果这个项目对你有帮助，请给个Star！
