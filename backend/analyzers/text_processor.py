"""
文本处理器
提供文本分词、分句等基础处理功能
"""
import jieba
import jieba.posseg as pseg
import re
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class TextProcessor:
    """文本处理器类"""

    def __init__(self):
        """初始化文本处理器"""
        self.stopwords = self._load_stopwords()
        logger.info("TextProcessor initialized")

    def _load_stopwords(self) -> set:
        """
        加载停用词表

        Returns:
            停用词集合
        """
        stopwords = set()
        try:
            with open('data/stopwords.txt', 'r', encoding='utf-8') as f:
                stopwords = set(line.strip() for line in f if line.strip())
            logger.info(f"Loaded {len(stopwords)} stopwords")
        except FileNotFoundError:
            logger.warning("Stopwords file not found, using default set")
            # 默认停用词
            stopwords = {'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'}

        return stopwords

    def segment(self, text: str, remove_stopwords: bool = False) -> List[str]:
        """
        分词

        Args:
            text: 输入文本
            remove_stopwords: 是否移除停用词

        Returns:
            分词结果列表
        """
        words = jieba.lcut(text)

        if remove_stopwords:
            words = [w for w in words if w not in self.stopwords and w.strip()]

        return words

    def segment_with_pos(self, text: str) -> List[Tuple[str, str]]:
        """
        分词并标注词性

        Args:
            text: 输入文本

        Returns:
            (词, 词性) 元组列表
        """
        return [(word, flag) for word, flag in pseg.cut(text)]

    def split_sentences(self, text: str) -> List[str]:
        """
        分句

        Args:
            text: 输入文本

        Returns:
            句子列表
        """
        # 使用标点符号分句
        sentences = re.split(r'[。！？!?；;]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences

    def extract_names(self, text: str) -> List[str]:
        """
        提取人名

        Args:
            text: 输入文本

        Returns:
            人名列表
        """
        words_with_pos = self.segment_with_pos(text)
        names = [word for word, pos in words_with_pos if pos == 'nr']
        return names

    def extract_locations(self, text: str) -> List[str]:
        """
        提取地名

        Args:
            text: 输入文本

        Returns:
            地名列表
        """
        words_with_pos = self.segment_with_pos(text)
        locations = [word for word, pos in words_with_pos if pos == 'ns']
        return locations

    def clean_text(self, text: str) -> str:
        """
        清洗文本

        Args:
            text: 输入文本

        Returns:
            清洗后的文本
        """
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)

        # 移除特殊字符（保留中文、英文、数字和常用标点）
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9，。！？；：""''（）《》、\s]', '', text)

        return text.strip()

    def extract_dialogues(self, text: str) -> List[Dict]:
        """
        提取对话

        Args:
            text: 输入文本

        Returns:
            对话列表，每个对话包含speaker和content
        """
        dialogues = []

        # 匹配引号内的内容
        patterns = [
            r'"([^"]+)"',  # 双引号
            r'"([^"]+)"',  # 中文双引号
            r''([^']+)'',  # 中文单引号
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                content = match.group(1)
                # 尝试提取说话人（简单实现）
                start_pos = match.start()
                context_before = text[max(0, start_pos-20):start_pos]

                speaker = "未知"
                # 查找"XX说"、"XX道"等模式
                speaker_match = re.search(r'([^，。！？；：\s]{2,4})(说|道|问|答|笑|叹|喊)', context_before)
                if speaker_match:
                    speaker = speaker_match.group(1)

                dialogues.append({
                    "speaker": speaker,
                    "content": content,
                    "position": start_pos
                })

        return dialogues

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算两段文本的相似度（简单实现：基于共同词汇）

        Args:
            text1: 文本1
            text2: 文本2

        Returns:
            相似度分数 (0-1)
        """
        words1 = set(self.segment(text1, remove_stopwords=True))
        words2 = set(self.segment(text2, remove_stopwords=True))

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union) if union else 0.0

    def get_word_frequency(self, text: str, top_n: int = 20) -> List[Tuple[str, int]]:
        """
        获取词频统计

        Args:
            text: 输入文本
            top_n: 返回前N个高频词

        Returns:
            (词, 频次) 元组列表
        """
        from collections import Counter

        words = self.segment(text, remove_stopwords=True)
        # 过滤单字词
        words = [w for w in words if len(w) > 1]

        counter = Counter(words)
        return counter.most_common(top_n)
