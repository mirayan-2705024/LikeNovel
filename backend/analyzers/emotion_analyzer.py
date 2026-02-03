"""
情感分析器
分析小说中的情感变化
"""
from typing import List, Dict
from collections import defaultdict
import logging
from .text_processor import TextProcessor

logger = logging.getLogger(__name__)


class EmotionAnalyzer:
    """情感分析器类"""

    def __init__(self):
        """初始化情感分析器"""
        self.text_processor = TextProcessor()
        self.emotion_keywords = self._init_emotion_keywords()
        logger.info("EmotionAnalyzer initialized")

    def _init_emotion_keywords(self) -> Dict[str, List[str]]:
        """
        初始化情感关键词

        Returns:
            情感类型到关键词的映射
        """
        return {
            "positive": [
                "高兴", "开心", "快乐", "喜悦", "欢喜", "兴奋", "激动",
                "满意", "欣慰", "愉快", "舒畅", "笑", "微笑", "大笑"
            ],
            "negative": [
                "悲伤", "难过", "痛苦", "伤心", "哭", "流泪", "哀伤",
                "失望", "沮丧", "绝望", "忧愁", "忧伤", "悲痛"
            ],
            "angry": [
                "愤怒", "生气", "恼怒", "暴怒", "怒", "气", "火",
                "恨", "仇恨", "憎恨", "怨恨", "不满"
            ],
            "fear": [
                "害怕", "恐惧", "惊恐", "恐慌", "畏惧", "胆怯",
                "担心", "担忧", "忧虑", "紧张", "不安"
            ],
            "surprise": [
                "惊讶", "惊奇", "吃惊", "震惊", "诧异", "意外",
                "惊", "愕然", "惊呆"
            ],
            "love": [
                "爱", "喜欢", "喜爱", "钟情", "倾心", "爱慕",
                "思念", "想念", "牵挂", "关心", "在乎"
            ]
        }

    def analyze(
        self,
        chapters: List[Dict],
        characters: List[Dict],
        events: List[Dict]
    ) -> Dict:
        """
        分析情感

        Args:
            chapters: 章节列表
            characters: 人物列表
            events: 事件列表

        Returns:
            情感分析结果
        """
        logger.info("Analyzing emotions...")

        # 分析章节情感
        chapter_emotions = self._analyze_chapter_emotions(chapters)

        # 分析人物情感
        character_emotions = self._analyze_character_emotions(
            chapters, characters
        )

        # 分析人物间的情感关系
        emotion_relations = self._analyze_emotion_relations(
            chapters, characters
        )

        # 构建情感曲线
        emotion_curve = self._build_emotion_curve(chapter_emotions)

        # 识别情感高潮和低谷
        emotional_peaks = self._identify_emotional_peaks(chapter_emotions)

        result = {
            "chapter_emotions": chapter_emotions,
            "character_emotions": character_emotions,
            "emotion_relations": emotion_relations,
            "emotion_curve": emotion_curve,
            "emotional_peaks": emotional_peaks,
            "statistics": {
                "average_emotion": sum(
                    ch["emotion_score"] for ch in chapter_emotions
                ) / len(chapter_emotions) if chapter_emotions else 0,
                "emotion_variance": self._calculate_variance(
                    [ch["emotion_score"] for ch in chapter_emotions]
                ),
                "peak_count": len(emotional_peaks["peaks"]),
                "valley_count": len(emotional_peaks["valleys"])
            }
        }

        logger.info(f"Emotion analysis complete: {len(chapter_emotions)} chapters analyzed")

        return result

    def _analyze_chapter_emotions(self, chapters: List[Dict]) -> List[Dict]:
        """
        分析章节情感

        Args:
            chapters: 章节列表

        Returns:
            章节情感列表
        """
        chapter_emotions = []

        for chapter in chapters:
            content = chapter["content"]

            # 统计情感词
            emotion_counts = defaultdict(int)
            total_emotion_words = 0

            for emotion_type, keywords in self.emotion_keywords.items():
                for keyword in keywords:
                    count = content.count(keyword)
                    emotion_counts[emotion_type] += count
                    total_emotion_words += count

            # 计算情感分数（简化版：正面情感为正，负面情感为负）
            positive_score = emotion_counts["positive"] + emotion_counts["love"]
            negative_score = (
                emotion_counts["negative"] +
                emotion_counts["angry"] +
                emotion_counts["fear"]
            )

            # 归一化到 -1 到 1
            if total_emotion_words > 0:
                emotion_score = (positive_score - negative_score) / total_emotion_words
            else:
                emotion_score = 0.0

            # 主导情感
            dominant_emotion = max(
                emotion_counts.items(),
                key=lambda x: x[1]
            )[0] if emotion_counts else "neutral"

            chapter_emotions.append({
                "chapter": chapter["number"],
                "emotion_score": emotion_score,
                "dominant_emotion": dominant_emotion,
                "emotion_counts": dict(emotion_counts),
                "total_emotion_words": total_emotion_words
            })

        return chapter_emotions

    def _analyze_character_emotions(
        self,
        chapters: List[Dict],
        characters: List[Dict]
    ) -> Dict[str, List[Dict]]:
        """
        分析人物情感

        Args:
            chapters: 章节列表
            characters: 人物列表

        Returns:
            人物情感映射
        """
        char_emotions = defaultdict(list)
        char_names = {char["name"] for char in characters}

        for chapter in chapters:
            paragraphs = chapter["paragraphs"]

            for para in paragraphs:
                # 找出段落中的人物
                chars_in_para = [name for name in char_names if name in para]

                if not chars_in_para:
                    continue

                # 分析段落情感
                para_emotions = defaultdict(int)
                for emotion_type, keywords in self.emotion_keywords.items():
                    for keyword in keywords:
                        if keyword in para:
                            para_emotions[emotion_type] += 1

                if para_emotions:
                    dominant_emotion = max(
                        para_emotions.items(),
                        key=lambda x: x[1]
                    )[0]

                    for char in chars_in_para:
                        char_emotions[char].append({
                            "chapter": chapter["number"],
                            "emotion": dominant_emotion,
                            "context": para[:100]
                        })

        return dict(char_emotions)

    def _analyze_emotion_relations(
        self,
        chapters: List[Dict],
        characters: List[Dict]
    ) -> List[Dict]:
        """
        分析人物间的情感关系

        Args:
            chapters: 章节列表
            characters: 人物列表

        Returns:
            情感关系列表
        """
        emotion_relations = []
        char_names = {char["name"] for char in characters}

        # 情感关系模式
        patterns = [
            (r"(.+)喜欢(.+)", "喜欢"),
            (r"(.+)爱(.+)", "爱"),
            (r"(.+)恨(.+)", "恨"),
            (r"(.+)尊敬(.+)", "尊敬"),
            (r"(.+)讨厌(.+)", "讨厌"),
        ]

        for chapter in chapters:
            content = chapter["content"]

            for pattern, emotion_type in patterns:
                import re
                matches = re.finditer(pattern, content)

                for match in matches:
                    groups = match.groups()
                    if len(groups) >= 2:
                        char1, char2 = groups[0], groups[1]

                        if char1 in char_names and char2 in char_names:
                            emotion_relations.append({
                                "from": char1,
                                "to": char2,
                                "emotion_type": emotion_type,
                                "chapter": chapter["number"],
                                "intensity": 0.8,  # 默认强度
                                "context": match.group(0)
                            })

        return emotion_relations

    def _build_emotion_curve(self, chapter_emotions: List[Dict]) -> List[Dict]:
        """
        构建情感曲线

        Args:
            chapter_emotions: 章节情感列表

        Returns:
            情感曲线数据
        """
        curve = []
        for ch_emotion in chapter_emotions:
            curve.append({
                "chapter": ch_emotion["chapter"],
                "score": ch_emotion["emotion_score"],
                "dominant": ch_emotion["dominant_emotion"]
            })

        return curve

    def _identify_emotional_peaks(
        self,
        chapter_emotions: List[Dict]
    ) -> Dict[str, List[Dict]]:
        """
        识别情感高潮和低谷

        Args:
            chapter_emotions: 章节情感列表

        Returns:
            高潮和低谷信息
        """
        if len(chapter_emotions) < 3:
            return {"peaks": [], "valleys": []}

        peaks = []
        valleys = []

        for i in range(1, len(chapter_emotions) - 1):
            prev_score = chapter_emotions[i-1]["emotion_score"]
            curr_score = chapter_emotions[i]["emotion_score"]
            next_score = chapter_emotions[i+1]["emotion_score"]

            # 高潮：比前后都高
            if curr_score > prev_score and curr_score > next_score:
                peaks.append({
                    "chapter": chapter_emotions[i]["chapter"],
                    "score": curr_score,
                    "type": "peak"
                })

            # 低谷：比前后都低
            if curr_score < prev_score and curr_score < next_score:
                valleys.append({
                    "chapter": chapter_emotions[i]["chapter"],
                    "score": curr_score,
                    "type": "valley"
                })

        return {"peaks": peaks, "valleys": valleys}

    def _calculate_variance(self, scores: List[float]) -> float:
        """
        计算方差

        Args:
            scores: 分数列表

        Returns:
            方差
        """
        if not scores:
            return 0.0

        mean = sum(scores) / len(scores)
        variance = sum((x - mean) ** 2 for x in scores) / len(scores)

        return variance

    def get_character_emotion_timeline(
        self,
        character_name: str,
        analysis_result: Dict
    ) -> List[Dict]:
        """
        获取人物的情感时间线

        Args:
            character_name: 人物名称
            analysis_result: 分析结果

        Returns:
            情感时间线
        """
        return analysis_result["character_emotions"].get(character_name, [])

    def get_emotion_summary(self, analysis_result: Dict) -> Dict:
        """
        获取情感分析摘要

        Args:
            analysis_result: 分析结果

        Returns:
            摘要信息
        """
        stats = analysis_result["statistics"]

        # 统计主导情感分布
        emotion_distribution = defaultdict(int)
        for ch_emotion in analysis_result["chapter_emotions"]:
            emotion_distribution[ch_emotion["dominant_emotion"]] += 1

        summary = {
            "average_emotion": stats["average_emotion"],
            "emotion_variance": stats["emotion_variance"],
            "emotional_stability": "稳定" if stats["emotion_variance"] < 0.1 else "波动",
            "peak_count": stats["peak_count"],
            "valley_count": stats["valley_count"],
            "emotion_distribution": dict(emotion_distribution),
            "most_common_emotion": max(
                emotion_distribution.items(),
                key=lambda x: x[1]
            )[0] if emotion_distribution else "neutral"
        }

        return summary
