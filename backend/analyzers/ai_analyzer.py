"""
AI 大模型分析器
使用 OpenAI/Claude API 进行高级分析
"""
import os
import logging
from typing import List, Dict, Any
import json

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """AI 大模型分析器"""

    def __init__(self, provider='openai', api_key=None):
        """
        初始化 AI 分析器

        Args:
            provider: 'openai' 或 'anthropic'
            api_key: API 密钥
        """
        self.provider = provider
        self.api_key = api_key or os.getenv(f'{provider.upper()}_API_KEY')

        if not self.api_key:
            logger.warning(f"未配置 {provider} API key，AI 增强功能将不可用")
            self.enabled = False
        else:
            self.enabled = True
            self._init_client()

    def _init_client(self):
        """初始化 API 客户端"""
        try:
            if self.provider == 'openai':
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
                self.model = "gpt-4o-mini"  # 使用性价比高的模型
            elif self.provider == 'anthropic':
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
                self.model = "claude-3-haiku-20240307"  # 使用快速模型
            logger.info(f"AI 分析器初始化成功: {self.provider}")
        except Exception as e:
            logger.error(f"AI 客户端初始化失败: {e}")
            self.enabled = False

    def analyze_chapter_structure(self, text: str, chapter: int) -> Dict[str, Any]:
        """
        [Step 1] 分析章节结构化摘要
        
        Args:
            text: 章节文本
            chapter: 章节号
            
        Returns:
            结构化摘要
        """
        if not self.enabled:
            return {}
            
        prompt = f"""请分析第 {chapter} 章，生成高浓度的结构化摘要（JSON格式）：

章节文本：
{text[:3000]} # 限制长度

请提取：
1. time: 时间点（如：深夜、三年后）
2. location: 主要地点
3. characters: 登场人物列表（仅名字）
4. summary: 剧情概要（100字以内，包含核心冲突和转折）
5. sentiment: 情感基调（如：紧张、悲伤、欢快）
6. key_event: 本章最重要的一个事件
7. potential_mysteries: 潜在的伏笔或未解之谜（列表，如"神秘的黑衣人身份"、"戒指里的灵魂"）

只返回 JSON，不要其他内容。"""

        try:
            result = self._call_api(prompt, max_tokens=500)
            return json.loads(result)
        except Exception as e:
            logger.error(f"AI 章节结构分析失败: {e}")
            return {
                "time": "未知",
                "location": "未知",
                "characters": [],
                "summary": "分析失败",
                "sentiment": "中性",
                "key_event": "未知",
                "potential_mysteries": []
            }

    def analyze_macro_window(self, summaries: List[Dict], start_chapter: int, end_chapter: int, unresolved_mysteries: List[str] = None) -> Dict[str, Any]:
        """
        [Step 2] 分析宏观窗口（基于摘要）
        
        Args:
            summaries: 章节摘要列表
            start_chapter: 起始章
            end_chapter: 结束章
            unresolved_mysteries: 当前未解决的谜题列表
            
        Returns:
            宏观分析结果
        """
        if not self.enabled:
            return {}
            
        # 将摘要转换为文本输入
        context = f"以下是小说第 {start_chapter} 章到第 {end_chapter} 章的剧情摘要：\n\n"
        for i, s in enumerate(summaries):
            context += f"第 {start_chapter + i} 章 [{s.get('time', '')} @ {s.get('location', '')}]: {s.get('summary', '')}\n"
        
        mysteries_text = ""
        if unresolved_mysteries:
            mysteries_text = "\n当前未解决的伏笔/谜题：\n" + "\n".join([f"- {m}" for m in unresolved_mysteries])
            
        prompt = f"""基于以上剧情摘要，请分析这段情节的宏观脉络（JSON格式）：

{context}
{mysteries_text}

请提取：
1. plot_arc: 剧情弧光（起承转合）
2. active_relations: 活跃的人物关系变化（如：A和B从误会到和解）
3. key_conflicts: 主要冲突点
4. characters: 关键人物及其在本阶段的作用
5. resolved_mysteries: 在本阶段得到解决或揭示的伏笔（从上述列表中选择并解释）

只返回 JSON，不要其他内容。"""

        try:
            result = self._call_api(prompt, max_tokens=1000)
            return json.loads(result)
        except Exception as e:
            logger.error(f"AI 宏观窗口分析失败: {e}")
            return {}

    def analyze_characters(self, text: str, chapter: int) -> Dict[str, Any]:
        """
        使用 AI 分析人物

        Args:
            text: 章节文本
            chapter: 章节号

        Returns:
            人物分析结果
        """
        if not self.enabled:
            return {}

        prompt = f"""请分析以下小说章节中的人物信息，以 JSON 格式返回：

章节文本：
{text[:2000]}  # 限制长度

请提取：
1. characters: 人物列表，每个人物包含 name（名字）、aliases（别名列表）、description（描述）
2. relations: 人物关系列表，每个关系包含 from（人物1）、to（人物2）、type（关系类型）、description（关系描述）

只返回 JSON，不要其他内容。"""

        try:
            result = self._call_api(prompt)
            return json.loads(result)
        except Exception as e:
            logger.error(f"AI 人物分析失败: {e}")
            return {}

    def analyze_events(self, text: str, chapter: int) -> List[Dict[str, Any]]:
        """
        使用 AI 分析事件

        Args:
            text: 章节文本
            chapter: 章节号

        Returns:
            事件列表
        """
        if not self.enabled:
            return []

        prompt = f"""请分析以下小说章节中的关键事件，以 JSON 数组格式返回：

章节文本：
{text[:2000]}

请提取每个事件的：
1. description: 事件描述（一句话概括）
2. participants: 参与人物列表
3. location: 发生地点
4. importance: 重要性评分（0-1）
5. event_type: 事件类型（如：相遇、冲突、合作、转折等）

只返回 JSON 数组，不要其他内容。"""

        try:
            result = self._call_api(prompt)
            return json.loads(result)
        except Exception as e:
            logger.error(f"AI 事件分析失败: {e}")
            return []

    def analyze_emotions(self, text: str) -> Dict[str, Any]:
        """
        使用 AI 分析情感

        Args:
            text: 文本

        Returns:
            情感分析结果
        """
        if not self.enabled:
            return {}

        prompt = f"""请分析以下文本的情感，以 JSON 格式返回：

文本：
{text[:1000]}

请返回：
1. sentiment: 整体情感值（-1到1，负数为消极，正数为积极）
2. emotions: 情感类型及强度，包含 joy（喜悦）、sadness（悲伤）、anger（愤怒）、fear（恐惧）、surprise（惊讶）、disgust（厌恶）
3. emotional_peaks: 情感高潮点描述

只返回 JSON，不要其他内容。"""

        try:
            result = self._call_api(prompt)
            return json.loads(result)
        except Exception as e:
            logger.error(f"AI 情感分析失败: {e}")
            return {}

    def enhance_character_profile(self, character_name: str, contexts: List[str]) -> Dict[str, Any]:
        """
        使用 AI 增强人物画像

        Args:
            character_name: 人物名称
            contexts: 人物相关的文本片段列表

        Returns:
            增强的人物画像
        """
        if not self.enabled:
            return {}

        context_text = "\n\n".join(contexts[:5])  # 限制上下文数量

        prompt = f"""请为小说人物 "{character_name}" 生成详细画像，基于以下文本片段：

{context_text[:3000]}

请以 JSON 格式返回：
1. personality: 性格特点列表
2. appearance: 外貌描述
3. background: 背景故事
4. motivations: 动机和目标
5. character_arc: 人物成长轨迹

只返回 JSON，不要其他内容。"""

        try:
            result = self._call_api(prompt)
            return json.loads(result)
        except Exception as e:
            logger.error(f"AI 人物画像增强失败: {e}")
            return {}

    def summarize_chapter(self, text: str, chapter: int) -> str:
        """
        使用 AI 总结章节

        Args:
            text: 章节文本
            chapter: 章节号

        Returns:
            章节摘要
        """
        if not self.enabled:
            return ""

        prompt = f"""请用 2-3 句话总结以下章节的主要内容：

第 {chapter} 章：
{text[:2000]}

只返回摘要文本，不要其他内容。"""

        try:
            return self._call_api(prompt)
        except Exception as e:
            logger.error(f"AI 章节总结失败: {e}")
            return ""

    def _call_api(self, prompt: str, max_tokens: int = 2000) -> str:
        """
        调用 AI API

        Args:
            prompt: 提示词
            max_tokens: 最大 token 数

        Returns:
            API 响应文本
        """
        try:
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "你是一个专业的小说分析助手，擅长提取人物、事件、情感等信息。"},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=0.3  # 降低随机性，提高一致性
                )
                return response.choices[0].message.content

            elif self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=0.3,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.content[0].text

        except Exception as e:
            logger.error(f"API 调用失败: {e}")
            raise

    def estimate_cost(self, text_length: int) -> Dict[str, float]:
        """
        估算分析成本

        Args:
            text_length: 文本长度（字符数）

        Returns:
            成本估算（美元）
        """
        # 粗略估算：1000 字符 ≈ 250 tokens
        tokens = text_length / 4

        if self.provider == 'openai':
            # GPT-4o-mini 价格：$0.15/1M input tokens, $0.60/1M output tokens
            input_cost = (tokens / 1_000_000) * 0.15
            output_cost = (tokens / 4 / 1_000_000) * 0.60  # 假设输出是输入的 1/4
            total = input_cost + output_cost
        elif self.provider == 'anthropic':
            # Claude 3 Haiku 价格：$0.25/1M input tokens, $1.25/1M output tokens
            input_cost = (tokens / 1_000_000) * 0.25
            output_cost = (tokens / 4 / 1_000_000) * 1.25
            total = input_cost + output_cost
        else:
            input_cost = output_cost = total = 0

        return {
            "input_cost": round(input_cost, 4),
            "output_cost": round(output_cost, 4),
            "total_cost": round(total, 4),
            "tokens": int(tokens)
        }
