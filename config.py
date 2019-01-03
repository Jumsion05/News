# import logging
# from redis import StrictRedis
#
# class Config(object):
#     """工程配置信息"""
#     DEBUG = True
#     # 加密的秘钥
#     SECRET_KEY = "EjpNVSNQTyGi1VvWECj9TvC/+kq3oujee2kTfQUs8yCM6xX9Yjq52v54g+HVoknA"
#
#     # 数据库的配置信息
#     SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/news"
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
#
#     # redis配置
#     REDIS_HOST = "127.0.0.1"
#     REDIS_PORT = 6379
#
#     # flask_session的配置信息
#     SESSION_TYPE = "redis"  # 指定 session 保存到 redis 中
#     SESSION_USE_SIGNER = True  # 让 cookie 中的 session_id 被加密签名处理
#     SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)  # 使用 redis 的实例
#     PERMANENT_SESSION_LIFETIME = 86400  # session 的有效期，单位是秒
#
#     # 默认日志的等级
#     LOG_LEVEL = logging.DEBUG
#
#
#
# class DevelopementConfig(Config):
#     """开发模式下的配置"""
#     DEBUG = True
#
# class ProductionConfig(Config):
#     """生产模式下的配置"""
#     LOG_LEVEL = logging.ERROR
#
# config = {
#     "development": DevelopementConfig,
#     "production": ProductionConfig
# }

import logging
from redis import StrictRedis


class Config(object):
    """工程配置信息"""
    DEBUG = True

    #  配置数据库信息
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/news"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #  配置redis
    REDIS_HOST = "127.0.0.1"  # 项目上线后，这个地址会被替换掉的，mysql也是
    REDIS_PORT = 6379

    # 设置秘钥
    SECRET_KEY = "DKPzIHktokSzF+inBfpdcQHNyXaB0OxuLWq8BWs+e4rPEIxMinbGw5SbwWNV1VYG"

    #  flask_session配置信息
    SESSION_TYPE = "redis"  # 指定session保存到redis中
    SESSION_USE_SIGNER = True  # 让cookie中的session_id被加密签名处理
    SESSION_REDIS = StrictRedis(host=REDIS_HOST,port=REDIS_PORT,db=1) # 使用redis的实例
    PERMANENT_SESSION_LIFETIME = 24 * 60 * 60  #  session的有效期，单位为秒



class DevelopmentConfig(Config):
    """开发模式下的配置"""
    LOG_LEVEL = logging.DEBUG

class ProductionConfig(Config):
    """生产模式下的配置"""
    DEBUG = False
    LOG_LEVEL = logging.WARNING