from flask import abort, jsonify
from flask import current_app
from flask import g
from flask import render_template
from flask import request
from flask import session

from info import constants
from info import db
from info.models import News, User
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import news_blu


@news_blu.route("/<int:news_id>")
@user_login_data
def detail(news_id):
    """
    新闻咨询详情页
    :param news_id:
    :return:
    """
    # 根据id获取新闻咨询数据
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        abort(404)

    if not news:
        abort(404)

    # 每次用户访问新闻，都是新增新闻的点击率
    news.clicks += 1
    try:
        db.session.commit()
    except Exception as e:
        # 即便无法更新点击率[浏览量]，但是并不影响项目的正常运转
        current_app.logger.error(e)

    # 查询点击排行的咨询列表
    news_list = None

    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    # 获取当前已经登陆的用户信息
    user = g.user


    # 判断该新闻是否被收藏,
    is_collection = False
    if user:
        if news in user.collection_news:
            is_collection = True


    return render_template("news/detail.html",
                           news=news,
                           news_list=news_list,
                           user=user,
                           is_collection=is_collection
                           )

@news_blu.route("/news_collect", methods=["POST"])
@user_login_data
def news_collect():
    """用户收藏/取消收藏新闻"""
    # 接收数据[news_id, action]
    # action的值只能是collect或者cancel_collect

    user = g.user
    json_data = request.json
    news_id = json_data.get("news_id")
    action = json_data.get("action")
    # print(action)
    # print(news_id)

    # 校验数据
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    if not news_id:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if action not in ("collect","cancel_collect"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 检验news_id是否正确
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="新闻数据不存在")

    # 操作数据
    if action == "collect":
        # 要收藏当前新闻
        user.collection_news.append(news)
    else:
        # 要取消收藏当前新闻
        user.collection_news.remove(news)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")

    # 返回结果
    return jsonify(errno=RET.OK, errmsg="OK")
