"""
小说脉络分析系统 - 配置文件
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """应用配置类"""

    # Neo4j配置
    NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'password')

    # Flask配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    # 文件上传配置
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'data/novels')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 104857600))  # 100MB
    ALLOWED_EXTENSIONS = {'txt', 'epub', 'pdf'}

    # 分析参数
    MIN_CHARACTER_MENTIONS = int(os.getenv('MIN_CHARACTER_MENTIONS', 3))
    MIN_RELATION_STRENGTH = float(os.getenv('MIN_RELATION_STRENGTH', 0.3))

    # AI 大模型配置
    AI_PROVIDER = os.getenv('AI_PROVIDER', 'openai')  # openai 或 anthropic
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    ENABLE_AI_ANALYSIS = os.getenv('ENABLE_AI_ANALYSIS', 'false').lower() == 'true'

    # 数据目录
    DATA_DIR = 'data'
    DICTIONARIES_DIR = os.path.join(DATA_DIR, 'dictionaries')
    SAMPLE_NOVELS_DIR = os.path.join(DATA_DIR, 'sample_novels')

    @staticmethod
    def init_app(app):
        """初始化应用配置"""
        # 确保必要的目录存在
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.DICTIONARIES_DIR, exist_ok=True)
        os.makedirs(Config.SAMPLE_NOVELS_DIR, exist_ok=True)
