"""
地点分析器
分析小说中的地点和场景
"""
from typing import List, Dict, Set
from collections import defaultdict
import logging
from .text_processor import TextProcessor

logger = logging.getLogger(__name__)


class LocationAnalyzer:
    """地点分析器类"""

    def __init__(self):
        """初始化地点分析器"""
        self.text_processor = TextProcessor()
        logger.info("LocationAnalyzer initialized")

    def analyze(
        self,
        chapters: List[Dict],
        locations: List[Dict],
        characters: List[Dict],
        events: List[Dict]
    ) -> Dict:
        """
        分析地点

        Args:
            chapters: 章节列表
            locations: 地点列表
            characters: 人物列表
            events: 事件列表

        Returns:
            地点分析结果
        """
        logger.info("Analyzing locations...")

        # 分析地点重要性
        locations_with_importance = self._calculate_location_importance(
            locations, events
        )

        # 追踪场景转换
        scene_transitions = self._track_scene_transitions(
            chapters, locations_with_importance
        )

        # 关联人物和地点
        character_location_map = self._map_characters_to_locations(
            chapters, characters, locations_with_importance
        )

        # 关联事件和地点
        event_location_map = self._map_events_to_locations(
            events, locations_with_importance, chapters
        )

        # 分析地点类型
        locations_with_type = self._classify_location_types(
            locations_with_importance, chapters
        )

        result = {
            "locations": locations_with_type,
            "scene_transitions": scene_transitions,
            "character_location_map": character_location_map,
            "event_location_map": event_location_map,
            "statistics": {
                "total_locations": len(locations_with_type),
                "scene_transitions": len(scene_transitions),
                "most_active_location": self._get_most_active_location(
                    locations_with_type
                )
            }
        }

        logger.info(f"Location analysis complete: {len(locations_with_type)} locations, "
                   f"{len(scene_transitions)} scene transitions")

        return result

    def _calculate_location_importance(
        self,
        locations: List[Dict],
        events: List[Dict]
    ) -> List[Dict]:
        """
        计算地点重要性

        Args:
            locations: 地点列表
            events: 事件列表

        Returns:
            带有重要性的地点列表
        """
        # 统计每个地点的事件数量
        location_events = defaultdict(list)

        for event in events:
            event_desc = event["description"]
            for loc in locations:
                if loc["name"] in event_desc:
                    location_events[loc["name"]].append(event)

        # 计算重要性
        result = []
        for loc in locations:
            loc_copy = loc.copy()
            events_at_loc = location_events[loc["name"]]

            # 事件数量
            event_count = len(events_at_loc)

            # 重要事件数量
            important_events = sum(
                1 for e in events_at_loc
                if e.get("importance_score", 0) > 0.6
            )

            # 计算重要性分数
            importance = min(
                (event_count * 0.6 + important_events * 0.4) / 10,
                1.0
            )

            loc_copy["event_count"] = event_count
            loc_copy["important_events"] = important_events
            loc_copy["importance"] = importance

            result.append(loc_copy)

        # 按重要性排序
        result.sort(key=lambda x: x["importance"], reverse=True)

        return result

    def _track_scene_transitions(
        self,
        chapters: List[Dict],
        locations: List[Dict]
    ) -> List[Dict]:
        """
        追踪场景转换

        Args:
            chapters: 章节列表
            locations: 地点列表

        Returns:
            场景转换列表
        """
        transitions = []
        location_names = {loc["name"] for loc in locations}

        for chapter in chapters:
            paragraphs = chapter["paragraphs"]
            current_location = None

            for i, para in enumerate(paragraphs):
                # 检查段落中的地点
                found_locations = [
                    loc_name for loc_name in location_names
                    if loc_name in para
                ]

                if found_locations:
                    new_location = found_locations[0]  # 取第一个

                    if current_location and new_location != current_location:
                        # 发生场景转换
                        transitions.append({
                            "from": current_location,
                            "to": new_location,
                            "chapter": chapter["number"],
                            "paragraph": i,
                            "context": para[:100]
                        })

                    current_location = new_location

        return transitions

    def _map_characters_to_locations(
        self,
        chapters: List[Dict],
        characters: List[Dict],
        locations: List[Dict]
    ) -> Dict[str, List[Dict]]:
        """
        关联人物和地点

        Args:
            chapters: 章节列表
            characters: 人物列表
            locations: 地点列表

        Returns:
            人物到地点的映射
        """
        char_loc_map = defaultdict(lambda: defaultdict(int))
        char_names = {char["name"] for char in characters}
        loc_names = {loc["name"] for loc in locations}

        for chapter in chapters:
            for para in chapter["paragraphs"]:
                # 找出段落中的人物和地点
                chars_in_para = [name for name in char_names if name in para]
                locs_in_para = [name for name in loc_names if name in para]

                # 建立关联
                for char in chars_in_para:
                    for loc in locs_in_para:
                        char_loc_map[char][loc] += 1

        # 转换为列表格式
        result = {}
        for char, loc_counts in char_loc_map.items():
            result[char] = [
                {"location": loc, "visit_count": count}
                for loc, count in sorted(
                    loc_counts.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
            ]

        return result

    def _map_events_to_locations(
        self,
        events: List[Dict],
        locations: List[Dict],
        chapters: List[Dict]
    ) -> Dict[str, List[Dict]]:
        """
        关联事件和地点

        Args:
            events: 事件列表
            locations: 地点列表
            chapters: 章节列表

        Returns:
            地点到事件的映射
        """
        loc_event_map = defaultdict(list)
        loc_names = {loc["name"] for loc in locations}

        for event in events:
            event_desc = event["description"]

            # 找出事件发生的地点
            for loc_name in loc_names:
                if loc_name in event_desc:
                    loc_event_map[loc_name].append({
                        "event_id": event["id"],
                        "description": event["description"][:100],
                        "chapter": event["chapter"],
                        "importance": event.get("importance_score", 0)
                    })

        return dict(loc_event_map)

    def _classify_location_types(
        self,
        locations: List[Dict],
        chapters: List[Dict]
    ) -> List[Dict]:
        """
        分类地点类型

        Args:
            locations: 地点列表
            chapters: 章节列表

        Returns:
            带有类型的地点列表
        """
        # 地点类型关键词
        type_keywords = {
            "indoor": ["房", "屋", "殿", "堂", "室", "阁", "楼", "府", "宫"],
            "outdoor": ["山", "峰", "林", "森林", "河", "湖", "海", "谷", "原", "野"],
            "building": ["门", "派", "宗", "寺", "庙", "塔", "城", "镇", "村"],
            "natural": ["天", "地", "界", "域", "境", "洞", "窟"]
        }

        result = []
        for loc in locations:
            loc_copy = loc.copy()

            # 根据名称判断类型
            loc_type = "unknown"
            for type_name, keywords in type_keywords.items():
                if any(kw in loc["name"] for kw in keywords):
                    loc_type = type_name
                    break

            loc_copy["type"] = loc_type
            result.append(loc_copy)

        return result

    def _get_most_active_location(self, locations: List[Dict]) -> str:
        """
        获取最活跃的地点

        Args:
            locations: 地点列表

        Returns:
            最活跃地点的名称
        """
        if not locations:
            return "无"

        most_active = max(locations, key=lambda x: x.get("event_count", 0))
        return most_active["name"]

    def get_location_profile(
        self,
        location_name: str,
        analysis_result: Dict
    ) -> Dict:
        """
        获取地点的完整信息

        Args:
            location_name: 地点名称
            analysis_result: 分析结果

        Returns:
            地点信息
        """
        # 查找地点信息
        location = None
        for loc in analysis_result["locations"]:
            if loc["name"] == location_name:
                location = loc
                break

        if not location:
            return {}

        # 获取相关信息
        events = analysis_result["event_location_map"].get(location_name, [])

        # 获取访问过的人物
        visitors = []
        for char, locs in analysis_result["character_location_map"].items():
            for loc_info in locs:
                if loc_info["location"] == location_name:
                    visitors.append({
                        "character": char,
                        "visit_count": loc_info["visit_count"]
                    })

        # 获取场景转换
        transitions_from = [
            t for t in analysis_result["scene_transitions"]
            if t["from"] == location_name
        ]
        transitions_to = [
            t for t in analysis_result["scene_transitions"]
            if t["to"] == location_name
        ]

        profile = {
            "basic_info": location,
            "events": events,
            "visitors": sorted(visitors, key=lambda x: x["visit_count"], reverse=True),
            "transitions_from": transitions_from,
            "transitions_to": transitions_to
        }

        return profile

    def get_character_journey(
        self,
        character_name: str,
        analysis_result: Dict
    ) -> List[Dict]:
        """
        获取人物的地点轨迹

        Args:
            character_name: 人物名称
            analysis_result: 分析结果

        Returns:
            地点轨迹列表
        """
        char_locations = analysis_result["character_location_map"].get(
            character_name, []
        )

        return char_locations
