from flask import abort, jsonify
from flask import current_app
from flask import g
from flask import render_template
from flask import request
from flask import session

from info import constants
from info import db
from info.models import News, User, Comment, CommentLike
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

    # 获取评论信息
    comments = []
    try:
        comments = Comment.query.filter(Comment.news_id==news.id).order_by(Comment.create_time.desc())
    except Exception as e:
        current_app.logger.error(e)

    # 直接获取的评论信息是一个列表,成员是一个评论对象
    comment_list = []
    for comment in comments:
        comment_list.append(comment.to_dict())

    # 获取当前用户点赞过的评论信息
    like_list = user.like_comments.all()
    comment_like_list = []
    for comment in like_list:
        comment_like_list.append(comment.to_dict())

    # 当前新闻作者
    author = news.user
    print("author:",author)

    # 获取当前作者发布的总篇数
    news_list_count = author.news_list.count()

    # 查询当前作者粉丝数量
    fans_count = author.followers.count()

    # 显示当前登录用户对作者的关注状态
    is_follow = False
    if author in user.followed:
        is_follow = True

    return render_template("news/detail.html",
                           news=news,
                           news_list=news_list,
                           user=user,
                           is_collection=is_collection,
                           comment_list=comment_list,
                           comment_like_list=comment_like_list,
                           # 获取当前新闻作者的信息
                           author=author,
                           # 获取当前新闻作者发布的篇数
                           news_list_count=news_list_count,
                           # 作者粉丝的数量
                           fans_count=fans_count,
                           # 当前登录用户对作者的关注状态
                           is_follow=is_follow
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


@news_blu.route("/news_comment", methods=["POST"])
@user_login_data
def news_comment():
    """用户评论新闻或者用户回复评论"""
    # 接收数据[news_id,评论内容,parent_id]
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    data_dict = request.json
    news_id = data_dict.get("news_id")
    comment_str = data_dict.get("content")
    parent_id = data_dict.get("parent_id")
    print(news_id)
    print(comment_str)
    print(parent_id)

    # 校验数据
    if not all([news_id,comment_str]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")

    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据错误")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="该新闻不存在")

    # 操作数据库
    comment = Comment()
    comment.user_id = user.id
    comment.news_id = news.id
    comment.content = comment_str

    if parent_id:
        comment.parent_id = parent_id

    # 保存数据库
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存评论数据失败")

    # 响应数据
    return jsonify(errno=RET.OK, errmsg="OK", comment=comment.to_dict())

@news_blu.route("/comment_like", methods=["POST"])
@user_login_data
def comment_like():
    """用户对评论进行点赞或者取消点赞"""
    # 接收参数（comment_id,action）
    # action值可以是add或者remove
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    data_dict = request.json
    comment_id = data_dict.get("comment_id")
    action = data_dict.get("action")
    print(comment_id)
    print(action)

    # 根据comment_id去查询评论的信息(如果查不到,说明评论信息不存在)
    if not all([comment_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")

    if action not in ("add", "remove"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询失败")

    # 判断comment是否存在
    if not comment:
        return jsonify(errno=RET.NODATA, errmsg="评论数据不存在")

    # 新建模型对象
    commentLike = CommentLike()
    commentLike.comment_id = comment.id
    commentLike.user_id = user.id

    # 根据action执行对应的操作
    if action == "add":
        # 点赞
        db.session.add(commentLike)
        # 增加当前评论的点赞数量
        comment.like_count += 1
    else:
        # 取消点赞
        commentLike = CommentLike.query.filter_by(comment_id=comment_id, user_id=user.id).first()
        db.session.delete(commentLike)
        # 减去当前评论的点赞数量
        comment.like_count -= 1

    # 保存数据库操作
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")

    # 返回响应结果, 评论点赞或者取消点赞成功
    return jsonify(errno=RET.OK, errmsg="操作成功", like_count=comment.like_count)

@news_blu.route("/author_fans",methods=["POST"])
@user_login_data
def author_fans():
    """登录用户关注或者取消关注新闻作者"""
    # 接收参数[author_id, action]并进行校验
    # action的值可以是follow关注和is_followed取消关注
    user = g.user
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    data_dict = request.json
    author_id = data_dict.get("author_id")
    action = data_dict.get("action")

    # 根据author_id查询作者的信息(如果查询不到,说明作者不存在)
    if not all([author_id,action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")

    if action not in ("follow","is_followed"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不足")

    # 判断新闻作者是否存在
    try:
        author = User.query.get(author_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")

    if not author:
        return jsonify(errno=RET.NODATA, errmsg="新闻作者不存在")

    # 根据action执行对象的操作
    if action == "follow":
        # 关注
        # author.followers 新闻作者的所有粉丝,返回是一个列表
        author.followers.append(user)
        print(author.followers.count())
    else:
        #　取消关注
        author.followers.remove(user)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")

    # 返回数据结果,返回粉丝数量
    followers_count = author.followers.count()
    return jsonify(errno=RET.OK, errmsg="OK", followers_count=followers_count)