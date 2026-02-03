"""
实体提取器
提取小说中的人物、地点等实体
"""
from collections import Counter
from typing import List, Dict, Set
import logging
from .text_processor import TextProcessor

logger = logging.getLogger(__name__)


class EntityExtractor:
    """实体提取器类"""

    def __init__(self, min_mentions: int = 3):
        """
        初始化实体提取器

        Args:
            min_mentions: 最小提及次数阈值
        """
        self.text_processor = TextProcessor()
        self.min_mentions = min_mentions
        logger.info(f"EntityExtractor initialized with min_mentions={min_mentions}")

    def extract_characters(self, chapters: List[Dict]) -> List[Dict]:
        """
        提取人物

        Args:
            chapters: 章节列表

        Returns:
            人物列表
        """
        logger.info("Extracting characters...")

        # 收集所有人名
        all_names = []
        name_chapters = {}  # 记录每个人名出现的章节

        for chapter in chapters:
            content = chapter["content"]
            names = self.text_processor.extract_names(content)

            for name in names:
                all_names.append(name)
                if name not in name_chapters:
                    name_chapters[name] = set()
                name_chapters[name].add(chapter["number"])

        # 统计频次
        name_counter = Counter(all_names)

        # 过滤低频人名
        characters = []
        char_id = 1

        for name, count in name_counter.most_common():
            if count < self.min_mentions:
                continue

            # 获取首次出现章节
            first_appearance = min(name_chapters[name])

            character = {
                "id": f"char_{char_id:03d}",
                "name": name,
                "mention_count": count,
                "first_appearance": first_appearance,
                "chapters": sorted(list(name_chapters[name])),
                "importance": self._calculate_importance(count, len(chapters))
            }

            characters.append(character)
            char_id += 1

        logger.info(f"Extracted {len(characters)} characters")
        return characters

    def extract_locations(self, chapters: List[Dict]) -> List[Dict]:
        """
        提取地点

        Args:
            chapters: 章节列表

        Returns:
            地点列表
        """
        logger.info("Extracting locations...")

        # 收集所有地名
        all_locations = []
        location_chapters = {}

        for chapter in chapters:
            content = chapter["content"]
            locations = self.text_processor.extract_locations(content)

            for loc in locations:
                all_locations.append(loc)
                if loc not in location_chapters:
                    location_chapters[loc] = set()
                location_chapters[loc].add(chapter["number"])

        # 统计频次
        location_counter = Counter(all_locations)

        # 过滤低频地名
        locations = []
        loc_id = 1

        for name, count in location_counter.most_common():
            if count < self.min_mentions:
                continue

            location = {
                "id": f"loc_{loc_id:03d}",
                "name": name,
                "mention_count": count,
                "chapters": sorted(list(location_chapters[name])),
                "type": "unknown"  # 后续可以通过规则或模型判断类型
            }

            locations.append(location)
            loc_id += 1

        logger.info(f"Extracted {len(locations)} locations")
        return locations

    def merge_similar_names(self, characters: List[Dict], threshold: float = 0.8) -> List[Dict]:
        """
        合并相似的人名（处理别名）

        Args:
            characters: 人物列表
            threshold: 相似度阈值

        Returns:
            合并后的人物列表
        """
        logger.info("Merging similar character names...")

        merged = []
        used = set()

        for i, char1 in enumerate(characters):
            if i in used:
                continue

            # 查找相似的人名
            similar_chars = [char1]
            for j, char2 in enumerate(characters[i+1:], start=i+1):
                if j in used:
                    continue

                similarity = self._name_similarity(char1["name"], char2["name"])
                if similarity >= threshold:
                    similar_chars.append(char2)
                    used.add(j)

            # 合并
            if len(similar_chars) > 1:
                merged_char = self._merge_characters(similar_chars)
                merged.append(merged_char)
            else:
                merged.append(char1)

            used.add(i)

        logger.info(f"Merged {len(characters)} characters into {len(merged)}")
        return merged

    def _calculate_importance(self, mention_count: int, total_chapters: int) -> float:
        """
        计算人物重要性

        Args:
            mention_count: 提及次数
            total_chapters: 总章节数

        Returns:
            重要性分数 (0-1)
        """
        # 简单实现：基于提及频率
        # 可以后续扩展为考虑更多因素
        max_mentions = mention_count  # 假设当前是最高频
        return min(mention_count / (total_chapters * 5), 1.0)  # 归一化

    def _name_similarity(self, name1: str, name2: str) -> float:
        """
        计算人名相似度

        Args:
            name1: 人名1
            name2: 人名2

        Returns:
            相似度分数 (0-1)
        """
        # 简单实现：检查包含关系
        if name1 in name2 or name2 in name1:
            return 0.9

        # 检查共同字符
        set1 = set(name1)
        set2 = set(name2)
        intersection = set1 & set2

        if not set1 or not set2:
            return 0.0

        return len(intersection) / max(len(set1), len(set2))

    def _merge_characters(self, characters: List[Dict]) -> Dict:
        """
        合并多个人物记录

        Args:
            characters: 人物列表

        Returns:
            合并后的人物
        """
        # 使用最长的名字作为主名
        main_char = max(characters, key=lambda x: len(x["name"]))

        # 合并别名
        aliases = [c["name"] for c in characters if c["name"] != main_char["name"]]

        # 合并统计信息
        total_mentions = sum(c["mention_count"] for c in characters)
        all_chapters = set()
        for c in characters:
            all_chapters.update(c["chapters"])

        merged = main_char.copy()
        merged["aliases"] = aliases
        merged["mention_count"] = total_mentions
        merged["chapters"] = sorted(list(all_chapters))
        merged["first_appearance"] = min(c["first_appearance"] for c in characters)

        return merged

    def extract_entities_from_novel(self, parsed_novel: Dict) -> Dict:
        """
        从解析后的小说中提取所有实体

        Args:
            parsed_novel: 解析后的小说数据

        Returns:
            包含所有实体的字典
        """
        logger.info("Extracting all entities from novel...")

        chapters = parsed_novel["chapters"]

        # 提取人物
        characters = self.extract_characters(chapters)
        characters = self.merge_similar_names(characters)

        # 提取地点
        locations = self.extract_locations(chapters)

        result = {
            "characters": characters,
            "locations": locations,
            "metadata": parsed_novel["metadata"]
        }

        logger.info(f"Extraction complete: {len(characters)} characters, {len(locations)} locations")
        return result
