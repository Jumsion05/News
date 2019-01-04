from flask import current_app, jsonify
from flask import g
from flask import request
from flask import session

from info import constants
from info.models import User, News, Category
from info.utils.common import user_login_data
from info.utils.response_code import RET
from . import index_blu
from flask import render_template

# 使用蓝图对象注册路由
@index_blu.route("/")
@user_login_data
def index():
    # # 获取当前登录用户的id
    # user_id = session.get("user_id")
    # # 通过id获取用户信息
    # user = None
    # if user_id:
    #     try:
    #         user = User.query.get(user_id)
    #     except Exception as e:
    #         current_app.logger.error(e)

    # 获取当前登录的信息
    user = g.user

    # 获取点击排行榜数据
    news_list = None
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    # 获取新闻分类数据
    categories = Category.query.all()
    # print(categories)

    data = {
        "user_info": user.to_dict() if user else None,
        "news_list": news_list,
        "categoires": categories,
    }

    return render_template("news/index.html", data=data)

# 自定视图函数,访问网站图标
@index_blu.route("/favcion.ico")
def favicon():
    return current_app.send_static_file("news/favicon.ico")


@index_blu.route("/news_list")
def news_list():
    """根据新闻分类id获取新闻咨询列表"""
    # 获取参数
    cid = request.args.get("cid")
    page = request.args.get("page",1) # 页码数
    per_page = request.args.get("per_page", constants.HOME_PAGE_MAX_NEWS) # 页码内容数量

    # 校验参数
    if not cid:
        return jsonify(errno=RET.DATAERR, errmsg="缺少参数")

    # 根据cid获取参数
    try:
        # 如果查询的是"最新"的新闻咨询,则获取的必须是所有分类下数据
        filters = []
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)
        if cid != 1:
            filters.append(News.category_id==cid)
        pagination = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page,per_page,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="无效参数")

    page = pagination.page # 页码数
    # 获取当前页面中所有的数据是一个list数据,成员是news模型对象
    news_list = pagination.items
    pages = pagination.pages

    # 数据重构
    news_li = []
    for news in news_list:
        news_li.append(news.to_basic_dict()) # 把对象转换成字典格式

    # 返回数据结果
    return jsonify(
        errno=RET.OK,
        errmsg="OK",
        current_app=page,
        pages=pages,
        news_list=news_li
    )