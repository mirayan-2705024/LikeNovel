"""
Neo4j数据库客户端
提供与Neo4j数据库的连接和基础操作
"""
from neo4j import GraphDatabase
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class Neo4jClient:
    """Neo4j数据库客户端类"""

    def __init__(self, uri: str, user: str, password: str):
        """
        初始化Neo4j客户端

        Args:
            uri: Neo4j数据库URI
            user: 用户名
            password: 密码
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None
        self._connect()

    def _connect(self):
        """建立数据库连接"""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            # 测试连接
            self.driver.verify_connectivity()
            logger.info(f"Successfully connected to Neo4j at {self.uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    def close(self):
        """关闭数据库连接"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")

    def execute_query(self, query: str, parameters: Optional[Dict] = None) -> List[Dict]:
        """
        执行Cypher查询

        Args:
            query: Cypher查询语句
            parameters: 查询参数

        Returns:
            查询结果列表
        """
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

    def execute_write(self, query: str, parameters: Optional[Dict] = None) -> Any:
        """
        执行写入操作

        Args:
            query: Cypher查询语句
            parameters: 查询参数

        Returns:
            执行结果
        """
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return result.consume()

    def create_node(self, label: str, properties: Dict) -> Dict:
        """
        创建节点

        Args:
            label: 节点标签
            properties: 节点属性

        Returns:
            创建的节点信息
        """
        query = f"""
        CREATE (n:{label} $props)
        RETURN n
        """
        result = self.execute_query(query, {"props": properties})
        return result[0] if result else {}

    def create_relationship(
        self,
        from_node: tuple,
        to_node: tuple,
        rel_type: str,
        properties: Optional[Dict] = None
    ) -> Dict:
        """
        创建关系

        Args:
            from_node: 起始节点 (label, id_property, id_value)
            to_node: 目标节点 (label, id_property, id_value)
            rel_type: 关系类型
            properties: 关系属性

        Returns:
            创建的关系信息
        """
        from_label, from_prop, from_val = from_node
        to_label, to_prop, to_val = to_node

        query = f"""
        MATCH (a:{from_label} {{{from_prop}: $from_val}})
        MATCH (b:{to_label} {{{to_prop}: $to_val}})
        CREATE (a)-[r:{rel_type} $props]->(b)
        RETURN r
        """
        result = self.execute_query(
            query,
            {
                "from_val": from_val,
                "to_val": to_val,
                "props": properties or {}
            }
        )
        return result[0] if result else {}

    def find_node(self, label: str, property_name: str, property_value: Any) -> Optional[Dict]:
        """
        查找节点

        Args:
            label: 节点标签
            property_name: 属性名
            property_value: 属性值

        Returns:
            节点信息或None
        """
        query = f"""
        MATCH (n:{label} {{{property_name}: $value}})
        RETURN n
        """
        result = self.execute_query(query, {"value": property_value})
        return result[0] if result else None

    def update_node(self, label: str, property_name: str, property_value: Any, updates: Dict) -> Dict:
        """
        更新节点属性

        Args:
            label: 节点标签
            property_name: 查找属性名
            property_value: 查找属性值
            updates: 要更新的属性字典

        Returns:
            更新后的节点信息
        """
        query = f"""
        MATCH (n:{label} {{{property_name}: $value}})
        SET n += $updates
        RETURN n
        """
        result = self.execute_query(
            query,
            {"value": property_value, "updates": updates}
        )
        return result[0] if result else {}

    def delete_all(self):
        """删除数据库中的所有节点和关系（谨慎使用）"""
        query = "MATCH (n) DETACH DELETE n"
        self.execute_write(query)
        logger.warning("All nodes and relationships deleted from database")

    def create_indexes(self):
        """创建常用索引以提升查询性能"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS FOR (c:Character) ON (c.name)",
            "CREATE INDEX IF NOT EXISTS FOR (c:Character) ON (c.id)",
            "CREATE INDEX IF NOT EXISTS FOR (e:Event) ON (e.id)",
            "CREATE INDEX IF NOT EXISTS FOR (e:Event) ON (e.chapter)",
            "CREATE INDEX IF NOT EXISTS FOR (l:Location) ON (l.name)",
            "CREATE INDEX IF NOT EXISTS FOR (ch:Chapter) ON (ch.number)",
        ]

        for index_query in indexes:
            try:
                self.execute_write(index_query)
                logger.info(f"Created index: {index_query}")
            except Exception as e:
                logger.warning(f"Index creation failed or already exists: {e}")

    def get_statistics(self) -> Dict:
        """
        获取数据库统计信息

        Returns:
            包含各类节点和关系数量的字典
        """
        stats = {}

        # 节点统计
        node_labels = ["Character", "Event", "Location", "Chapter", "State"]
        for label in node_labels:
            query = f"MATCH (n:{label}) RETURN count(n) as count"
            result = self.execute_query(query)
            stats[f"{label.lower()}_count"] = result[0]["count"] if result else 0

        # 关系统计
        query = "MATCH ()-[r]->() RETURN count(r) as count"
        result = self.execute_query(query)
        stats["relationship_count"] = result[0]["count"] if result else 0

        return stats

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()
