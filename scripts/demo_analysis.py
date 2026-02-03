"""
演示脚本 - 展示如何使用小说分析系统
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import Config
from backend.database.neo4j_client import Neo4jClient
from backend.parsers.txt_parser import TxtParser
from backend.extractors.entity_extractor import EntityExtractor
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_parse_novel(file_path: str):
    """
    演示小说解析功能

    Args:
        file_path: 小说文件路径
    """
    logger.info("=" * 60)
    logger.info("Demo: Parsing Novel")
    logger.info("=" * 60)

    # 解析小说
    parser = TxtParser()
    novel_data = parser.parse(file_path)

    # 显示基本信息
    print(f"\n📚 小说信息:")
    print(f"  标题: {novel_data['metadata']['title']}")
    print(f"  作者: {novel_data['metadata']['author']}")
    print(f"  章节数: {novel_data['total_chapters']}")
    print(f"  总字数: {novel_data['total_words']}")

    # 显示前3章信息
    print(f"\n📖 前3章预览:")
    for chapter in novel_data['chapters'][:3]:
        print(f"  {chapter['title']} - {chapter['word_count']}字")

    return novel_data


def demo_extract_entities(novel_data: dict):
    """
    演示实体提取功能

    Args:
        novel_data: 解析后的小说数据
    """
    logger.info("=" * 60)
    logger.info("Demo: Extracting Entities")
    logger.info("=" * 60)

    # 提取实体
    extractor = EntityExtractor(min_mentions=2)
    entities = extractor.extract_entities_from_novel(novel_data)

    # 显示人物信息
    print(f"\n👥 提取的人物 ({len(entities['characters'])}个):")
    for char in entities['characters'][:10]:  # 只显示前10个
        print(f"  {char['name']}")
        print(f"    - 提及次数: {char['mention_count']}")
        print(f"    - 首次出现: 第{char['first_appearance']}章")
        print(f"    - 重要性: {char['importance']:.2f}")
        if 'aliases' in char:
            print(f"    - 别名: {', '.join(char['aliases'])}")

    # 显示地点信息
    print(f"\n🗺️  提取的地点 ({len(entities['locations'])}个):")
    for loc in entities['locations'][:10]:  # 只显示前10个
        print(f"  {loc['name']} - 提及{loc['mention_count']}次")

    return entities


def demo_save_to_neo4j(novel_data: dict, entities: dict):
    """
    演示保存到Neo4j数据库

    Args:
        novel_data: 小说数据
        entities: 实体数据
    """
    logger.info("=" * 60)
    logger.info("Demo: Saving to Neo4j")
    logger.info("=" * 60)

    try:
        # 连接数据库
        client = Neo4jClient(
            uri=Config.NEO4J_URI,
            user=Config.NEO4J_USER,
            password=Config.NEO4J_PASSWORD
        )

        # 保存章节信息
        print(f"\n💾 保存章节信息...")
        for chapter in novel_data['chapters'][:5]:  # 只保存前5章作为演示
            client.create_node("Chapter", {
                "number": chapter["number"],
                "title": chapter["title"],
                "word_count": chapter["word_count"]
            })
        print(f"  ✓ 已保存 {min(5, len(novel_data['chapters']))} 个章节")

        # 保存人物信息
        print(f"\n💾 保存人物信息...")
        for char in entities['characters'][:10]:  # 只保存前10个人物
            client.create_node("Character", {
                "id": char["id"],
                "name": char["name"],
                "mention_count": char["mention_count"],
                "first_appearance": char["first_appearance"],
                "importance": char["importance"]
            })
        print(f"  ✓ 已保存 {min(10, len(entities['characters']))} 个人物")

        # 显示数据库统计
        stats = client.get_statistics()
        print(f"\n📊 数据库统计:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

        client.close()
        print(f"\n✅ 数据已成功保存到Neo4j!")

    except Exception as e:
        logger.error(f"保存到Neo4j失败: {e}")
        print(f"\n❌ 保存失败: {e}")
        print(f"   请确保Neo4j数据库正在运行 (docker-compose up -d)")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🎭 小说脉络分析系统 - 演示程序")
    print("=" * 60)

    # 检查是否提供了文件路径
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # 使用默认示例文件
        file_path = "data/sample_novels/example.txt"
        print(f"\n💡 提示: 可以通过命令行参数指定小说文件")
        print(f"   用法: python scripts/demo_analysis.py <小说文件路径>")
        print(f"\n📁 使用默认示例文件: {file_path}")

    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"\n❌ 错误: 文件不存在: {file_path}")
        print(f"\n💡 请先创建示例文件或指定有效的小说文件路径")
        return

    try:
        # 1. 解析小说
        novel_data = demo_parse_novel(file_path)

        # 2. 提取实体
        entities = demo_extract_entities(novel_data)

        # 3. 保存到数据库
        response = input("\n是否要将数据保存到Neo4j数据库? (yes/no): ")
        if response.lower() == 'yes':
            demo_save_to_neo4j(novel_data, entities)

        print("\n" + "=" * 60)
        print("✨ 演示完成!")
        print("=" * 60)

    except Exception as e:
        logger.error(f"演示过程出错: {e}", exc_info=True)
        print(f"\n❌ 错误: {e}")


if __name__ == "__main__":
    main()
