# from logging.handlers import RotatingFileHandler
#
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from redis import StrictRedis
# from flask_wtf import CSRFProtect
# from flask_session import Session
# from config import config
# import logging
#
# # 创建数据库db对象
# db = SQLAlchemy()
# # 连接redis数据库
# redis_store = None
#
# def create_app(config_name):
#     """通过传入不同的配置名称,初始化配置的应用"""
#     setup_log(config_name)
#     app = Flask(__name__)
#     app.config.from_object(config[config_name])
#     # 配置数据库
#     db.init_app(app)
#     # 配置redis
#     global redis_store
#     redis_store = StrictRedis(host=config[config_name].REDIS_PORT,port=config[config_name].REDIS_PORT)
#     # 开启csrf保护
#     CSRFProtect(app)
#     # session配置
#     Session(app)
#
#     # 首页蓝图
#     from info.modules.index import index_blu
#     app.register_blueprint(index_blu)
#     # 登录注册蓝图
#     from info.modules.passport import passport_blue
#     app.register_blueprint(passport_blue)
#
#     return app
#
#
# def setup_log(config_name):
#     """配置日志"""
#
#     # 设置日志的记录等级
#     logging.basicConfig(level=config[config_name].LOG_LEVEL)  # 调试debug级
#     # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
#     file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
#     # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
#     formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
#     # 为刚创建的日志记录器设置日志记录格式
#     file_log_handler.setFormatter(formatter)
#     # 为全局的日志工具对象（flask app使用的）添加日志记录器
#     logging.getLogger().addHandler(file_log_handler)

import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask import g
from flask import render_template
from flask.ext.wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from flask_wtf.csrf import generate_csrf


db = SQLAlchemy()
redis_store = None

def get_log(level_name):
    """设置日志函数"""
    #  设置日志的记录等级
    logging.basicConfig(level=level_name)  #  调试debug等级
    #  创建日志记录器，指明日志保存的路径，每个日志文件的最大大小，保存日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log",maxBytes=1024*1024*10,backupCount=10)
    #  创建日志记录的格式，日志的等级，输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    #  为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    #  为全局的日志工具对象(flask app 使用的),添加日志记录器
    logging.getLogger().addHandler(file_log_handler)
    # print(level_name.LOG_LEVEL)


def create_app(config_name):
    """项目初始化函数"""
    app = Flask(__name__)

    #  设置配置类
    Config = config_name

    app.config.from_object(Config)

    #  配置数据库
    db.init_app(app)

    #  创建StrictRedis对象
    global redis_store
    redis_store = StrictRedis(Config.REDIS_HOST,Config.REDIS_PORT)

    #  开启CSRF防范机制
    CSRFProtect(app)

    #  解决在ajax中使用csrf防范机制的问题
    #  1.  告诉浏览器，已经生成csrf_token
    @app.after_request
    def after_request(response):
        # 生成csrf_token
        csrf_token = generate_csrf()
        #  可以通过设置cookie的方式，把csrf_token告诉浏览器
        response.set_cookie("csrf_token",csrf_token)

        return response


    #  开启session功能
    Session(app)

    #  配置项目的日志
    get_log(config_name.LOG_LEVEL)
    # print(config_name.LOG_LEVEL)

    #  使用app对象注册蓝图
    #  首页
    from info.modules.index import index_blu
    app.register_blueprint(index_blu)
    # 注册
    from info.modules.passport import passport_blue
    app.register_blueprint(passport_blue)
    # 添加自定义过滤器
    from info.utils.common import do_index_class
    app.add_template_filter(do_index_class, "index_class")


    return app




