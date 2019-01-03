# from flask_migrate import Migrate,MigrateCommand
# from flask_script import Manager
# from info import create_app,db
# from info import models
#
# app = create_app("development")
#
# manager = Manager(app)
#
# # 数据库迁移
# Migrate(app, db)
# manager.add_command("db",MigrateCommand)
#
# if __name__ == '__main__':
#     manager.run()

import logging
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from info import create_app,db
from config import DevelopmentConfig,ProductionConfig


app = create_app(DevelopmentConfig)

# 使用终端脚本工具启动和管理flask
manager = Manager(app)

#  启动数据迁移工具
Migrate(app,db)
#  添加数据迁移的命令到终端脚本工具中
manager.add_command("db",MigrateCommand)



if __name__ == '__main__':
    app.run()
    # manager.run()
