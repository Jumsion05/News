from . import index_blu

# 使用蓝图对象注册路由
@index_blu.route("/index")
def index():
    return "index页面"