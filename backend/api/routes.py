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


@api_bp.route('/analyze/async', methods=['POST'])
def analyze_novel_async():
    """异步分析小说"""
    try:
        data = request.get_json()
        filepath = data.get('filepath')

        if not filepath or not os.path.exists(filepath):
            return jsonify({"error": "File not found"}), 404

        # 创建任务ID
        task_id = str(uuid.uuid4())
        
        # 初始化任务状态
        tasks[task_id] = {
            'status': 'pending',
            'progress': 0,
            'message': '等待开始...',
            'created_at': time.time()
        }
        
        # 启动后台线程
        thread = threading.Thread(target=run_analysis_task, args=(task_id, filepath))
        thread.daemon = True
        thread.start()

        return jsonify({
            "message": "Analysis started",
            "task_id": task_id
        }), 202

    except Exception as e:
        logger.error(f"Async analysis error: {e}")
        return jsonify({"error": str(e)}), 500


@api_bp.route('/tasks/<task_id>', methods=['GET'])
def get_task_status(task_id):
    """获取任务状态"""
    task = tasks.get(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    return jsonify(task), 200


@api_bp.route('/analyze', methods=['POST'])
def analyze_novel():
    """分析小说"""
    try:
        data = request.get_json()
        filepath = data.get('filepath')

        if not filepath or not os.path.exists(filepath):
            return jsonify({"error": "File not found"}), 404

        logger.info(f"Starting analysis for: {filepath}")

        tasks[task_id]['message'] = '正在解析小说文本...'
        parser = TxtParser()
        novel_data = parser.parse(filepath)
        tasks[task_id]['progress'] = 10

        # 根据配置决定分析模式
        analysis_mode = Config.ANALYSIS_MODE
        
        if analysis_mode == 'pure_ai':
            # === 纯 AI 模式：双层滑动窗口 (Micro + Macro) ===
            tasks[task_id]['message'] = '正在初始化双层 AI 扫描...'
            hybrid_analyzer = HybridAnalyzer()
            if not hybrid_analyzer.ai_enabled:
                 raise Exception("纯 AI 模式需要配置有效的 API Key")
            
            # 全局数据容器
            all_characters = {}
            all_relations = []
            plot_structure = []  # Layer 1 结果
            macro_structure = [] # Layer 2 结果
            chapter_summaries = [] # 缓存所有章节摘要
            
            # 伏笔追踪系统
            mystery_registry = [] 
            unresolved_mysteries = []
            
            # === 全局档案库 (v0.7.0) ===
            global_archives = {
                "characters": {},  # name -> [{chapter, event, status}]
                "items": {},       # name -> [{chapter, event, status}]
                "locations": {}    # name -> [{chapter, event, status}]
            }
            
            # Layer 1 参数 (微观窗口)
            micro_window_size = 5
            micro_step = 5 # 不重叠，因为我们要生成连续的摘要序列
            
            # Layer 2 参数 (宏观窗口)
            macro_window_size = 25 # 25章
            macro_step = 25 # 也不重叠，简化处理
            
            total_chapters = len(novel_data['chapters'])
            
            # 限制分析范围（防止 token 爆炸）
            max_chapters = 50 # 限制分析前50章 (即2个宏观窗口)
            processing_chapters = min(total_chapters, max_chapters)
            
            num_micro_windows = (processing_chapters // micro_step) + (1 if processing_chapters % micro_step > 0 else 0)
            
            logger.info(f"Starting hierarchical analysis: {num_micro_windows} micro windows")
            
            # === Layer 1: 微观分析循环 ===
            for i in range(num_micro_windows):
                start_idx = i * micro_step
                end_idx = min(start_idx + micro_window_size, processing_chapters)
                
                if start_idx >= processing_chapters:
                    break
                
                # 准备当前窗口文本
                window_chapters = novel_data['chapters'][start_idx:end_idx]
                window_text = "\n".join([c['content'] for c in window_chapters])
                
                # 更新进度
                progress = 10 + int((i / num_micro_windows) * 60) # Layer 1 占 60% 进度
                tasks[task_id]['progress'] = progress
                tasks[task_id]['message'] = f'[L1微观] 分析第 {start_idx+1}-{end_idx} 章...'
                
                try:
                    # 1. 详细分析当前窗口 (提取人物、关系)
                    micro_result = hybrid_analyzer.ai_analyzer.analyze_characters(window_text, start_idx+1)
                    
                    # 合并人物
                    for char in micro_result.get('characters', []):
                        name = char['name']
                        if name not in all_characters:
                            all_characters[name] = {
                                "id": f"char_{name}",
                                "name": name,
                                "mention_count": 0,
                                "first_appearance": start_idx + 1,
                                "importance": 0.0,
                                "aliases": char.get('aliases', [])
                            }
                        all_characters[name]['mention_count'] += 1
                    
                    # 收集关系
                    for rel in micro_result.get('relations', []):
                        all_relations.append({
                            "from": rel['from'],
                            "to": rel['to'],
                            "relationship_type": rel['type'],
                            "strength": 0.5,
                            "chapter": start_idx + 1,
                            "window_index": i
                        })
                    
                    # 2. 生成单章摘要 (为 Layer 2 做准备)
                    # 这里的优化点：其实可以让 analyze_characters 同时返回摘要，节省一次 API 调用
                    # 但为了结构清晰，我们这里简单模拟生成摘要
                    # 实际生产中应该在 analyze_characters 的 prompt 里加一项 "summary"
                    
                    # 临时方案：对窗口内的每一章，简单生成一个摘要
                    for idx, chapter in enumerate(window_chapters):
                        chap_num = start_idx + idx + 1
                        # 这是一个轻量级调用，或者可以复用 micro_result 里的信息
                        summary_data = hybrid_analyzer.ai_analyzer.analyze_chapter_structure(chapter['content'], chap_num)
                        chapter_summaries.append(summary_data)
                        
                        # 添加到剧情结构图
                        plot_structure.append({
                            "id": f"plot_{chap_num}",
                            "range": str(chap_num),
                            "summary": summary_data.get('summary', '无摘要'),
                            "key_event": summary_data.get('key_event', '未知')
                        })
                        
                        # === 伏笔追踪：注册新伏笔 ===
                        new_mysteries = summary_data.get('potential_mysteries', [])
                        for m in new_mysteries:
                            mystery_registry.append({
                                "id": f"mys_{uuid.uuid4().hex[:8]}",
                                "content": m,
                                "setup_chapter": chap_num,
                                "status": "unresolved"
                            })
                            unresolved_mysteries.append(m)
                        
                except Exception as e:
                    logger.error(f"Micro window {i} failed: {e}")
                    continue

            # === Layer 2: 宏观分析循环 ===
            num_macro_windows = (len(chapter_summaries) // macro_window_size) + (1 if len(chapter_summaries) % macro_window_size > 0 else 0)
            
            for j in range(num_macro_windows):
                start_chap = j * macro_window_size
                end_chap = min(start_chap + macro_window_size, len(chapter_summaries))
                
                if start_chap >= len(chapter_summaries):
                    break
                    
                # 更新进度
                progress = 70 + int((j / num_macro_windows) * 25) # Layer 2 占 25% 进度
                tasks[task_id]['progress'] = progress
                tasks[task_id]['message'] = f'[L2宏观] 综合分析第 {start_chap+1}-{end_chap} 章...'
                
                try:
                    # 使用 Layer 1 的摘要进行宏观分析，并传入未解决伏笔
                    macro_summaries = chapter_summaries[start_chap:end_chap]
                    macro_result = hybrid_analyzer.ai_analyzer.analyze_macro_window(
                        macro_summaries, 
                        start_chap + 1, 
                        end_chap,
                        unresolved_mysteries=unresolved_mysteries
                    )
                    
                    # === 伏笔追踪：处理回收 ===
                    resolved_list = macro_result.get('resolved_mysteries', [])
                    for resolved in resolved_list:
                        # 这是一个简化的匹配逻辑，实际可能需要 AI 来判断哪个 mystery 被解决了
                        # 这里我们假设 AI 返回的是文本描述，我们在 registry 里标记
                        # (在真实场景中，应该让 AI 返回 mystery ID，但这太复杂了)
                        macro_structure.append({
                            "id": f"macro_{j}",
                            "range": f"{start_chap+1}-{end_chap}",
                            "plot_arc": macro_result.get('plot_arc', '无'),
                            "key_conflicts": macro_result.get('key_conflicts', []),
                            "summary": f"第 {start_chap+1}-{end_chap} 章宏观剧情",
                            "resolved_mysteries": resolved_list # 记录本阶段解决的伏笔
                        })
                        
                        # 更新全局 registry (简单匹配)
                        # TODO: 这里应该有更复杂的逻辑来移除 unresolved_mysteries 中的条目
                    
                except Exception as e:
                    logger.error(f"Macro window {j} failed: {e}")
                    continue
            
            # 构建最终结果
            characters_list = list(all_characters.values())
            # 简单计算重要性
            for char in characters_list:
                char['importance'] = min(char['mention_count'] / num_micro_windows, 1.0)
                char['final_importance'] = char['importance']
                char['degree_centrality'] = 0 
                
            char_analysis = {
                "characters": characters_list,
                "relations": all_relations,
                "main_characters": sorted(characters_list, key=lambda x: x['importance'], reverse=True)[:10],
                "supporting_characters": []
            }
            
            # 构造时间线 (包含微观和宏观结构)
            timeline_analysis = {
                'events': [], 
                'timeline': [], 
                'main_plot_events': [],
                'structure_graph': plot_structure, # 微观（章级）
                'macro_structure': macro_structure, # 宏观（25章级）
                'global_archives': global_archives # 新增：全局档案库
            }
            
            emotion_analysis = {'chapter_emotions': [], 'emotion_curve': [], 'statistics': {}}
            location_analysis = {'locations': []}
            state_analysis = {'character_states': {}}
            entities = {"characters": characters_list, "locations": []}
            
            tasks[task_id]['progress'] = 98
            tasks[task_id]['message'] = '正在生成最终报告...'
            
        else:
            # === 传统/混合 模式 ===
            # 2. 提取实体 (20%)
            tasks[task_id]['message'] = '正在提取实体...'
            extractor = EntityExtractor(min_mentions=2)
            entities = extractor.extract_entities_from_novel(novel_data)
            tasks[task_id]['progress'] = 20
    
            # 3. 分析人物关系 (40%)
            tasks[task_id]['message'] = '正在分析人物关系...'
            char_analyzer = CharacterAnalyzer()
            char_analysis = char_analyzer.analyze(
                novel_data['chapters'],
                entities['characters']
            )
            tasks[task_id]['progress'] = 40
    
            # 4. 分析时间线 (60%)
            tasks[task_id]['message'] = '正在分析时间线...'
            timeline_analyzer = TimelineAnalyzer()
            timeline_analysis = timeline_analyzer.analyze(
                novel_data['chapters'],
                char_analysis['characters'],
                char_analysis['relations']
            )
            tasks[task_id]['progress'] = 60
    
            # 5. 分析地点 (75%)
            tasks[task_id]['message'] = '正在分析地点...'
            location_analyzer = LocationAnalyzer()
            location_analysis = location_analyzer.analyze(
                novel_data['chapters'],
                entities['locations'],
                char_analysis['characters'],
                timeline_analysis['events']
            )
            tasks[task_id]['progress'] = 75
    
            # 6. 分析情感 (90%)
            tasks[task_id]['message'] = '正在分析情感...'
            emotion_analyzer = EmotionAnalyzer()
            emotion_analysis = emotion_analyzer.analyze(
                novel_data['chapters'],
                char_analysis['characters'],
                timeline_analysis['events']
            )
            tasks[task_id]['progress'] = 90
    
            # 7. 追踪状态 (100%)
            tasks[task_id]['message'] = '正在追踪状态...'
            state_tracker = StateTracker()
            state_analysis = state_tracker.analyze(
                novel_data['chapters'],
                char_analysis['characters'],
                timeline_analysis['events']
            )
            
            # 8. AI 增强分析 (可选 - 仅在 hybrid 模式下)
            if analysis_mode == 'hybrid':
                hybrid_analyzer = HybridAnalyzer()
                if hybrid_analyzer.ai_enabled:
                    tasks[task_id]['message'] = '正在进行AI增强分析...'
                    
                    # 增强人物分析
                    char_analysis = hybrid_analyzer.enhance_character_analysis(
                        char_analysis, 
                        novel_data['chapters']
                    )
                    tasks[task_id]['progress'] = 92
                    
                    # 增强时间线
                    timeline_analysis = hybrid_analyzer.enhance_timeline_analysis(
                        timeline_analysis, 
                        novel_data['chapters']
                    )
                    tasks[task_id]['progress'] = 95
                    
                    # 增强情感分析
                    emotion_analysis = hybrid_analyzer.enhance_emotion_analysis(
                        emotion_analysis, 
                        novel_data['chapters']
                    )
                    tasks[task_id]['progress'] = 98
        
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

        # 创建名称到ID的映射
        name_to_id = {char["name"]: char["id"] for char in char_analysis['characters']}

        # 构建节点
        nodes = [{
            "id": char["name"],  # 使用名称作为ID，保持一致性
            "label": char["name"],
            "importance": char.get("final_importance", 0),
            "type": "main" if char in char_analysis['main_characters'] else "supporting"
        } for char in char_analysis['characters']]

        # 构建边 - 只包含节点存在的边
        edges = []
        for i, rel in enumerate(char_analysis['relations']):
            # 确保源和目标节点都存在
            if rel["from"] in name_to_id and rel["to"] in name_to_id:
                edges.append({
                    "id": f"edge_{i}",
                    "source": rel["from"],
                    "target": rel["to"],
                    "label": rel["relationship_type"],
                    "strength": rel["strength"]
                })

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
