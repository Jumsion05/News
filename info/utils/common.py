import functools

import qiniu
from flask import current_app
from flask import g
from flask import session


def do_index_class(index):
    """自定义过滤器,过滤点击排序html的class"""
    if index == 1:
        return "first"
    elif index == 2:
        return "second"
    elif index == 3:
        return "third"
    else:
        return ""

#  装饰器查询登录用户的信息

def user_login_data(u):
    #  使用装饰器装饰视图函数时，会出现试视图函数绑定bug，
    #  视图路由会调用装饰器的name属性，当前name指的是wrapper
    #　所以使用 functools进行还原为ｕ
    @functools.wraps(u)
    def wrapper(*args,**kwargs):
        #  获取用户的id
        user_id = session.get("user_id")
        user = None
        if user_id:
            try:
                from info.models import User
                #  根据用户的id从数据库中查询用户的信息
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)

        #  g变量是用来临时存储用户信息，可以在其他函数调用
        g.user = user

        return u(*args,**kwargs)


    return wrapper


def file_storage(data):
    """上传文件到七牛云"""
    # data 上传文件的内容[ 经过read()读取出来的文件内容 ]
    # 应用ID
    access_key = "UhYWJIgbXnIzPHiZdVCenSnWVksXLlOY4WBAYc91"
    secret_key = "kVIfTnGjvMU6U9f7l5n_0cTzG4rlGh_v-MXdcKlf"
    # 存储空间名【一个项目使用一个空间】
    bucket_name = "gz-python6"
    # 实例化七牛云操作对象
    q = qiniu.Auth(access_key, secret_key)
    # key 保存到七牛云以后的文件名，一般不设置，如果不设置，则七牛云会自动帮我们生成随机的唯一的文件名
    key = None
    # upload_token 上传文件的方法
    token = q.upload_token(bucket_name)
    ret, info = qiniu.put_data(token, key, data)
    return ret["key"]  # 上传文件的相关信息