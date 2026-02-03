"""
事件分析器
识别和分析小说中的事件
"""
from typing import List, Dict, Set
import re
import logging
from .text_processor import TextProcessor

logger = logging.getLogger(__name__)


class EventAnalyzer:
    """事件分析器类"""

    def __init__(self):
        """初始化事件分析器"""
        self.text_processor = TextProcessor()
        self.action_verbs = self._load_action_verbs()
        logger.info("EventAnalyzer initialized")

    def _load_action_verbs(self) -> Set[str]:
        """
        加载动作动词列表

        Returns:
            动作动词集合
        """
        # 常见的动作动词
        return {
            '去', '来', '到', '走', '跑', '飞', '回', '进', '出', '离开',
            '说', '道', '问', '答', '喊', '叫', '笑', '哭', '叹',
            '打', '杀', '攻击', '战斗', '对抗', '击败', '逃跑',
            '看', '见', '发现', '找', '寻', '遇', '遇到',
            '给', '送', '拿', '取', '得', '获得', '失去',
            '学', '练', '修炼', '突破', '提升', '达到',
            '帮', '救', '保护', '伤害', '杀死',
            '开始', '结束', '完成', '失败', '成功',
            '决定', '选择', '同意', '拒绝',
            '爱', '恨', '喜欢', '讨厌', '尊敬'
        }

    def extract_events(self, chapters: List[Dict], characters: List[Dict]) -> List[Dict]:
        """
        提取事件

        Args:
            chapters: 章节列表
            characters: 人物列表

        Returns:
            事件列表
        """
        logger.info("Extracting events...")

        char_names = {char["name"] for char in characters}
        events = []
        event_id = 1

        for chapter in chapters:
            chapter_events = self._extract_chapter_events(
                chapter, char_names, event_id
            )
            events.extend(chapter_events)
            event_id += len(chapter_events)

        logger.info(f"Extracted {len(events)} events")
        return events

    def _extract_chapter_events(
        self,
        chapter: Dict,
        char_names: Set[str],
        start_id: int
    ) -> List[Dict]:
        """
        从章节中提取事件

        Args:
            chapter: 章节信息
            char_names: 人物名称集合
            start_id: 起始ID

        Returns:
            事件列表
        """
        events = []
        sentences = self.text_processor.split_sentences(chapter["content"])

        for i, sentence in enumerate(sentences):
            # 检查句子是否包含动作
            if not self._contains_action(sentence):
                continue

            # 提取参与者
            participants = [name for name in char_names if name in sentence]
            if not participants:
                continue

            # 创建事件
            event = {
                "id": f"event_{start_id + len(events):04d}",
                "description": sentence[:200],  # 限制长度
                "chapter": chapter["number"],
                "sequence": i,
                "participants": participants,
                "event_type": "minor",  # 默认为小事件
                "importance_score": 0.0,
                "sentence_index": i
            }

            events.append(event)

        return events

    def _contains_action(self, sentence: str) -> bool:
        """
        检查句子是否包含动作

        Args:
            sentence: 句子

        Returns:
            是否包含动作
        """
        words = self.text_processor.segment(sentence)
        return any(word in self.action_verbs for word in words)

    def calculate_importance(
        self,
        events: List[Dict],
        characters: List[Dict],
        relations: List[Dict]
    ) -> List[Dict]:
        """
        计算事件重要性

        Args:
            events: 事件列表
            characters: 人物列表
            relations: 关系列表

        Returns:
            带有重要性分数的事件列表
        """
        logger.info("Calculating event importance...")

        # 创建人物重要性映射
        char_importance = {
            char["name"]: char.get("final_importance", char.get("importance", 0.5))
            for char in characters
        }

        for event in events:
            # 计算人物参与度分数
            char_score = self._calculate_character_participation(
                event, char_importance
            )

            # 计算篇幅占比分数
            length_score = min(len(event["description"]) / 200, 1.0)

            # 计算情节影响力（简化版：基于参与人物数量）
            impact_score = min(len(event["participants"]) / 3, 1.0)

            # 综合重要性分数
            importance = (
                char_score * 0.4 +
                length_score * 0.3 +
                impact_score * 0.3
            )

            event["importance_score"] = importance

            # 根据重要性判断事件类型
            if importance >= 0.6:
                event["event_type"] = "major"

        return events

    def _calculate_character_participation(
        self,
        event: Dict,
        char_importance: Dict[str, float]
    ) -> float:
        """
        计算人物参与度分数

        Args:
            event: 事件信息
            char_importance: 人物重要性映射

        Returns:
            参与度分数
        """
        if not event["participants"]:
            return 0.0

        # 取参与人物中最高的重要性
        max_importance = max(
            char_importance.get(name, 0.0)
            for name in event["participants"]
        )

        return max_importance

    def build_event_hierarchy(self, events: List[Dict]) -> Dict:
        """
        构建事件层级结构（大事件和子事件）

        Args:
            events: 事件列表

        Returns:
            层级结构
        """
        logger.info("Building event hierarchy...")

        # 按章节分组
        events_by_chapter = {}
        for event in events:
            chapter = event["chapter"]
            if chapter not in events_by_chapter:
                events_by_chapter[chapter] = []
            events_by_chapter[chapter].append(event)

        # 识别大事件
        major_events = []
        sub_events_map = {}

        for chapter, chapter_events in events_by_chapter.items():
            # 按序号排序
            chapter_events.sort(key=lambda x: x["sequence"])

            # 识别大事件（重要性高的事件）
            for event in chapter_events:
                if event["event_type"] == "major":
                    major_events.append(event)
                    sub_events_map[event["id"]] = []

            # 将小事件归类到最近的大事件
            current_major = None
            for event in chapter_events:
                if event["event_type"] == "major":
                    current_major = event["id"]
                elif current_major and event["event_type"] == "minor":
                    sub_events_map[current_major].append(event)

        hierarchy = {
            "major_events": major_events,
            "sub_events_map": sub_events_map
        }

        logger.info(f"Built hierarchy: {len(major_events)} major events")
        return hierarchy

    def analyze_causality(self, events: List[Dict]) -> List[Dict]:
        """
        分析事件因果关系（简化版）

        Args:
            events: 事件列表

        Returns:
            因果关系列表
        """
        logger.info("Analyzing event causality...")

        causality = []
        causality_keywords = ['因为', '所以', '导致', '引起', '造成', '结果']

        # 按章节和序号排序
        sorted_events = sorted(events, key=lambda x: (x["chapter"], x["sequence"]))

        for i, event in enumerate(sorted_events):
            # 检查描述中是否包含因果关键词
            has_causality = any(kw in event["description"] for kw in causality_keywords)

            if has_causality and i > 0:
                # 简单假设：与前一个事件有因果关系
                prev_event = sorted_events[i-1]
                causality.append({
                    "from": prev_event["id"],
                    "to": event["id"],
                    "causality_strength": 0.7,
                    "evidence": event["description"][:100]
                })

        logger.info(f"Found {len(causality)} causal relationships")
        return causality
