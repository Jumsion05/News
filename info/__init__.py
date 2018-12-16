from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from flask_session import Session
from config import config
import logging

# 创建数据库db对象
db = SQLAlchemy()
# 连接redis数据库
strict_redis = None

def create_app(config_name):
    """通过传入不同的配置名称,初始化配置的应用"""
    setup_log(config_name)
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    # 配置数据库
    db.init_app(app)
    # 配置redis
    global strict_redis
    strict_redis = StrictRedis(host=config[config_name].REDIS_PORT,port=config[config_name].REDIS_PORT)
    # 开启csrf保护
    CSRFProtect(app)
    # session配置
    Session(app)

    # 注册蓝图
    from info.modules.index import index_blu
    app.register_blueprint(index_blu)

    return app


def setup_log(config_name):
    """配置日志"""

    # 设置日志的记录等级
    logging.basicConfig(level=config[config_name].LOG_LEVEL)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)