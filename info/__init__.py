from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
from flask_session import Session
from config import config

# 创建数据库db对象
db = SQLAlchemy()
# 连接redis数据库
strict_redis = None

def create_app(config_name):
    """通过传入不同的配置名称,初始化配置的应用"""
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
    return app