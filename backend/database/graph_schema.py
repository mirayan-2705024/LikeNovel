"""
图数据库模型定义
定义Neo4j图数据库的节点和关系结构
"""
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class GraphSchema:
    """图数据库模型定义类"""

    @staticmethod
    def create_constraints(client) -> None:
        """
        创建唯一性约束

        Args:
            client: Neo4jClient实例
        """
        constraints = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Character) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (e:Event) REQUIRE e.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (l:Location) REQUIRE l.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (ch:Chapter) REQUIRE ch.number IS UNIQUE",
        ]

        for constraint in constraints:
            try:
                client.execute_write(constraint)
                logger.info(f"Created constraint: {constraint}")
            except Exception as e:
                logger.warning(f"Constraint creation failed or already exists: {e}")

    @staticmethod
    def initialize_schema(client) -> None:
        """
        初始化数据库模式

        Args:
            client: Neo4jClient实例
        """
        logger.info("Initializing database schema...")

        # 创建约束
        GraphSchema.create_constraints(client)

        # 创建索引
        client.create_indexes()

        logger.info("Database schema initialized successfully")

    @staticmethod
    def get_node_properties() -> Dict[str, List[str]]:
        """
        获取各类节点的属性定义

        Returns:
            节点类型到属性列表的映射
        """
        return {
            "Character": [
                "id",           # 唯一标识
                "name",         # 姓名
                "gender",       # 性别
                "description",  # 描述
                "first_appearance",  # 首次出现章节
                "importance",   # 重要性分数
                "mention_count"  # 提及次数
            ],
            "Event": [
                "id",           # 唯一标识
                "description",  # 事件描述
                "chapter",      # 所属章节
                "sequence",     # 章节内序号
                "timestamp",    # 时间戳
                "event_type",   # 事件类型 (major/minor)
                "importance_score",  # 重要性分数
                "contribution_score"  # 主线贡献度
            ],
            "SubEvent": [
                "id",           # 唯一标识
                "description",  # 子事件描述
                "sequence",     # 序号
                "duration",     # 持续时间
                "contribution_score"  # 贡献度
            ],
            "Location": [
                "id",           # 唯一标识
                "name",         # 地点名称
                "description",  # 描述
                "type",         # 类型 (indoor/outdoor/etc)
                "event_count"   # 发生事件数量
            ],
            "Chapter": [
                "number",       # 章节号（唯一）
                "title",        # 标题
                "summary",      # 摘要
                "word_count"    # 字数
            ],
            "State": [
                "id",           # 唯一标识
                "character_name",  # 人物名称
                "state_type",   # 状态类型
                "value",        # 状态值
                "chapter",      # 章节
                "description"   # 描述
            ],
            "WorldElement": [
                "id",           # 唯一标识
                "name",         # 名称
                "type",         # 类型 (种族/门派/组织/国家/势力)
                "description",  # 描述
                "properties"    # 其他属性（JSON）
            ],
            "Level": [
                "id",           # 唯一标识
                "name",         # 等级名称
                "rank",         # 等级排序
                "system_type",  # 体系类型 (修仙/武功/魔法/官职等)
                "description",  # 描述
                "requirements"  # 要求
            ],
            "TextSegment": [
                "id",           # 唯一标识
                "novel_id",     # 小说ID
                "chapter",      # 章节
                "paragraph",    # 段落号
                "start_pos",    # 起始位置
                "end_pos",      # 结束位置
                "content",      # 文本内容
                "segment_type"  # 片段类型
            ]
        }

    @staticmethod
    def get_relationship_types() -> Dict[str, Dict]:
        """
        获取关系类型定义

        Returns:
            关系类型到属性定义的映射
        """
        return {
            "KNOWS": {
                "description": "人物之间的认识关系",
                "properties": [
                    "relationship_type",  # 关系类型 (朋友/敌人/亲属/恋人等)
                    "strength",          # 关系强度
                    "first_met_chapter"  # 首次相遇章节
                ]
            },
            "PARTICIPATES_IN": {
                "description": "人物参与事件",
                "properties": [
                    "role"  # 角色 (主角/配角/旁观者)
                ]
            },
            "OCCURS_AT": {
                "description": "事件发生在地点",
                "properties": [
                    "duration"  # 持续时间
                ]
            },
            "NEXT": {
                "description": "事件时间顺序",
                "properties": [
                    "time_gap"  # 时间间隔
                ]
            },
            "BELONGS_TO": {
                "description": "归属关系",
                "properties": [
                    "role",         # 角色
                    "join_chapter"  # 加入章节
                ]
            },
            "HAS_STATE": {
                "description": "人物拥有状态",
                "properties": [
                    "chapter",   # 章节
                    "intensity"  # 强度
                ]
            },
            "EMOTION_TOWARDS": {
                "description": "人物对人物的情感",
                "properties": [
                    "emotion_type",  # 情感类型
                    "intensity",     # 强度
                    "chapter"        # 章节
                ]
            },
            "CONTAINS": {
                "description": "事件包含子事件",
                "properties": [
                    "sequence"  # 序号
                ]
            },
            "TRIGGERS": {
                "description": "事件触发事件",
                "properties": [
                    "causality_strength"  # 因果关系强度
                ]
            },
            "CONTRIBUTES_TO": {
                "description": "事件对主线的贡献",
                "properties": [
                    "contribution_score",  # 贡献分数
                    "contribution_type"    # 贡献类型 (推动/铺垫/转折/高潮)
                ]
            },
            "MENTIONED_IN": {
                "description": "实体在文本中被提及",
                "properties": [
                    "mention_type",  # 提及类型 (explicit/implicit)
                    "context"        # 上下文
                ]
            },
            "OCCURS_IN_TEXT": {
                "description": "事件发生在文本片段",
                "properties": [
                    "relevance_score"  # 相关度分数
                ]
            }
        }

    @staticmethod
    def create_sample_data(client) -> None:
        """
        创建示例数据用于测试

        Args:
            client: Neo4jClient实例
        """
        logger.info("Creating sample data...")

        # 创建示例章节
        client.create_node("Chapter", {
            "number": 1,
            "title": "第一章 初遇",
            "summary": "主角与女主角的初次相遇",
            "word_count": 3000
        })

        # 创建示例人物
        client.create_node("Character", {
            "id": "char_001",
            "name": "张三",
            "gender": "男",
            "description": "主角，年轻的修仙者",
            "first_appearance": 1,
            "importance": 1.0,
            "mention_count": 50
        })

        client.create_node("Character", {
            "id": "char_002",
            "name": "李四",
            "gender": "女",
            "description": "女主角，天才剑修",
            "first_appearance": 1,
            "importance": 0.9,
            "mention_count": 45
        })

        # 创建示例关系
        client.create_relationship(
            ("Character", "id", "char_001"),
            ("Character", "id", "char_002"),
            "KNOWS",
            {
                "relationship_type": "朋友",
                "strength": 0.8,
                "first_met_chapter": 1
            }
        )

        logger.info("Sample data created successfully")
