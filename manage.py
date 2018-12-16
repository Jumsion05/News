from flask_migrate import Migrate,MigrateCommand
from flask_script import Manager
from info import create_app,db
from info import models

app = create_app("development")

manager = Manager(app)

# 数据库迁移
Migrate(app, db)
manager.add_command("db",MigrateCommand)

if __name__ == '__main__':
    manager.run()