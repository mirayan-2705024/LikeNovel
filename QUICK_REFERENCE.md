# LikeNovel 快速参考卡片

## 🚀 快速启动

```bash
# Windows 用户
start.bat

# 手动启动
docker-compose up -d
python backend/app.py
```

**访问地址**: http://localhost:5000

---

## 📋 主要功能

| 功能 | 说明 |
|------|------|
| 📤 文件上传 | 支持 TXT 格式小说 |
| 📊 概览 | 章节、字数、人物、关系等统计 |
| 👥 人物关系 | 交互式关系图谱 + 人物详情 |
| ⏱️ 时间线 | 事件列表 + 主线筛选 |
| 🗺️ 地点 | 地点分析 + 重要度排序 |
| 💭 情感 | 情感曲线 + 统计数据 |

---

## 🎯 使用流程

1. **启动服务** → `start.bat`
2. **打开浏览器** → http://localhost:5000
3. **上传小说** → 选择 TXT 文件
4. **等待分析** → 10秒 - 5分钟
5. **查看结果** → 5 个标签页

---

## 🔧 常用命令

```bash
# 启动服务
start.bat

# 停止服务
stop.bat

# 查看 Neo4j
http://localhost:7474
用户名: neo4j
密码: password

# 健康检查
curl http://localhost:5000/health
```

---

## 📊 API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/api/upload` | POST | 上传文件 |
| `/api/analyze` | POST | 分析小说 |
| `/api/novels` | GET | 小说列表 |
| `/api/novel/{id}/characters` | GET | 人物列表 |
| `/api/novel/{id}/graph` | GET | 关系图谱 |
| `/api/novel/{id}/timeline` | GET | 时间线 |
| `/api/novel/{id}/locations` | GET | 地点列表 |
| `/api/novel/{id}/emotions` | GET | 情感数据 |

---

## 🎨 图谱操作

| 操作 | 说明 |
|------|------|
| 点击节点 | 查看人物详情 |
| 双击节点 | 居中显示 |
| 拖拽节点 | 调整位置 |
| 滚轮 | 缩放图谱 |
| 拖拽空白 | 移动视图 |

---

## 📁 文件结构

```
novelanalys/
├── backend/          # 后端代码
│   ├── analyzers/   # 7 个分析器
│   ├── api/         # API 路由
│   └── app.py       # Flask 主入口
├── frontend/         # 前端代码
│   ├── css/         # 样式
│   ├── js/          # JavaScript
│   └── index.html   # 主页面
├── data/            # 数据文件
├── scripts/         # 工具脚本
├── start.bat        # 启动脚本
└── stop.bat         # 停止脚本
```

---

## 🐛 故障排查

| 问题 | 解决方法 |
|------|----------|
| 无法访问 5000 端口 | 检查 Flask 是否运行 |
| 上传失败 | 检查文件格式（TXT）和编码（UTF-8） |
| 图谱不显示 | 检查浏览器控制台错误 |
| Neo4j 连接失败 | `docker-compose restart` |
| 分析时间过长 | 正常现象，大文件需要 2-5 分钟 |

---

## 📚 文档

| 文档 | 说明 |
|------|------|
| `README.md` | 项目说明 |
| `USAGE.md` | 使用指南 |
| `API_DOCUMENTATION.md` | API 文档 |
| `DEPLOYMENT_CHECKLIST.md` | 部署清单 |
| `PROJECT_SUMMARY.md` | 项目总结 |

---

## 💡 提示

- 📝 使用 UTF-8 编码的 TXT 文件
- 📏 文件大小建议 < 10MB
- ⏱️ 短篇 10-30秒，长篇 2-5分钟
- 🌐 推荐使用 Chrome 或 Edge 浏览器
- 💾 重启后数据清空，需重新上传

---

## 🎯 性能参考

| 小说长度 | 分析时间 | 人物数 | 关系数 |
|----------|----------|--------|--------|
| < 10万字 | 10-30秒 | 5-15 | 10-30 |
| 10-50万字 | 30-120秒 | 15-50 | 30-100 |
| > 50万字 | 2-5分钟 | 50+ | 100+ |

---

## 📞 支持

- **GitHub**: https://github.com/mirayan-2705024/LikeNovel
- **Issues**: https://github.com/mirayan-2705024/LikeNovel/issues

---

## 🎉 版本信息

**当前版本**: v0.4.0
**发布日期**: 2026-02-03
**许可证**: MIT

---

**快速开始**: `start.bat` → http://localhost:5000 → 上传小说 → 开始分析！
