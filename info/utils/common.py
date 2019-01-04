import functools

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