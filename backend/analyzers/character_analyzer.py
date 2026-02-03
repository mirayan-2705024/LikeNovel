"""
人物关系分析器
分析人物之间的关系网络
"""
from typing import List, Dict
import logging
from ..extractors.relation_extractor import RelationExtractor

logger = logging.getLogger(__name__)


class CharacterAnalyzer:
    """人物关系分析器类"""

    def __init__(self):
        """初始化人物关系分析器"""
        self.relation_extractor = RelationExtractor()
        logger.info("CharacterAnalyzer initialized")

    def analyze(
        self,
        chapters: List[Dict],
        characters: List[Dict]
    ) -> Dict:
        """
        分析人物关系

        Args:
            chapters: 章节列表
            characters: 人物列表

        Returns:
            分析结果
        """
        logger.info("Analyzing character relationships...")

        # 提取关系
        relations = self.relation_extractor.extract_relations_from_chapters(
            chapters, characters
        )

        # 计算人物的网络中心度
        characters_with_centrality = self._calculate_centrality(
            characters, relations
        )

        # 识别主要人物和次要人物
        main_characters, supporting_characters = self._classify_characters(
            characters_with_centrality
        )

        # 构建关系网络
        network = self._build_relationship_network(
            characters_with_centrality, relations
        )

        result = {
            "characters": characters_with_centrality,
            "main_characters": main_characters,
            "supporting_characters": supporting_characters,
            "relations": relations,
            "network": network,
            "statistics": {
                "total_characters": len(characters),
                "main_characters_count": len(main_characters),
                "supporting_characters_count": len(supporting_characters),
                "total_relations": len(relations)
            }
        }

        logger.info(f"Analysis complete: {len(main_characters)} main characters, "
                   f"{len(supporting_characters)} supporting characters, "
                   f"{len(relations)} relations")

        return result

    def _calculate_centrality(
        self,
        characters: List[Dict],
        relations: List[Dict]
    ) -> List[Dict]:
        """
        计算人物的网络中心度

        Args:
            characters: 人物列表
            relations: 关系列表

        Returns:
            带有中心度的人物列表
        """
        # 计算每个人物的度中心性（连接数）
        degree = {char["name"]: 0 for char in characters}

        for rel in relations:
            degree[rel["from"]] += 1
            degree[rel["to"]] += 1

        # 更新人物信息
        result = []
        for char in characters:
            char_copy = char.copy()
            char_copy["degree_centrality"] = degree[char["name"]]
            # 综合重要性：考虑提及次数、中心度和首次出现
            char_copy["final_importance"] = self._calculate_final_importance(
                char_copy
            )
            result.append(char_copy)

        # 按重要性排序
        result.sort(key=lambda x: x["final_importance"], reverse=True)

        return result

    def _calculate_final_importance(self, character: Dict) -> float:
        """
        计算人物的最终重要性分数

        Args:
            character: 人物信息

        Returns:
            重要性分数
        """
        # 权重分配
        mention_weight = 0.4
        centrality_weight = 0.4
        early_appearance_weight = 0.2

        # 提及次数分数（归一化）
        mention_score = min(character["mention_count"] / 50, 1.0)

        # 中心度分数（归一化）
        centrality_score = min(character["degree_centrality"] / 10, 1.0)

        # 早期出现分数（越早出现分数越高）
        early_score = 1.0 / character["first_appearance"]

        final_score = (
            mention_score * mention_weight +
            centrality_score * centrality_weight +
            early_score * early_appearance_weight
        )

        return final_score

    def _classify_characters(
        self,
        characters: List[Dict]
    ) -> tuple:
        """
        分类主要人物和次要人物

        Args:
            characters: 人物列表

        Returns:
            (主要人物列表, 次要人物列表)
        """
        # 使用重要性阈值分类
        threshold = 0.3

        main_characters = [
            char for char in characters
            if char["final_importance"] >= threshold
        ]

        supporting_characters = [
            char for char in characters
            if char["final_importance"] < threshold
        ]

        return main_characters, supporting_characters

    def _build_relationship_network(
        self,
        characters: List[Dict],
        relations: List[Dict]
    ) -> Dict:
        """
        构建关系网络

        Args:
            characters: 人物列表
            relations: 关系列表

        Returns:
            网络结构
        """
        # 构建邻接表
        adjacency = {char["name"]: [] for char in characters}

        for rel in relations:
            adjacency[rel["from"]].append({
                "target": rel["to"],
                "type": rel["relationship_type"],
                "strength": rel["strength"]
            })
            adjacency[rel["to"]].append({
                "target": rel["from"],
                "type": rel["relationship_type"],
                "strength": rel["strength"]
            })

        # 识别社区/群组
        communities = self._detect_communities(adjacency, relations)

        network = {
            "adjacency": adjacency,
            "communities": communities,
            "density": self._calculate_network_density(
                len(characters), len(relations)
            )
        }

        return network

    def _detect_communities(
        self,
        adjacency: Dict,
        relations: List[Dict]
    ) -> List[List[str]]:
        """
        检测社区/群组（简单实现）

        Args:
            adjacency: 邻接表
            relations: 关系列表

        Returns:
            社区列表
        """
        # 简单的连通分量检测
        visited = set()
        communities = []

        def dfs(node, community):
            visited.add(node)
            community.append(node)
            for neighbor in adjacency.get(node, []):
                if neighbor["target"] not in visited:
                    dfs(neighbor["target"], community)

        for node in adjacency:
            if node not in visited:
                community = []
                dfs(node, community)
                if len(community) > 1:  # 只保留有多个成员的社区
                    communities.append(community)

        return communities

    def _calculate_network_density(
        self,
        num_nodes: int,
        num_edges: int
    ) -> float:
        """
        计算网络密度

        Args:
            num_nodes: 节点数
            num_edges: 边数

        Returns:
            密度值
        """
        if num_nodes <= 1:
            return 0.0

        max_edges = num_nodes * (num_nodes - 1) / 2
        return num_edges / max_edges if max_edges > 0 else 0.0

    def get_character_profile(
        self,
        character_name: str,
        analysis_result: Dict
    ) -> Dict:
        """
        获取人物的完整画像

        Args:
            character_name: 人物名称
            analysis_result: 分析结果

        Returns:
            人物画像
        """
        # 查找人物信息
        character = None
        for char in analysis_result["characters"]:
            if char["name"] == character_name:
                character = char
                break

        if not character:
            return {}

        # 查找相关关系
        related_relations = [
            rel for rel in analysis_result["relations"]
            if rel["from"] == character_name or rel["to"] == character_name
        ]

        # 获取关系网络
        network_neighbors = analysis_result["network"]["adjacency"].get(
            character_name, []
        )

        profile = {
            "basic_info": character,
            "relations": related_relations,
            "network_neighbors": network_neighbors,
            "is_main_character": character in analysis_result["main_characters"]
        }

        return profile
