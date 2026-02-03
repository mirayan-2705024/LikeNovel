"""
关系提取器
提取人物之间的关系
"""
from collections import defaultdict
from typing import List, Dict, Tuple, Set
import re
import logging
from .text_processor import TextProcessor

logger = logging.getLogger(__name__)


class RelationExtractor:
    """关系提取器类"""

    def __init__(self):
        """初始化关系提取器"""
        self.text_processor = TextProcessor()
        self.relation_patterns = self._init_relation_patterns()
        logger.info("RelationExtractor initialized")

    def _init_relation_patterns(self) -> Dict[str, List[str]]:
        """
        初始化关系模式

        Returns:
            关系类型到模式列表的映射
        """
        return {
            "亲属": [
                r"(.+)的(父亲|母亲|儿子|女儿|哥哥|弟弟|姐姐|妹妹|爷爷|奶奶|爸爸|妈妈)",
                r"(.+)是(.+)的(父亲|母亲|儿子|女儿|哥哥|弟弟|姐姐|妹妹)",
            ],
            "朋友": [
                r"(.+)和(.+)(是|成为|做)(朋友|好友|兄弟|姐妹)",
                r"(.+)与(.+)交好",
            ],
            "师徒": [
                r"(.+)是(.+)的(师父|师傅|徒弟|弟子)",
                r"(.+)(拜|认)(.+)为师",
                r"(.+)传授(.+)",
            ],
            "恋人": [
                r"(.+)和(.+)(相爱|恋爱|喜欢|爱上)",
                r"(.+)爱着(.+)",
            ],
            "敌人": [
                r"(.+)和(.+)(为敌|敌对|仇恨|对抗)",
                r"(.+)是(.+)的(敌人|仇人|对手)",
                r"(.+)(杀|打|攻击)(.+)",
            ],
            "同门": [
                r"(.+)和(.+)是(同门|师兄弟|师姐妹)",
                r"(.+)与(.+)同为(.+)弟子",
            ]
        }

    def extract_relations_from_chapters(
        self,
        chapters: List[Dict],
        characters: List[Dict]
    ) -> List[Dict]:
        """
        从章节中提取人物关系

        Args:
            chapters: 章节列表
            characters: 人物列表

        Returns:
            关系列表
        """
        logger.info("Extracting character relations...")

        # 创建人物名称集合用于快速查找
        char_names = {char["name"] for char in characters}
        char_dict = {char["name"]: char for char in characters}

        # 提取共现关系
        cooccurrence_relations = self._extract_cooccurrence_relations(
            chapters, char_names, char_dict
        )

        # 提取模式匹配关系
        pattern_relations = self._extract_pattern_relations(
            chapters, char_names, char_dict
        )

        # 提取对话关系
        dialogue_relations = self._extract_dialogue_relations(
            chapters, char_names, char_dict
        )

        # 合并所有关系
        all_relations = self._merge_relations(
            cooccurrence_relations,
            pattern_relations,
            dialogue_relations
        )

        logger.info(f"Extracted {len(all_relations)} relations")
        return all_relations

    def _extract_cooccurrence_relations(
        self,
        chapters: List[Dict],
        char_names: Set[str],
        char_dict: Dict
    ) -> List[Dict]:
        """
        基于共现提取关系

        Args:
            chapters: 章节列表
            char_names: 人物名称集合
            char_dict: 人物字典

        Returns:
            关系列表
        """
        relations = defaultdict(lambda: {
            "count": 0,
            "chapters": set(),
            "contexts": []
        })

        for chapter in chapters:
            # 分段落分析
            for para in chapter["paragraphs"]:
                # 找出段落中出现的人物
                chars_in_para = [name for name in char_names if name in para]

                # 为每对人物创建共现关系
                for i, char1 in enumerate(chars_in_para):
                    for char2 in chars_in_para[i+1:]:
                        # 确保顺序一致
                        pair = tuple(sorted([char1, char2]))
                        relations[pair]["count"] += 1
                        relations[pair]["chapters"].add(chapter["number"])
                        if len(relations[pair]["contexts"]) < 3:  # 只保存前3个上下文
                            relations[pair]["contexts"].append(para[:100])

        # 转换为列表格式
        result = []
        rel_id = 1
        for (char1, char2), data in relations.items():
            if data["count"] >= 2:  # 至少共现2次
                result.append({
                    "id": f"rel_{rel_id:03d}",
                    "from": char1,
                    "to": char2,
                    "type": "认识",  # 默认类型
                    "strength": min(data["count"] / 10, 1.0),  # 归一化强度
                    "cooccurrence_count": data["count"],
                    "chapters": sorted(list(data["chapters"])),
                    "first_met_chapter": min(data["chapters"]),
                    "contexts": data["contexts"]
                })
                rel_id += 1

        return result

    def _extract_pattern_relations(
        self,
        chapters: List[Dict],
        char_names: Set[str],
        char_dict: Dict
    ) -> List[Dict]:
        """
        基于模式匹配提取关系

        Args:
            chapters: 章节列表
            char_names: 人物名称集合
            char_dict: 人物字典

        Returns:
            关系列表
        """
        relations = []
        rel_id = 1

        for chapter in chapters:
            content = chapter["content"]

            # 对每种关系类型应用模式
            for rel_type, patterns in self.relation_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, content)
                    for match in matches:
                        groups = match.groups()
                        # 提取人物名
                        potential_chars = [g for g in groups if g in char_names]

                        if len(potential_chars) >= 2:
                            relations.append({
                                "id": f"rel_pattern_{rel_id:03d}",
                                "from": potential_chars[0],
                                "to": potential_chars[1],
                                "type": rel_type,
                                "strength": 0.8,  # 模式匹配的关系强度较高
                                "chapter": chapter["number"],
                                "context": match.group(0)
                            })
                            rel_id += 1

        return relations

    def _extract_dialogue_relations(
        self,
        chapters: List[Dict],
        char_names: Set[str],
        char_dict: Dict
    ) -> List[Dict]:
        """
        基于对话提取关系

        Args:
            chapters: 章节列表
            char_names: 人物名称集合
            char_dict: 人物字典

        Returns:
            关系列表
        """
        relations = defaultdict(lambda: {
            "count": 0,
            "chapters": set()
        })

        for chapter in chapters:
            content = chapter["content"]
            dialogues = self.text_processor.extract_dialogues(content)

            # 分析对话中的人物关系
            for i, dialogue in enumerate(dialogues):
                speaker = dialogue["speaker"]
                if speaker not in char_names:
                    continue

                # 查找对话内容中提到的其他人物
                for char_name in char_names:
                    if char_name != speaker and char_name in dialogue["content"]:
                        pair = tuple(sorted([speaker, char_name]))
                        relations[pair]["count"] += 1
                        relations[pair]["chapters"].add(chapter["number"])

        # 转换为列表格式
        result = []
        rel_id = 1
        for (char1, char2), data in relations.items():
            if data["count"] >= 1:
                result.append({
                    "id": f"rel_dialogue_{rel_id:03d}",
                    "from": char1,
                    "to": char2,
                    "type": "对话",
                    "strength": min(data["count"] / 5, 1.0),
                    "dialogue_count": data["count"],
                    "chapters": sorted(list(data["chapters"]))
                })
                rel_id += 1

        return result

    def _merge_relations(self, *relation_lists) -> List[Dict]:
        """
        合并多个关系列表

        Args:
            *relation_lists: 多个关系列表

        Returns:
            合并后的关系列表
        """
        # 使用字典合并相同人物对的关系
        merged = {}

        for relations in relation_lists:
            for rel in relations:
                key = tuple(sorted([rel["from"], rel["to"]]))

                if key not in merged:
                    merged[key] = {
                        "from": rel["from"],
                        "to": rel["to"],
                        "types": [],
                        "strength": 0,
                        "chapters": set(),
                        "details": []
                    }

                merged[key]["types"].append(rel["type"])
                merged[key]["strength"] = max(merged[key]["strength"], rel.get("strength", 0))
                if "chapters" in rel:
                    merged[key]["chapters"].update(rel["chapters"])
                if "chapter" in rel:
                    merged[key]["chapters"].add(rel["chapter"])
                merged[key]["details"].append(rel)

        # 转换为列表格式
        result = []
        for i, (key, data) in enumerate(merged.items(), 1):
            # 确定主要关系类型
            type_counts = {}
            for t in data["types"]:
                type_counts[t] = type_counts.get(t, 0) + 1
            main_type = max(type_counts.items(), key=lambda x: x[1])[0]

            result.append({
                "id": f"rel_{i:03d}",
                "from": data["from"],
                "to": data["to"],
                "relationship_type": main_type,
                "strength": data["strength"],
                "first_met_chapter": min(data["chapters"]) if data["chapters"] else 1,
                "chapters": sorted(list(data["chapters"])),
                "all_types": list(set(data["types"])),
                "evidence_count": len(data["details"])
            })

        return result
