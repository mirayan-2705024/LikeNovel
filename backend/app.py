"""
Flask应用主入口
"""
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import sys
import logging

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import Config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.config.from_object(Config)

# 启用CORS
CORS(app)

# 初始化配置
Config.init_app(app)

# 注册API蓝图
from backend.api.routes import api_bp
app.register_blueprint(api_bp, url_prefix='/api')


@app.route('/')
def index():
    """主页"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/health')
def health():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "version": "0.4.0",
        "service": "LikeNovel Analysis System"
    })


@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        "error": "Not Found",
        "message": "The requested resource was not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    logger.error(f"Internal error: {error}")
    return jsonify({
        "error": "Internal Server Error",
        "message": "An internal error occurred"
    }), 500


if __name__ == '__main__':
    logger.info("Starting LikeNovel Analysis System...")
    logger.info(f"Neo4j URI: {Config.NEO4J_URI}")
    logger.info(f"Upload folder: {Config.UPLOAD_FOLDER}")

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=Config.FLASK_DEBUG
    )
