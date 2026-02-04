"""
混合分析器
结合传统 NLP 和 AI 大模型的优势
"""
import logging
from typing import List, Dict, Any
from config.config import Config
from backend.analyzers.ai_analyzer import AIAnalyzer

logger = logging.getLogger(__name__)


class HybridAnalyzer:
    """混合分析器 - 传统 NLP + AI 大模型"""

    def __init__(self):
        """初始化混合分析器"""
        self.ai_enabled = Config.ENABLE_AI_ANALYSIS

        if self.ai_enabled:
            try:
                self.ai_analyzer = AIAnalyzer(
                    provider=Config.AI_PROVIDER,
                    api_key=Config.OPENAI_API_KEY if Config.AI_PROVIDER == 'openai' else Config.ANTHROPIC_API_KEY
                )
                if self.ai_analyzer.enabled:
                    logger.info("AI 增强分析已启用")
                else:
                    logger.warning("AI 分析器初始化失败，将使用传统 NLP")
                    self.ai_enabled = False
            except Exception as e:
                logger.error(f"AI 分析器加载失败: {e}")
                self.ai_enabled = False
        else:
            logger.info("使用传统 NLP 分析（AI 增强未启用）")

    def enhance_character_analysis(
        self,
        traditional_result: Dict[str, Any],
        chapters: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        增强人物分析

        Args:
            traditional_result: 传统 NLP 分析结果
            chapters: 章节列表

        Returns:
            增强后的分析结果
        """
        if not self.ai_enabled:
            return traditional_result

        logger.info("使用 AI 增强人物分析...")

        try:
            # 为主要人物生成详细画像
            for character in traditional_result.get('main_characters', [])[:5]:  # 限制前5个主要人物
                char_name = character['name']

                # 收集人物相关的文本片段
                contexts = []
                for chapter in chapters[:10]:  # 限制章节数
                    if char_name in chapter['content']:
                        # 提取包含人物的段落
                        paragraphs = chapter['content'].split('\n')
                        for para in paragraphs:
                            if char_name in para and len(para) > 20:
                                contexts.append(para)
                                if len(contexts) >= 5:
                                    break
                    if len(contexts) >= 5:
                        break

                if contexts:
                    # 使用 AI 生成详细画像
                    ai_profile = self.ai_analyzer.enhance_character_profile(char_name, contexts)
                    if ai_profile:
                        character['ai_profile'] = ai_profile
                        logger.info(f"已为 {char_name} 生成 AI 画像")

            # 使用 AI 分析第一章来补充人物关系
            if chapters:
                first_chapter = chapters[0]['content']
                ai_char_analysis = self.ai_analyzer.analyze_characters(first_chapter, 1)

                if ai_char_analysis:
                    # 合并 AI 识别的关系
                    ai_relations = ai_char_analysis.get('relations', [])
                    traditional_result['ai_relations'] = ai_relations
                    logger.info(f"AI 识别了 {len(ai_relations)} 个额外关系")

        except Exception as e:
            logger.error(f"AI 人物分析增强失败: {e}")

        return traditional_result

    def enhance_timeline_analysis(
        self,
        traditional_result: Dict[str, Any],
        chapters: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        增强时间线分析

        Args:
            traditional_result: 传统分析结果
            chapters: 章节列表

        Returns:
            增强后的分析结果
        """
        if not self.ai_enabled:
            return traditional_result

        logger.info("使用 AI 增强时间线分析...")

        try:
            # 为关键章节生成 AI 事件分析
            ai_events = []
            for chapter in chapters[:5]:  # 限制前5章
                events = self.ai_analyzer.analyze_events(
                    chapter['content'],
                    chapter['chapter_number']
                )
                if events:
                    ai_events.extend(events)
                    logger.info(f"第 {chapter['chapter_number']} 章: AI 识别了 {len(events)} 个事件")

            if ai_events:
                traditional_result['ai_events'] = ai_events

            # 为每章生成摘要
            chapter_summaries = []
            for chapter in chapters[:10]:  # 限制前10章
                summary = self.ai_analyzer.summarize_chapter(
                    chapter['content'],
                    chapter['chapter_number']
                )
                if summary:
                    chapter_summaries.append({
                        'chapter': chapter['chapter_number'],
                        'summary': summary
                    })

            if chapter_summaries:
                traditional_result['chapter_summaries'] = chapter_summaries
                logger.info(f"生成了 {len(chapter_summaries)} 个章节摘要")

        except Exception as e:
            logger.error(f"AI 时间线分析增强失败: {e}")

        return traditional_result

    def enhance_emotion_analysis(
        self,
        traditional_result: Dict[str, Any],
        chapters: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        增强情感分析

        Args:
            traditional_result: 传统分析结果
            chapters: 章节列表

        Returns:
            增强后的分析结果
        """
        if not self.ai_enabled:
            return traditional_result

        logger.info("使用 AI 增强情感分析...")

        try:
            # 为关键章节进行 AI 情感分析
            ai_emotions = []
            for chapter in chapters[:5]:  # 限制前5章
                emotion = self.ai_analyzer.analyze_emotions(chapter['content'])
                if emotion:
                    emotion['chapter'] = chapter['chapter_number']
                    ai_emotions.append(emotion)
                    logger.info(f"第 {chapter['chapter_number']} 章: AI 情感分析完成")

            if ai_emotions:
                traditional_result['ai_emotions'] = ai_emotions

        except Exception as e:
            logger.error(f"AI 情感分析增强失败: {e}")

        return traditional_result

    def estimate_analysis_cost(self, novel_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        估算 AI 分析成本

        Args:
            novel_data: 小说数据

        Returns:
            成本估算
        """
        if not self.ai_enabled:
            return {"enabled": False, "cost": 0}

        total_length = sum(len(ch['content']) for ch in novel_data['chapters'])

        # 估算会使用的文本量（不是全部文本）
        # - 人物分析：前10章 + 主要人物上下文
        # - 事件分析：前5章
        # - 情感分析：前5章
        # - 章节摘要：前10章

        estimated_length = min(total_length, total_length * 0.3)  # 约30%的文本

        cost_info = self.ai_analyzer.estimate_cost(estimated_length)
        cost_info['enabled'] = True
        cost_info['provider'] = Config.AI_PROVIDER

        return cost_info

    def get_analysis_mode(self) -> str:
        """
        获取当前分析模式

        Returns:
            'traditional' 或 'hybrid'
        """
        return 'hybrid' if self.ai_enabled else 'traditional'
