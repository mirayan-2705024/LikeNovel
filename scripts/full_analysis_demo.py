"""
完整分析演示脚本 - 展示Milestone 2的所有功能
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import Config
from backend.database.neo4j_client import Neo4jClient
from backend.parsers.txt_parser import TxtParser
from backend.extractors.entity_extractor import EntityExtractor
from backend.analyzers.character_analyzer import CharacterAnalyzer
from backend.analyzers.timeline_analyzer import TimelineAnalyzer
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_full_analysis(file_path: str):
    """
    完整分析演示

    Args:
        file_path: 小说文件路径
    """
    print("\n" + "=" * 70)
    print("🎭 小说脉络分析系统 - 完整分析演示 (Milestone 2)")
    print("=" * 70)

    # 1. 解析小说
    print("\n📚 步骤 1: 解析小说文件...")
    parser = TxtParser()
    novel_data = parser.parse(file_path)
    print(f"  ✓ 解析完成: {novel_data['total_chapters']}章, {novel_data['total_words']}字")

    # 2. 提取实体
    print("\n👥 步骤 2: 提取人物和地点...")
    extractor = EntityExtractor(min_mentions=2)
    entities = extractor.extract_entities_from_novel(novel_data)
    print(f"  ✓ 提取完成: {len(entities['characters'])}个人物, {len(entities['locations'])}个地点")

    # 3. 分析人物关系
    print("\n🔗 步骤 3: 分析人物关系...")
    char_analyzer = CharacterAnalyzer()
    char_analysis = char_analyzer.analyze(
        novel_data['chapters'],
        entities['characters']
    )
    print(f"  ✓ 分析完成: {len(char_analysis['relations'])}个关系")
    print(f"  - 主要人物: {len(char_analysis['main_characters'])}个")
    print(f"  - 次要人物: {len(char_analysis['supporting_characters'])}个")
    print(f"  - 网络密度: {char_analysis['network']['density']:.3f}")

    # 4. 分析时间线
    print("\n⏱️  步骤 4: 分析时间线和事件...")
    timeline_analyzer = TimelineAnalyzer()
    timeline_analysis = timeline_analyzer.analyze(
        novel_data['chapters'],
        char_analysis['characters'],
        char_analysis['relations']
    )
    print(f"  ✓ 分析完成: {timeline_analysis['statistics']['total_events']}个事件")
    print(f"  - 大事件: {timeline_analysis['statistics']['major_events']}个")
    print(f"  - 小事件: {timeline_analysis['statistics']['minor_events']}个")
    print(f"  - 主线事件: {timeline_analysis['statistics']['main_plot_events']}个")
    print(f"  - 因果关系: {timeline_analysis['statistics']['causal_relations']}个")

    # 5. 显示详细结果
    print("\n" + "=" * 70)
    print("📊 详细分析结果")
    print("=" * 70)

    # 显示主要人物
    print("\n👑 主要人物:")
    for char in char_analysis['main_characters'][:5]:
        print(f"  {char['name']}")
        print(f"    - 重要性: {char['final_importance']:.3f}")
        print(f"    - 提及次数: {char['mention_count']}")
        print(f"    - 关系数: {char['degree_centrality']}")
        print(f"    - 首次出现: 第{char['first_appearance']}章")

    # 显示主要关系
    print("\n🤝 主要关系:")
    for rel in char_analysis['relations'][:10]:
        print(f"  {rel['from']} ←→ {rel['to']}")
        print(f"    - 类型: {rel['relationship_type']}")
        print(f"    - 强度: {rel['strength']:.2f}")
        print(f"    - 首次相遇: 第{rel['first_met_chapter']}章")

    # 显示主线事件
    print("\n📖 主线事件:")
    for event in timeline_analysis['main_plot_events'][:10]:
        print(f"  第{event['chapter']}章: {event['description'][:60]}...")
        print(f"    - 重要性: {event['importance_score']:.2f}")
        print(f"    - 贡献度: {event['contribution_score']:.2f}")
        print(f"    - 类型: {event['contribution_type']}")
        print(f"    - 参与者: {', '.join(event['participants'])}")

    # 6. 保存到数据库
    response = input("\n💾 是否要将分析结果保存到Neo4j数据库? (yes/no): ")
    if response.lower() == 'yes':
        save_to_neo4j(novel_data, char_analysis, timeline_analysis)

    return {
        "novel_data": novel_data,
        "entities": entities,
        "char_analysis": char_analysis,
        "timeline_analysis": timeline_analysis
    }


def save_to_neo4j(novel_data, char_analysis, timeline_analysis):
    """
    保存分析结果到Neo4j

    Args:
        novel_data: 小说数据
        char_analysis: 人物分析结果
        timeline_analysis: 时间线分析结果
    """
    print("\n💾 保存到Neo4j数据库...")

    try:
        client = Neo4jClient(
            uri=Config.NEO4J_URI,
            user=Config.NEO4J_USER,
            password=Config.NEO4J_PASSWORD
        )

        # 保存章节
        print("  - 保存章节...")
        for chapter in novel_data['chapters']:
            client.create_node("Chapter", {
                "number": chapter["number"],
                "title": chapter["title"],
                "word_count": chapter["word_count"]
            })

        # 保存人物
        print("  - 保存人物...")
        for char in char_analysis['characters']:
            client.create_node("Character", {
                "id": char["id"],
                "name": char["name"],
                "mention_count": char["mention_count"],
                "first_appearance": char["first_appearance"],
                "importance": char.get("final_importance", char.get("importance", 0)),
                "degree_centrality": char.get("degree_centrality", 0)
            })

        # 保存关系
        print("  - 保存人物关系...")
        for rel in char_analysis['relations']:
            client.create_relationship(
                ("Character", "name", rel["from"]),
                ("Character", "name", rel["to"]),
                "KNOWS",
                {
                    "relationship_type": rel["relationship_type"],
                    "strength": rel["strength"],
                    "first_met_chapter": rel["first_met_chapter"]
                }
            )

        # 保存事件
        print("  - 保存事件...")
        for event in timeline_analysis['events'][:50]:  # 限制数量
            client.create_node("Event", {
                "id": event["id"],
                "description": event["description"],
                "chapter": event["chapter"],
                "sequence": event["sequence"],
                "event_type": event["event_type"],
                "importance_score": event["importance_score"],
                "contribution_score": event.get("contribution_score", 0)
            })

            # 连接人物和事件
            for participant in event["participants"]:
                try:
                    client.create_relationship(
                        ("Character", "name", participant),
                        ("Event", "id", event["id"]),
                        "PARTICIPATES_IN",
                        {"role": "参与者"}
                    )
                except:
                    pass  # 忽略错误

        # 保存事件顺序关系
        print("  - 保存事件时间线...")
        timeline = timeline_analysis['timeline']
        for i in range(len(timeline) - 1):
            try:
                client.create_relationship(
                    ("Event", "id", timeline[i]["id"]),
                    ("Event", "id", timeline[i+1]["id"]),
                    "NEXT",
                    {"time_gap": timeline[i+1].get("time_gap_from_prev", "未知")}
                )
            except:
                pass

        # 显示统计
        stats = client.get_statistics()
        print("\n📊 数据库统计:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

        print("\n✅ 数据保存成功!")
        print(f"   访问 http://localhost:7474 查看Neo4j图谱")

        client.close()

    except Exception as e:
        logger.error(f"保存失败: {e}", exc_info=True)
        print(f"\n❌ 保存失败: {e}")
        print(f"   请确保Neo4j正在运行: docker-compose up -d")


def main():
    """主函数"""
    # 检查文件路径
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "data/sample_novels/example.txt"
        print(f"\n💡 使用默认示例文件: {file_path}")
        print(f"   用法: python scripts/full_analysis_demo.py <小说文件路径>\n")

    if not os.path.exists(file_path):
        print(f"\n❌ 错误: 文件不存在: {file_path}")
        return

    try:
        # 运行完整分析
        result = demo_full_analysis(file_path)

        print("\n" + "=" * 70)
        print("✨ 分析完成!")
        print("=" * 70)
        print("\n💡 提示:")
        print("  - 使用 Neo4j Browser (http://localhost:7474) 可视化图谱")
        print("  - 运行 Cypher 查询探索数据")
        print("  - 查看 README.md 了解更多查询示例")

    except Exception as e:
        logger.error(f"分析失败: {e}", exc_info=True)
        print(f"\n❌ 错误: {e}")


if __name__ == "__main__":
    main()
