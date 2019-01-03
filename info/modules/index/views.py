from flask import current_app
from flask import session

from info.models import User
from . import index_blu
from flask import render_template

# 使用蓝图对象注册路由
@index_blu.route("/")
def index():
    # 获取当前登录用户的id
    user_id = session.get("user_id")
    # 通过id获取用户信息
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    return render_template("news/index.html", data={"user_info": user.to_dict() if user else None})

# 自定视图函数,访问网站图标
@index_blu.route("/favcion.ico")
def favicon():
    return current_app.send_static_file("news/favicon.ico")