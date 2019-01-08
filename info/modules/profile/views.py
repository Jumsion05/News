from flask import current_app
from flask import g, jsonify
from flask import render_template
from flask import request
from flask import session

from info import user_login_data, db
from info.utils.response_code import RET
from . import profile_blu

@profile_blu.route("")
@user_login_data
def user_index():
    """个人中心的首页[主框架页面]"""
    user = g.user
    return render_template("news/user.html", user=user)

@profile_blu.route("/user_base_info", methods=["GET", "POST"])
@user_login_data
def user_base_info():
    """用户的个人基本信息表单界面"""
    user = g.user
    if request.method == "GET":
        return render_template("news/user_base_info.html", user=user)

    # 如果不是get方式,则保存数据
    # 接收的参数有[签名, 昵称, 性别]
    data_dict = request.json
    nick_name = data_dict.get("nick_name")
    gender = data_dict.get("gender")
    signature = data_dict.get("signature")

    # 校验参数
    if not all([nick_name, gender, signature]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")

    if gender not in ("WOMAN", "MAN"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")

    # 保存更新数据
    user.nick_name = nick_name
    user.gender = gender
    user.signature = signature

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")

    # 将session保存的数据进行实时更新
    session["nick_name"] = nick_name

    # 返回结果
    return jsonify(errno=RET.OK, errmsg="操作成功")