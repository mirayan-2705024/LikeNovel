"""
时间线分析器
构建小说的时间线和事件序列
"""
from typing import List, Dict
import re
import logging
from .event_analyzer import EventAnalyzer

logger = logging.getLogger(__name__)


class TimelineAnalyzer:
    """时间线分析器类"""

    def __init__(self):
        """初始化时间线分析器"""
        self.event_analyzer = EventAnalyzer()
        self.time_keywords = self._init_time_keywords()
        logger.info("TimelineAnalyzer initialized")

    def _init_time_keywords(self) -> Dict[str, List[str]]:
        """
        初始化时间关键词

        Returns:
            时间关键词字典
        """
        return {
            "absolute": [
                r'\d+年', r'\d+月', r'\d+日',
                r'春天', r'夏天', r'秋天', r'冬天',
                r'早上', r'中午', r'下午', r'晚上', r'夜里'
            ],
            "relative": [
                r'第二天', r'次日', r'翌日',
                r'三天后', r'一周后', r'一月后', r'一年后',
                r'\d+天后', r'\d+月后', r'\d+年后',
                r'同时', r'此时', r'这时', r'那时',
                r'之前', r'之后', r'以前', r'以后',
                r'不久', r'很快', r'随后', r'接着', r'然后'
            ]
        }

    def analyze(
        self,
        chapters: List[Dict],
        characters: List[Dict],
        relations: List[Dict]
    ) -> Dict:
        """
        分析时间线

        Args:
            chapters: 章节列表
            characters: 人物列表
            relations: 关系列表

        Returns:
            时间线分析结果
        """
        logger.info("Analyzing timeline...")

        # 提取事件
        events = self.event_analyzer.extract_events(chapters, characters)

        # 计算事件重要性
        events = self.event_analyzer.calculate_importance(
            events, characters, relations
        )

        # 提取时间标记
        events = self._extract_time_markers(events, chapters)

        # 构建事件序列
        timeline = self._build_timeline(events)

        # 构建事件层级
        hierarchy = self.event_analyzer.build_event_hierarchy(events)

        # 分析因果关系
        causality = self.event_analyzer.analyze_causality(events)

        # 计算主线贡献度
        events = self._calculate_contribution(events, characters)

        # 识别主线事件
        main_plot_events = self._identify_main_plot(events)

        result = {
            "events": events,
            "timeline": timeline,
            "hierarchy": hierarchy,
            "causality": causality,
            "main_plot_events": main_plot_events,
            "statistics": {
                "total_events": len(events),
                "major_events": len([e for e in events if e["event_type"] == "major"]),
                "minor_events": len([e for e in events if e["event_type"] == "minor"]),
                "main_plot_events": len(main_plot_events),
                "causal_relations": len(causality)
            }
        }

        logger.info(f"Timeline analysis complete: {len(events)} events, "
                   f"{len(main_plot_events)} main plot events")

        return result

    def _extract_time_markers(
        self,
        events: List[Dict],
        chapters: List[Dict]
    ) -> List[Dict]:
        """
        提取时间标记

        Args:
            events: 事件列表
            chapters: 章节列表

        Returns:
            带有时间标记的事件列表
        """
        chapter_dict = {ch["number"]: ch for ch in chapters}

        for event in events:
            chapter = chapter_dict[event["chapter"]]
            content = chapter["content"]

            # 查找事件描述附近的时间标记
            event_pos = content.find(event["description"][:50])
            if event_pos == -1:
                event["time_marker"] = None
                continue

            # 在事件前后100字符内查找时间标记
            context_start = max(0, event_pos - 100)
            context_end = min(len(content), event_pos + 100)
            context = content[context_start:context_end]

            # 查找时间关键词
            time_marker = None
            for time_type, patterns in self.time_keywords.items():
                for pattern in patterns:
                    match = re.search(pattern, context)
                    if match:
                        time_marker = {
                            "type": time_type,
                            "text": match.group(0)
                        }
                        break
                if time_marker:
                    break

            event["time_marker"] = time_marker

        return events

    def _build_timeline(self, events: List[Dict]) -> List[Dict]:
        """
        构建时间线

        Args:
            events: 事件列表

        Returns:
            时间线（排序后的事件列表）
        """
        # 按章节和序号排序
        timeline = sorted(events, key=lambda x: (x["chapter"], x["sequence"]))

        # 添加时间间隔信息
        for i in range(1, len(timeline)):
            prev_event = timeline[i-1]
            curr_event = timeline[i]

            # 计算时间间隔
            if curr_event["chapter"] == prev_event["chapter"]:
                time_gap = "同章节"
            else:
                chapter_diff = curr_event["chapter"] - prev_event["chapter"]
                time_gap = f"{chapter_diff}章后"

            curr_event["time_gap_from_prev"] = time_gap

        return timeline

    def _calculate_contribution(
        self,
        events: List[Dict],
        characters: List[Dict]
    ) -> List[Dict]:
        """
        计算事件对主线的贡献度

        Args:
            events: 事件列表
            characters: 人物列表

        Returns:
            带有贡献度的事件列表
        """
        # 识别主角（重要性最高的人物）
        main_character = max(
            characters,
            key=lambda x: x.get("final_importance", x.get("importance", 0))
        )["name"]

        for event in events:
            # 重要性分数
            importance = event["importance_score"]

            # 主角参与度
            main_char_involvement = 1.0 if main_character in event["participants"] else 0.3

            # 因果关系强度（简化：假设重要事件有更强的因果关系）
            causality_strength = importance * 0.8

            # 情节推进度（简化：基于事件类型）
            plot_advancement = 0.8 if event["event_type"] == "major" else 0.3

            # 计算贡献度
            contribution = (
                importance * 0.4 +
                causality_strength * 0.3 +
                main_char_involvement * 0.2 +
                plot_advancement * 0.1
            )

            event["contribution_score"] = contribution

            # 确定贡献类型
            if contribution >= 0.8:
                event["contribution_type"] = "高潮"
            elif contribution >= 0.6:
                event["contribution_type"] = "推动"
            elif contribution >= 0.4:
                event["contribution_type"] = "铺垫"
            elif contribution >= 0.2:
                event["contribution_type"] = "转折"
            else:
                event["contribution_type"] = "支线"

        return events

    def _identify_main_plot(self, events: List[Dict]) -> List[Dict]:
        """
        识别主线事件

        Args:
            events: 事件列表

        Returns:
            主线事件列表
        """
        # 选择贡献度高的事件作为主线
        main_plot_events = [
            event for event in events
            if event["contribution_score"] >= 0.5
        ]

        # 按时间排序
        main_plot_events.sort(key=lambda x: (x["chapter"], x["sequence"]))

        return main_plot_events

    def get_chapter_timeline(
        self,
        timeline_result: Dict,
        chapter_number: int
    ) -> List[Dict]:
        """
        获取指定章节的时间线

        Args:
            timeline_result: 时间线分析结果
            chapter_number: 章节号

        Returns:
            章节事件列表
        """
        return [
            event for event in timeline_result["timeline"]
            if event["chapter"] == chapter_number
        ]

    def get_character_timeline(
        self,
        timeline_result: Dict,
        character_name: str
    ) -> List[Dict]:
        """
        获取指定人物的时间线

        Args:
            timeline_result: 时间线分析结果
            character_name: 人物名称

        Returns:
            人物相关事件列表
        """
        return [
            event for event in timeline_result["timeline"]
            if character_name in event["participants"]
        ]

    def get_event_context(
        self,
        timeline_result: Dict,
        event_id: str,
        context_size: int = 2
    ) -> Dict:
        """
        获取事件的上下文

        Args:
            timeline_result: 时间线分析结果
            event_id: 事件ID
            context_size: 上下文大小（前后事件数量）

        Returns:
            事件上下文
        """
        timeline = timeline_result["timeline"]

        # 找到事件位置
        event_index = None
        for i, event in enumerate(timeline):
            if event["id"] == event_id:
                event_index = i
                break

        if event_index is None:
            return {}

        # 获取前后事件
        start = max(0, event_index - context_size)
        end = min(len(timeline), event_index + context_size + 1)

        return {
            "target_event": timeline[event_index],
            "previous_events": timeline[start:event_index],
            "following_events": timeline[event_index+1:end]
        }
