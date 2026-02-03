"""
状态追踪器
追踪人物状态变化
"""
from typing import List, Dict, Set
from collections import defaultdict
import logging
from .text_processor import TextProcessor

logger = logging.getLogger(__name__)


class StateTracker:
    """状态追踪器类"""

    def __init__(self):
        """初始化状态追踪器"""
        self.text_processor = TextProcessor()
        self.state_keywords = self._init_state_keywords()
        logger.info("StateTracker initialized")

    def _init_state_keywords(self) -> Dict[str, Dict[str, List[str]]]:
        """
        初始化状态关键词

        Returns:
            状态类型到关键词的映射
        """
        return {
            "health": {
                "健康": ["健康", "康复", "痊愈", "恢复"],
                "受伤": ["受伤", "伤", "负伤", "重伤", "轻伤"],
                "生病": ["生病", "病", "患病", "染病"],
                "死亡": ["死", "死亡", "身亡", "丧生", "殒命"]
            },
            "mood": {
                "快乐": ["快乐", "高兴", "开心", "愉快"],
                "悲伤": ["悲伤", "难过", "伤心", "痛苦"],
                "愤怒": ["愤怒", "生气", "恼怒", "暴怒"],
                "平静": ["平静", "冷静", "淡定", "从容"]
            },
            "power": {
                "炼气期": ["炼气期", "炼气"],
                "筑基期": ["筑基期", "筑基"],
                "金丹期": ["金丹期", "金丹", "结丹"],
                "元婴期": ["元婴期", "元婴"],
                "化神期": ["化神期", "化神"]
            },
            "social_status": {
                "平民": ["平民", "百姓", "普通人"],
                "弟子": ["弟子", "门人", "门下"],
                "长老": ["长老", "执事"],
                "掌门": ["掌门", "宗主", "门主"]
            }
        }

    def analyze(
        self,
        chapters: List[Dict],
        characters: List[Dict],
        events: List[Dict]
    ) -> Dict:
        """
        分析状态变化

        Args:
            chapters: 章节列表
            characters: 人物列表
            events: 事件列表

        Returns:
            状态分析结果
        """
        logger.info("Analyzing character states...")

        # 追踪人物状态
        character_states = self._track_character_states(
            chapters, characters
        )

        # 识别状态变化
        state_changes = self._identify_state_changes(character_states)

        # 关联状态变化和事件
        state_event_map = self._map_states_to_events(
            state_changes, events
        )

        # 构建状态演化时间线
        state_timelines = self._build_state_timelines(character_states)

        result = {
            "character_states": character_states,
            "state_changes": state_changes,
            "state_event_map": state_event_map,
            "state_timelines": state_timelines,
            "statistics": {
                "total_states": sum(
                    len(states) for states in character_states.values()
                ),
                "total_changes": len(state_changes),
                "characters_tracked": len(character_states)
            }
        }

        logger.info(f"State tracking complete: {len(character_states)} characters tracked, "
                   f"{len(state_changes)} state changes")

        return result

    def _track_character_states(
        self,
        chapters: List[Dict],
        characters: List[Dict]
    ) -> Dict[str, List[Dict]]:
        """
        追踪人物状态

        Args:
            chapters: 章节列表
            characters: 人物列表

        Returns:
            人物状态映射
        """
        char_states = defaultdict(list)
        char_names = {char["name"] for char in characters}

        for chapter in chapters:
            content = chapter["content"]
            paragraphs = chapter["paragraphs"]

            for para_idx, para in enumerate(paragraphs):
                # 找出段落中的人物
                chars_in_para = [name for name in char_names if name in para]

                if not chars_in_para:
                    continue

                # 检测状态关键词
                for state_type, state_values in self.state_keywords.items():
                    for state_name, keywords in state_values.items():
                        for keyword in keywords:
                            if keyword in para:
                                # 为段落中的每个人物记录状态
                                for char in chars_in_para:
                                    char_states[char].append({
                                        "chapter": chapter["number"],
                                        "paragraph": para_idx,
                                        "state_type": state_type,
                                        "state_value": state_name,
                                        "context": para[:100],
                                        "keyword": keyword
                                    })

        return dict(char_states)

    def _identify_state_changes(
        self,
        character_states: Dict[str, List[Dict]]
    ) -> List[Dict]:
        """
        识别状态变化

        Args:
            character_states: 人物状态映射

        Returns:
            状态变化列表
        """
        state_changes = []

        for char_name, states in character_states.items():
            if len(states) < 2:
                continue

            # 按章节和段落排序
            sorted_states = sorted(
                states,
                key=lambda x: (x["chapter"], x["paragraph"])
            )

            # 检测同类型状态的变化
            state_by_type = defaultdict(list)
            for state in sorted_states:
                state_by_type[state["state_type"]].append(state)

            for state_type, type_states in state_by_type.items():
                for i in range(1, len(type_states)):
                    prev_state = type_states[i-1]
                    curr_state = type_states[i]

                    if prev_state["state_value"] != curr_state["state_value"]:
                        state_changes.append({
                            "character": char_name,
                            "state_type": state_type,
                            "from_state": prev_state["state_value"],
                            "to_state": curr_state["state_value"],
                            "from_chapter": prev_state["chapter"],
                            "to_chapter": curr_state["chapter"],
                            "context": curr_state["context"]
                        })

        return state_changes

    def _map_states_to_events(
        self,
        state_changes: List[Dict],
        events: List[Dict]
    ) -> Dict:
        """
        关联状态变化和事件

        Args:
            state_changes: 状态变化列表
            events: 事件列表

        Returns:
            状态-事件映射
        """
        state_event_map = []

        for change in state_changes:
            char = change["character"]
            chapter = change["to_chapter"]

            # 查找同章节中该人物参与的事件
            related_events = [
                event for event in events
                if event["chapter"] == chapter and char in event["participants"]
            ]

            if related_events:
                # 选择最重要的事件
                trigger_event = max(
                    related_events,
                    key=lambda x: x.get("importance_score", 0)
                )

                state_event_map.append({
                    "state_change": change,
                    "trigger_event": {
                        "id": trigger_event["id"],
                        "description": trigger_event["description"][:100],
                        "importance": trigger_event.get("importance_score", 0)
                    }
                })

        return state_event_map

    def _build_state_timelines(
        self,
        character_states: Dict[str, List[Dict]]
    ) -> Dict[str, List[Dict]]:
        """
        构建状态演化时间线

        Args:
            character_states: 人物状态映射

        Returns:
            状态时间线映射
        """
        timelines = {}

        for char_name, states in character_states.items():
            # 按章节排序
            sorted_states = sorted(states, key=lambda x: x["chapter"])

            # 按状态类型分组
            timeline_by_type = defaultdict(list)
            for state in sorted_states:
                timeline_by_type[state["state_type"]].append({
                    "chapter": state["chapter"],
                    "value": state["state_value"],
                    "context": state["context"][:50]
                })

            timelines[char_name] = dict(timeline_by_type)

        return timelines

    def get_character_state_history(
        self,
        character_name: str,
        analysis_result: Dict,
        state_type: str = None
    ) -> List[Dict]:
        """
        获取人物的状态历史

        Args:
            character_name: 人物名称
            analysis_result: 分析结果
            state_type: 状态类型（可选）

        Returns:
            状态历史列表
        """
        states = analysis_result["character_states"].get(character_name, [])

        if state_type:
            states = [s for s in states if s["state_type"] == state_type]

        return sorted(states, key=lambda x: x["chapter"])

    def get_state_changes_by_character(
        self,
        character_name: str,
        analysis_result: Dict
    ) -> List[Dict]:
        """
        获取人物的所有状态变化

        Args:
            character_name: 人物名称
            analysis_result: 分析结果

        Returns:
            状态变化列表
        """
        return [
            change for change in analysis_result["state_changes"]
            if change["character"] == character_name
        ]

    def get_state_distribution(
        self,
        analysis_result: Dict,
        state_type: str
    ) -> Dict[str, int]:
        """
        获取状态分布统计

        Args:
            analysis_result: 分析结果
            state_type: 状态类型

        Returns:
            状态分布字典
        """
        distribution = defaultdict(int)

        for char_name, states in analysis_result["character_states"].items():
            for state in states:
                if state["state_type"] == state_type:
                    distribution[state["state_value"]] += 1

        return dict(distribution)

    def analyze_state_progression(
        self,
        character_name: str,
        analysis_result: Dict,
        state_type: str
    ) -> Dict:
        """
        分析人物在某个状态类型上的进展

        Args:
            character_name: 人物名称
            analysis_result: 分析结果
            state_type: 状态类型

        Returns:
            进展分析
        """
        states = self.get_character_state_history(
            character_name, analysis_result, state_type
        )

        if not states:
            return {"progression": "无数据"}

        # 获取状态序列
        state_sequence = [s["state_value"] for s in states]

        # 分析趋势
        unique_states = []
        for state in state_sequence:
            if not unique_states or unique_states[-1] != state:
                unique_states.append(state)

        progression = {
            "state_type": state_type,
            "initial_state": unique_states[0] if unique_states else "未知",
            "current_state": unique_states[-1] if unique_states else "未知",
            "state_sequence": unique_states,
            "change_count": len(unique_states) - 1,
            "stability": "稳定" if len(unique_states) <= 2 else "变化频繁"
        }

        return progression
