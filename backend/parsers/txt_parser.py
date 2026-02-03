"""
TXT文件解析器
解析纯文本格式的小说文件
"""
import re
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class TxtParser:
    """TXT文件解析器类"""

    def __init__(self):
        """初始化解析器"""
        self.chapter_patterns = [
            r'^第[零一二三四五六七八九十百千万\d]+章',  # 第X章
            r'^第[零一二三四五六七八九十百千万\d]+回',  # 第X回
            r'^Chapter\s+\d+',  # Chapter X
            r'^\d+\.',  # 1.
            r'^\d+、',  # 1、
        ]

    def parse(self, file_path: str, encoding: str = 'utf-8') -> Dict:
        """
        解析TXT文件

        Args:
            file_path: 文件路径
            encoding: 文件编码

        Returns:
            解析后的小说数据
        """
        logger.info(f"Parsing TXT file: {file_path}")

        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
        except UnicodeDecodeError:
            # 尝试其他编码
            logger.warning(f"Failed to decode with {encoding}, trying gbk")
            with open(file_path, 'r', encoding='gbk') as f:
                content = f.read()

        # 分割章节
        chapters = self._split_chapters(content)

        # 提取元数据
        metadata = self._extract_metadata(content, file_path)

        result = {
            "metadata": metadata,
            "chapters": chapters,
            "total_chapters": len(chapters),
            "total_words": sum(ch["word_count"] for ch in chapters)
        }

        logger.info(f"Parsed {len(chapters)} chapters, {result['total_words']} words")
        return result

    def _split_chapters(self, content: str) -> List[Dict]:
        """
        分割章节

        Args:
            content: 文本内容

        Returns:
            章节列表
        """
        chapters = []
        lines = content.split('\n')

        current_chapter = None
        current_content = []
        chapter_number = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 检查是否是章节标题
            is_chapter_title = False
            for pattern in self.chapter_patterns:
                if re.match(pattern, line):
                    is_chapter_title = True
                    break

            if is_chapter_title:
                # 保存上一章节
                if current_chapter is not None:
                    current_chapter["content"] = '\n'.join(current_content)
                    current_chapter["word_count"] = len(current_chapter["content"])
                    current_chapter["paragraphs"] = self._split_paragraphs(current_chapter["content"])
                    chapters.append(current_chapter)

                # 开始新章节
                chapter_number += 1
                current_chapter = {
                    "number": chapter_number,
                    "title": line,
                    "content": "",
                    "word_count": 0,
                    "paragraphs": []
                }
                current_content = []
            else:
                # 添加到当前章节内容
                if current_chapter is not None:
                    current_content.append(line)

        # 保存最后一章
        if current_chapter is not None:
            current_chapter["content"] = '\n'.join(current_content)
            current_chapter["word_count"] = len(current_chapter["content"])
            current_chapter["paragraphs"] = self._split_paragraphs(current_chapter["content"])
            chapters.append(current_chapter)

        # 如果没有识别到章节，将整个文本作为一章
        if not chapters:
            chapters.append({
                "number": 1,
                "title": "全文",
                "content": content,
                "word_count": len(content),
                "paragraphs": self._split_paragraphs(content)
            })

        return chapters

    def _split_paragraphs(self, content: str) -> List[str]:
        """
        分割段落

        Args:
            content: 章节内容

        Returns:
            段落列表
        """
        # 按空行分割段落
        paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
        return paragraphs

    def _extract_metadata(self, content: str, file_path: str) -> Dict:
        """
        提取元数据

        Args:
            content: 文本内容
            file_path: 文件路径

        Returns:
            元数据字典
        """
        import os

        metadata = {
            "title": os.path.basename(file_path).replace('.txt', ''),
            "author": "未知",
            "source": file_path,
            "format": "txt"
        }

        # 尝试从文本开头提取标题和作者
        lines = content.split('\n')[:10]  # 只检查前10行
        for line in lines:
            line = line.strip()
            if '作者' in line or 'Author' in line.lower():
                # 提取作者名
                author = re.sub(r'作者[：:]\s*', '', line)
                author = re.sub(r'Author[：:]\s*', '', author, flags=re.IGNORECASE)
                if author:
                    metadata["author"] = author.strip()
            elif '书名' in line or 'Title' in line.lower():
                # 提取书名
                title = re.sub(r'书名[：:]\s*', '', line)
                title = re.sub(r'Title[：:]\s*', '', title, flags=re.IGNORECASE)
                if title:
                    metadata["title"] = title.strip()

        return metadata

    def get_chapter_content(self, parsed_data: Dict, chapter_number: int) -> Optional[str]:
        """
        获取指定章节的内容

        Args:
            parsed_data: 解析后的数据
            chapter_number: 章节号

        Returns:
            章节内容或None
        """
        for chapter in parsed_data["chapters"]:
            if chapter["number"] == chapter_number:
                return chapter["content"]
        return None

    def get_chapter_range(self, parsed_data: Dict, start: int, end: int) -> List[Dict]:
        """
        获取指定范围的章节

        Args:
            parsed_data: 解析后的数据
            start: 起始章节号
            end: 结束章节号

        Returns:
            章节列表
        """
        return [
            ch for ch in parsed_data["chapters"]
            if start <= ch["number"] <= end
        ]
