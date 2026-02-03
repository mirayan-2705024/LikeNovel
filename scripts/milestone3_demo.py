"""
Milestone 3 完整演示 - 地点、情感、状态分析
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import Config
from backend.database.neo4j_client import Neo4jClient
from backend.parsers.txt_parser import TxtParser
from backend.extractors.entity_extractor import EntityExtractor
from backend.analyzers.character_analyzer import CharacterAnalyzer
from backend.analyzers.timeline_analyzer import TimelineAnalyzer
from backend.analyzers.location_analyzer import LocationAnalyzer
from backend.analyzers.emotion_analyzer import EmotionAnalyzer
from backend.analyzers.state_tracker import StateTracker
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_milestone3(file_path: str):
    """
    Milestone 3 完整演示

    Args:
        file_path: 小说文件路径
    """
    print("\n" + "=" * 70)
    print("🎭 小说脉络分析系统 - Milestone 3 完整演示")
    print("=" * 70)

    # 基础分析（Milestone 1 & 2）
    print("\n📚 步骤 1-4: 基础分析...")
    parser = TxtParser()
    novel_data = parser.parse(file_path)

    extractor = EntityExtractor(min_mentions=2)
    entities = extractor.extract_entities_from_novel(novel_data)

    char_analyzer = CharacterAnalyzer()
    char_analysis = char_analyzer.analyze(
        novel_data['chapters'],
        entities['characters']
    )

    timeline_analyzer = TimelineAnalyzer()
    timeline_analysis = timeline_analyzer.analyze(
        novel_data['chapters'],
        char_analysis['characters'],
        char_analysis['relations']
    )

    print(f"  ✓ 基础分析完成")

    # Milestone 3: 地点分析
    print("\n🗺️  步骤 5: 地点分析...")
    location_analyzer = LocationAnalyzer()
    location_analysis = location_analyzer.analyze(
        novel_data['chapters'],
        entities['locations'],
        char_analysis['characters'],
        timeline_analysis['events']
    )
    print(f"  ✓ 地点分析完成: {location_analysis['statistics']['total_locations']}个地点")
    print(f"  - 场景转换: {location_analysis['statistics']['scene_transitions']}次")
    print(f"  - 最活跃地点: {location_analysis['statistics']['most_active_location']}")

    # Milestone 3: 情感分析
    print("\n💭 步骤 6: 情感分析...")
    emotion_analyzer = EmotionAnalyzer()
    emotion_analysis = emotion_analyzer.analyze(
        novel_data['chapters'],
        char_analysis['characters'],
        timeline_analysis['events']
    )
    print(f"  ✓ 情感分析完成")
    print(f"  - 平均情感: {emotion_analysis['statistics']['average_emotion']:.3f}")
    print(f"  - 情感波动: {emotion_analysis['statistics']['emotion_variance']:.3f}")
    print(f"  - 情感高潮: {emotion_analysis['statistics']['peak_count']}个")
    print(f"  - 情感低谷: {emotion_analysis['statistics']['valley_count']}个")

    # Milestone 3: 状态追踪
    print("\n📊 步骤 7: 状态追踪...")
    state_tracker = StateTracker()
    state_analysis = state_tracker.analyze(
        novel_data['chapters'],
        char_analysis['characters'],
        timeline_analysis['events']
    )
    print(f"  ✓ 状态追踪完成")
    print(f"  - 追踪人物: {state_analysis['statistics']['characters_tracked']}个")
    print(f"  - 状态记录: {state_analysis['statistics']['total_states']}条")
    print(f"  - 状态变化: {state_analysis['statistics']['total_changes']}次")

    # 显示详细结果
    print("\n" + "=" * 70)
    print("📊 Milestone 3 详细分析结果")
    print("=" * 70)

    # 地点分析结果
    print("\n🗺️  地点分析:")
    print("\n  重要地点:")
    for loc in location_analysis['locations'][:5]:
        print(f"    {loc['name']}")
        print(f"      - 类型: {loc['type']}")
        print(f"      - 事件数: {loc['event_count']}")
        print(f"      - 重要性: {loc['importance']:.2f}")

    print("\n  场景转换示例:")
    for trans in location_analysis['scene_transitions'][:5]:
        print(f"    第{trans['chapter']}章: {trans['from']} → {trans['to']}")

    # 情感分析结果
    print("\n💭 情感分析:")
    emotion_summary = emotion_analyzer.get_emotion_summary(emotion_analysis)
    print(f"\n  情感摘要:")
    print(f"    - 平均情感: {emotion_summary['average_emotion']:.3f}")
    print(f"    - 情感稳定性: {emotion_summary['emotional_stability']}")
    print(f"    - 最常见情感: {emotion_summary['most_common_emotion']}")

    print(f"\n  情感分布:")
    for emotion, count in emotion_summary['emotion_distribution'].items():
        print(f"    - {emotion}: {count}章")

    print(f"\n  情感高潮章节:")
    for peak in emotion_analysis['emotional_peaks']['peaks'][:3]:
        print(f"    - 第{peak['chapter']}章 (分数: {peak['score']:.2f})")

    # 状态追踪结果
    print("\n📊 状态追踪:")
    print("\n  人物状态变化:")
    for change in state_analysis['state_changes'][:10]:
        print(f"    {change['character']}: {change['from_state']} → {change['to_state']}")
        print(f"      - 类型: {change['state_type']}")
        print(f"      - 章节: 第{change['from_chapter']}章 → 第{change['to_chapter']}章")

    # 人物完整画像示例
    if char_analysis['main_characters']:
        main_char = char_analysis['main_characters'][0]
        char_name = main_char['name']

        print(f"\n" + "=" * 70)
        print(f"👤 人物完整画像: {char_name}")
        print("=" * 70)

        # 基本信息
        print(f"\n  基本信息:")
        print(f"    - 重要性: {main_char['final_importance']:.3f}")
        print(f"    - 提及次数: {main_char['mention_count']}")
        print(f"    - 关系数: {main_char['degree_centrality']}")

        # 地点轨迹
        char_locations = location_analysis['character_location_map'].get(char_name, [])
        if char_locations:
            print(f"\n  地点轨迹:")
            for loc_info in char_locations[:5]:
                print(f"    - {loc_info['location']}: 访问{loc_info['visit_count']}次")

        # 情感时间线
        char_emotions = emotion_analysis['character_emotions'].get(char_name, [])
        if char_emotions:
            print(f"\n  情感变化:")
            emotion_counts = {}
            for em in char_emotions:
                emotion_counts[em['emotion']] = emotion_counts.get(em['emotion'], 0) + 1
            for emotion, count in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:3]:
                print(f"    - {emotion}: {count}次")

        # 状态变化
        char_state_changes = state_tracker.get_state_changes_by_character(
            char_name, state_analysis
        )
        if char_state_changes:
            print(f"\n  状态变化:")
            for change in char_state_changes[:5]:
                print(f"    - {change['state_type']}: {change['from_state']} → {change['to_state']} (第{change['to_chapter']}章)")

    # 保存到数据库
    response = input("\n💾 是否要将完整分析结果保存到Neo4j数据库? (yes/no): ")
    if response.lower() == 'yes':
        save_complete_analysis(
            novel_data, char_analysis, timeline_analysis,
            location_analysis, emotion_analysis, state_analysis
        )

    return {
        "novel_data": novel_data,
        "char_analysis": char_analysis,
        "timeline_analysis": timeline_analysis,
        "location_analysis": location_analysis,
        "emotion_analysis": emotion_analysis,
        "state_analysis": state_analysis
    }


def save_complete_analysis(
    novel_data, char_analysis, timeline_analysis,
    location_analysis, emotion_analysis, state_analysis
):
    """保存完整分析结果到Neo4j"""
    print("\n💾 保存完整分析结果到Neo4j...")

    try:
        client = Neo4jClient(
            uri=Config.NEO4J_URI,
            user=Config.NEO4J_USER,
            password=Config.NEO4J_PASSWORD
        )

        # 保存基础数据（章节、人物、关系、事件）
        print("  - 保存基础数据...")
        for chapter in novel_data['chapters']:
            client.create_node("Chapter", {
                "number": chapter["number"],
                "title": chapter["title"],
                "word_count": chapter["word_count"]
            })

        for char in char_analysis['characters']:
            client.create_node("Character", {
                "id": char["id"],
                "name": char["name"],
                "mention_count": char["mention_count"],
                "importance": char.get("final_importance", 0)
            })

        for rel in char_analysis['relations']:
            try:
                client.create_relationship(
                    ("Character", "name", rel["from"]),
                    ("Character", "name", rel["to"]),
                    "KNOWS",
                    {"relationship_type": rel["relationship_type"], "strength": rel["strength"]}
                )
            except:
                pass

        # 保存地点
        print("  - 保存地点数据...")
        for loc in location_analysis['locations']:
            client.create_node("Location", {
                "id": loc["id"],
                "name": loc["name"],
                "type": loc["type"],
                "importance": loc["importance"],
                "event_count": loc["event_count"]
            })

        # 保存状态
        print("  - 保存状态数据...")
        state_id = 1
        for char_name, states in state_analysis['character_states'].items():
            for state in states[:20]:  # 限制数量
                try:
                    client.create_node("State", {
                        "id": f"state_{state_id:04d}",
                        "character_name": char_name,
                        "state_type": state["state_type"],
                        "value": state["state_value"],
                        "chapter": state["chapter"]
                    })
                    state_id += 1
                except:
                    pass

        # 保存情感关系
        print("  - 保存情感关系...")
        for emotion_rel in emotion_analysis['emotion_relations']:
            try:
                client.create_relationship(
                    ("Character", "name", emotion_rel["from"]),
                    ("Character", "name", emotion_rel["to"]),
                    "EMOTION_TOWARDS",
                    {
                        "emotion_type": emotion_rel["emotion_type"],
                        "intensity": emotion_rel["intensity"],
                        "chapter": emotion_rel["chapter"]
                    }
                )
            except:
                pass

        stats = client.get_statistics()
        print("\n📊 数据库统计:")
        for key, value in stats.items():
            print(f"  {key}: {value}")

        print("\n✅ 完整分析结果保存成功!")
        print(f"   访问 http://localhost:7474 查看完整图谱")

        client.close()

    except Exception as e:
        logger.error(f"保存失败: {e}", exc_info=True)
        print(f"\n❌ 保存失败: {e}")


def main():
    """主函数"""
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "data/sample_novels/example.txt"
        print(f"\n💡 使用默认示例文件: {file_path}\n")

    if not os.path.exists(file_path):
        print(f"\n❌ 错误: 文件不存在: {file_path}")
        return

    try:
        result = demo_milestone3(file_path)

        print("\n" + "=" * 70)
        print("✨ Milestone 3 分析完成!")
        print("=" * 70)
        print("\n🎉 所有核心功能已实现:")
        print("  ✅ Milestone 1: 基础框架")
        print("  ✅ Milestone 2: 核心分析功能")
        print("  ✅ Milestone 3: 扩展分析功能")
        print("\n💡 下一步: Milestone 4 - Web界面开发")

    except Exception as e:
        logger.error(f"分析失败: {e}", exc_info=True)
        print(f"\n❌ 错误: {e}")


if __name__ == "__main__":
    main()
