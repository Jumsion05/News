import random
import re
from datetime import datetime

from flask import current_app, jsonify
from flask import make_response
from flask import request
from flask import session

from info import constants, db
from info import redis_store
from info.models import User
from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET
from info.utils.yuntongxun.sms import CCP
from . import passport_blue

@passport_blue.route("/image_code")
def image_code():
    """图片验证码"""

    #  接收uuid
    code_id = request.args.get("code_id")

    #  生成图片验证
    name, text, image = captcha.generate_captcha()
    print(text)

    #  把图片验证码的文本内容和uuid组合保存到redis中
    try:
        # setex设置一个具有指定有效期的数据
        redis_store.setex("image_code_%s" % code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
    except Exception as e:
        #  记录日志
        current_app.logger.error(e)
        #  返回错误信息给客户端
        return make_response(jsonify(error=RET.DATAERR, errmsg="保存图片验证码失败"))

    response = make_response(image)
    #  图片必须设置相应的数据类型，否则默认是text/html
    response.headers["Content-Type"] = "image/jpeg"
    return response


@passport_blue.route("/sms_code",methods=["POST","GET"])
def send_sms():
    """
    1. 接收参数并判断是否有值
    2. 校验手机号是正确
    3. 通过传入的图片编码去redis中查询真实的图片验证码内容
    4. 进行验证码内容的比对
    5. 生成发送短信的内容并发送短信
    6. redis中保存短信验证码内容
    7. 返回发送成功的响应
    :return:
    """
    # 1. 接收参数并判断是否有值
    param_dict = request.json
    # print(param_dict)
    mobile = param_dict.get("mobile")
    image_code = param_dict.get("image_code")
    image_code_id = param_dict.get("image_code_id")

    if not all([mobile,image_code,image_code_id]):
        return jsonify(errno=RET.DATAERR,errmsg="参数不全")

    # 校验手机号是否正确　
    if not re.match("^1[3578][0-9]{9}$",mobile):
        # 提示手机号不正确
        return jsonify(errno=RET.DATAERR,errmsg="手机号不正确")

    # 通过传入的图片编码去ｒｅｄｉｓ中查询真实的图片验证码内容
    try:
        real_image_code = redis_store.get("image_code_"+image_code_id)
        # 如果能够取出值，删除redis中缓存的内容
        if real_image_code:
            real_image_code = real_image_code.decode()
            redis_store.delete("image_code_"+image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取图片验证码失败")

    # 判断验证码是否存在或者已过期
    if not real_image_code:
        # 验证码已过期
        return jsonify(errno=RET.NODATA,errmsg="验证码已过期")

    # 进行验证码内容的对比
    if image_code.lower() != real_image_code.lower():
        # 验证码输入错误
        return jsonify(errno=RET.DATAERR,errmsg="验证码输入错误")

    # 验证该手机号是否已经注册
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="该手机已经注册")

    # 生成发送短信的内容并发送短信
    result = random.randint(0,999999)
    sms_code = "%06d" %result
    current_app.logger.debug("短信验证码的内容:%s" %sms_code)
    # result = CCP().send_template_sms(mobile,[sms_code, constants.SMS_CODE_REDIS_EXPIRES/60],constants.SMS_TEMPLATE_ID)
    # print(result)
    # if result != 0:
    #     # 发送短信失败
    #     return jsonify(errno=RET.THIRDERR,errmsg="发送短信失败")

    # redis中保存短信验证码内容
    try:
        redis_store.setex("SMS_"+ mobile,constants.SMS_CODE_REDIS_EXPIRES,sms_code)
    except Exception as e:
        current_app.logger.error(e)
        # 保存短信验证码失败
        return jsonify(errno=RET.DBERR,errmsg="保存短信验证码失败")

    # 返回发送成功的响应数据
    return jsonify(errno=RET.OK,errmsg="发送成功")

@passport_blue.route("/register",methods=["POST"])
def register():
    """
    1. 获取参数和判断是否有值
    2. 从redis中获取指定号码对应的短信验证码
    3. 校验验证码
    4. 初始化user模型,并设置数据添加到数据库中
    5. 保存当前用户的状态
    6. 返回响应数据
    :return:
    """
    #1. 获取参数和判断是否有值
    param_dict = request.json
    mobile = param_dict.get("mobile")
    sms_code = param_dict.get("sms_code")
    password = param_dict.get("password")
    print('sms_code验证码:',sms_code)

    if not all([mobile,sms_code,password]):
        # 参数不全
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 从redis中获取指定号码对应的短信验证码
    try:
        real_sms_code = redis_store.get("SMS_%s"%mobile).decode()
        print('real_sms_code验证码:',real_sms_code)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取验证码失败")

    if not real_sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码过期")

    # 校验验证码
    if sms_code != real_sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码错误")

    # 删除短信验证码
    try:
        redis_store.delete("SMS_%s"%mobile)
    except Exception as e:
        current_app.logger.error(e)

    # 初始化user模型, 并设置数据添加到数据库中
    user = User()
    user.nick_name = mobile
    user.mobile = mobile
    user.password = password

    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="数据保存失败")


    # 保存用户登录状态
    session["user_id"] = user.id
    session["nick_name"] = user.nick_name
    session["mobile"] = user.mobile

    # 返回响应数据
    return jsonify(errno=RET.OK, errmsg="OK")

@passport_blue.route("/login",methods=["POST"])
def login():
    """
    1. 获取参数和判断是否有值
    2. 从数据库中查询出指定的用户
    3. 校验密码
    4. 保存用户登录状态
    5. 返回响应数据
    :return:
    """
    # 1. 获取参数和判断是否有值
    param_dict = request.json
    mobile = param_dict.get("mobile")
    password = param_dict.get("password")

    if not all([mobile,password]):
        return jsonify(errno=RET.DBERR, errmsg="参数不全")

    # 从数据库中查询出指定的用户
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据错误")

    if not user:
        return jsonify(errno=RET.USERERR, errmsg="用户不存在")

    # 校验密码
    if not user.check_passowrd(password):
        return jsonify(errno=RET.PWDERR, errmsg="密码错误")

    # 保存用户状态
    session["user_id"] = user.id
    session["nick_name"] = user.mobile
    session["mobile"] = user.mobile
    # 记录用户最后一次登录的时间
    user.last_login = datetime.now()
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)

    # 登录成功
    return jsonify(errno=RET.OK, errmsg="OK")

@passport_blue.route("/logout",methods=["POST"])
def logout():
    """
    清楚session中的对应登录之后保存的信息
    :return:
    """
    session.pop("user_id",None)
    session.pop("nick_name",None)
    session.pop("mobile",None)

    # 返回响应数据
    return jsonify(errno=RET.OK, errmsg="OK")
