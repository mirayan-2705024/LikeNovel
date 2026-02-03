"""
数据库初始化脚本
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import Config
from backend.database.neo4j_client import Neo4jClient
from backend.database.graph_schema import GraphSchema
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """主函数"""
    logger.info("Starting database initialization...")

    try:
        # 连接数据库
        client = Neo4jClient(
            uri=Config.NEO4J_URI,
            user=Config.NEO4J_USER,
            password=Config.NEO4J_PASSWORD
        )

        # 清空数据库（可选，谨慎使用）
        response = input("Do you want to clear all existing data? (yes/no): ")
        if response.lower() == 'yes':
            logger.warning("Clearing all data from database...")
            client.delete_all()

        # 初始化模式
        GraphSchema.initialize_schema(client)

        # 创建示例数据（可选）
        response = input("Do you want to create sample data? (yes/no): ")
        if response.lower() == 'yes':
            GraphSchema.create_sample_data(client)

        # 显示统计信息
        stats = client.get_statistics()
        logger.info("Database statistics:")
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")

        logger.info("Database initialization completed successfully!")

        client.close()

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
