# [安装PostgreSQL](https://www.postgresql.org/download/)

# 启动关闭数据库
[https://tableplus.io/blog/2018/10/how-to-start-stop-restart-postgresql-server.html](https://tableplus.io/blog/2018/10/how-to-start-stop-restart-postgresql-server.html)

* 启动
```
pg_ctl -D "C:\Program Files\PostgreSQL\12\data" start
```

* 停止
```
pg_ctl -D "C:\Program Files\PostgreSQL\12\data" stop
```

* 重启
```
pg_ctl -D "C:\Program Files\PostgreSQL\12\data" restart
```

# 连接管理数据库
* Postgres CLI tools
```
用户登录：sudo -u <username> -i
创建数据库：createdb <database_name>
例如以postgres默认用户创建fyyur数据库：createdb -h localhost -p 5432 -U postgres fyyur
删除数据库：dropdb <database_name>
重置数据库：dropdb <database_name> && createdb <database_name>
```
* psql 
```
psql <dbname> [<username>]
列出所有数据库： \l
连接数据库：\c <dbname>
列出数据库表：\dt
展示具体表结构：\d <tablename>
```

# python适用的Postgres连接库DBAPI：pyscopg2

# 安装flask_sqlalchemy
* pip3 install flask_sqlalchemy
* 配置数据库连接 config.py
```
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:todo@localhost:5432/fyyur'
```

# 安装项目包依赖
* 初始项目环境
```
  $ pip3 install Flask
  $ pip3 install virtualenv
  $ cd YOUR_PROJECT_DIRECTORY_PATH/
  $ virtualenv --no-site-packages env
  $ 开启虚拟环境：source env/bin/activate (window:.\env\Scripts\activate.bat)
  $ 退出虚拟环境： .\env\Scripts\deactivate.bat
```

* 安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple  # 国内镜像源

# 运行开发服务器
* mac
```
  $ mac: export FLASK_APP=app.py
  $ mac: export FLASK_ENV=development # enables debug mode= "development")
  $ mac:python3 app.py
```

* window
```
  $ window Command Prompt: SET FLASK_APP=app.py / window PowerShell: $env:FLASK_APP = "app.py"
  $ window Command Prompt: SET FLASK_ENV=development / window PowerShell: $env:FLASK_ENV = "development"
  $ python -m flask run FLASK_DEBUG=true
``


# flask_migrate 升级数据库模型
* 首次初始化 ```flask db init```
* 建立迁移 ```flask db migrate -m 'xxxx' ```
* 运行迁移 ```flask db upgrade ```

