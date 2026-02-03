"""
API路由定义
"""
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import logging
from config.config import Config
from backend.database.neo4j_client import Neo4jClient
from backend.parsers.txt_parser import TxtParser
from backend.extractors.entity_extractor import EntityExtractor
from backend.analyzers.character_analyzer import CharacterAnalyzer
from backend.analyzers.timeline_analyzer import TimelineAnalyzer
from backend.analyzers.location_analyzer import LocationAnalyzer
from backend.analyzers.emotion_analyzer import EmotionAnalyzer
from backend.analyzers.state_tracker import StateTracker

logger = logging.getLogger(__name__)

# 创建蓝图
api_bp = Blueprint('api', __name__)

# 全局存储分析结果（生产环境应使用Redis等）
analysis_cache = {}


def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


@api_bp.route('/upload', methods=['POST'])
def upload_file():
    """上传小说文件"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed"}), 400

        # 保存文件
        filename = secure_filename(file.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)

        logger.info(f"File uploaded: {filename}")

        return jsonify({
            "message": "File uploaded successfully",
            "filename": filename,
            "filepath": filepath
        }), 200

    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/analyze', methods=['POST'])
def analyze_novel():
    """分析小说"""
    try:
        data = request.get_json()
        filepath = data.get('filepath')

        if not filepath or not os.path.exists(filepath):
            return jsonify({"error": "File not found"}), 404

        logger.info(f"Starting analysis for: {filepath}")

        # 1. 解析小说
        parser = TxtParser()
        novel_data = parser.parse(filepath)

        # 2. 提取实体
        extractor = EntityExtractor(min_mentions=2)
        entities = extractor.extract_entities_from_novel(novel_data)

        # 3. 分析人物关系
        char_analyzer = CharacterAnalyzer()
        char_analysis = char_analyzer.analyze(
            novel_data['chapters'],
            entities['characters']
        )

        # 4. 分析时间线
        timeline_analyzer = TimelineAnalyzer()
        timeline_analysis = timeline_analyzer.analyze(
            novel_data['chapters'],
            char_analysis['characters'],
            char_analysis['relations']
        )

        # 5. 分析地点
        location_analyzer = LocationAnalyzer()
        location_analysis = location_analyzer.analyze(
            novel_data['chapters'],
            entities['locations'],
            char_analysis['characters'],
            timeline_analysis['events']
        )

        # 6. 分析情感
        emotion_analyzer = EmotionAnalyzer()
        emotion_analysis = emotion_analyzer.analyze(
            novel_data['chapters'],
            char_analysis['characters'],
            timeline_analysis['events']
        )

        # 7. 追踪状态
        state_tracker = StateTracker()
        state_analysis = state_tracker.analyze(
            novel_data['chapters'],
            char_analysis['characters'],
            timeline_analysis['events']
        )

        # 生成分析ID
        novel_id = os.path.basename(filepath).replace('.txt', '')

        # 缓存结果
        analysis_cache[novel_id] = {
            "novel_data": novel_data,
            "entities": entities,
            "char_analysis": char_analysis,
            "timeline_analysis": timeline_analysis,
            "location_analysis": location_analysis,
            "emotion_analysis": emotion_analysis,
            "state_analysis": state_analysis
        }

        logger.info(f"Analysis completed for: {novel_id}")

        return jsonify({
            "message": "Analysis completed",
            "novel_id": novel_id,
            "statistics": {
                "chapters": novel_data['total_chapters'],
                "words": novel_data['total_words'],
                "characters": len(char_analysis['characters']),
                "relations": len(char_analysis['relations']),
                "events": len(timeline_analysis['events']),
                "locations": len(location_analysis['locations'])
            }
        }), 200

    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@api_bp.route('/novels', methods=['GET'])
def get_novels():
    """获取已分析的小说列表"""
    try:
        novels = []
        for novel_id, data in analysis_cache.items():
            novels.append({
                "id": novel_id,
                "title": data['novel_data']['metadata']['title'],
                "author": data['novel_data']['metadata']['author'],
                "chapters": data['novel_data']['total_chapters'],
                "words": data['novel_data']['total_words']
            })

        return jsonify({"novels": novels}), 200

    except Exception as e:
        logger.error(f"Error getting novels: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/novel/<novel_id>/characters', methods=['GET'])
def get_characters(novel_id):
    """获取人物列表"""
    try:
        if novel_id not in analysis_cache:
            return jsonify({"error": "Novel not found"}), 404

        char_analysis = analysis_cache[novel_id]['char_analysis']

        characters = [{
            "id": char["id"],
            "name": char["name"],
            "importance": char.get("final_importance", char.get("importance", 0)),
            "mention_count": char["mention_count"],
            "first_appearance": char["first_appearance"],
            "degree_centrality": char.get("degree_centrality", 0)
        } for char in char_analysis['characters']]

        return jsonify({"characters": characters}), 200

    except Exception as e:
        logger.error(f"Error getting characters: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/novel/<novel_id>/graph', methods=['GET'])
def get_graph(novel_id):
    """获取关系图谱数据"""
    try:
        if novel_id not in analysis_cache:
            return jsonify({"error": "Novel not found"}), 404

        char_analysis = analysis_cache[novel_id]['char_analysis']

        # 构建节点
        nodes = [{
            "id": char["id"],
            "label": char["name"],
            "importance": char.get("final_importance", 0),
            "type": "main" if char in char_analysis['main_characters'] else "supporting"
        } for char in char_analysis['characters']]

        # 构建边
        edges = [{
            "id": f"edge_{i}",
            "source": rel["from"],
            "target": rel["to"],
            "label": rel["relationship_type"],
            "strength": rel["strength"]
        } for i, rel in enumerate(char_analysis['relations'])]

        return jsonify({
            "nodes": nodes,
            "edges": edges
        }), 200

    except Exception as e:
        logger.error(f"Error getting graph: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/novel/<novel_id>/timeline', methods=['GET'])
def get_timeline(novel_id):
    """获取时间线数据"""
    try:
        if novel_id not in analysis_cache:
            return jsonify({"error": "Novel not found"}), 404

        timeline_analysis = analysis_cache[novel_id]['timeline_analysis']

        events = [{
            "id": event["id"],
            "description": event["description"][:100],
            "chapter": event["chapter"],
            "sequence": event["sequence"],
            "event_type": event["event_type"],
            "importance_score": event.get("importance_score", 0),
            "contribution_score": event.get("contribution_score", 0),
            "participants": event["participants"]
        } for event in timeline_analysis['timeline']]

        return jsonify({
            "events": events,
            "main_plot_events": [e["id"] for e in timeline_analysis['main_plot_events']]
        }), 200

    except Exception as e:
        logger.error(f"Error getting timeline: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/novel/<novel_id>/locations', methods=['GET'])
def get_locations(novel_id):
    """获取地点数据"""
    try:
        if novel_id not in analysis_cache:
            return jsonify({"error": "Novel not found"}), 404

        location_analysis = analysis_cache[novel_id]['location_analysis']

        locations = [{
            "id": loc["id"],
            "name": loc["name"],
            "type": loc["type"],
            "importance": loc["importance"],
            "event_count": loc["event_count"]
        } for loc in location_analysis['locations']]

        return jsonify({"locations": locations}), 200

    except Exception as e:
        logger.error(f"Error getting locations: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/novel/<novel_id>/emotions', methods=['GET'])
def get_emotions(novel_id):
    """获取情感数据"""
    try:
        if novel_id not in analysis_cache:
            return jsonify({"error": "Novel not found"}), 404

        emotion_analysis = analysis_cache[novel_id]['emotion_analysis']

        return jsonify({
            "chapter_emotions": emotion_analysis['chapter_emotions'],
            "emotion_curve": emotion_analysis['emotion_curve'],
            "emotional_peaks": emotion_analysis['emotional_peaks'],
            "statistics": emotion_analysis['statistics']
        }), 200

    except Exception as e:
        logger.error(f"Error getting emotions: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/character/<novel_id>/<character_name>', methods=['GET'])
def get_character_profile(novel_id, character_name):
    """获取人物详细信息"""
    try:
        if novel_id not in analysis_cache:
            return jsonify({"error": "Novel not found"}), 404

        cache = analysis_cache[novel_id]
        char_analysis = cache['char_analysis']
        location_analysis = cache['location_analysis']
        emotion_analysis = cache['emotion_analysis']
        state_analysis = cache['state_analysis']

        # 查找人物
        character = None
        for char in char_analysis['characters']:
            if char['name'] == character_name:
                character = char
                break

        if not character:
            return jsonify({"error": "Character not found"}), 404

        # 获取关系
        relations = [
            rel for rel in char_analysis['relations']
            if rel['from'] == character_name or rel['to'] == character_name
        ]

        # 获取地点轨迹
        locations = location_analysis['character_location_map'].get(character_name, [])

        # 获取情感
        emotions = emotion_analysis['character_emotions'].get(character_name, [])

        # 获取状态
        states = state_analysis['character_states'].get(character_name, [])

        profile = {
            "basic_info": character,
            "relations": relations,
            "locations": locations[:10],
            "emotions": emotions[:10],
            "states": states[:10]
        }

        return jsonify(profile), 200

    except Exception as e:
        logger.error(f"Error getting character profile: {e}")
        return jsonify({"error": str(e)}), 500
