import mysql.connector
from mysql.connector import Error

class MySQLDatabase:
    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        """创建数据库连接"""
        if self.connection is None or not self.connection.is_connected():
            try:
                self.connection = mysql.connector.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    charset="utf8mb4"
                )
                if self.connection.is_connected():
                    print("✅ MySQL 连接成功")
            except Error as e:
                print(f"❌ MySQL 连接失败：{e}")
                raise e
        return self.connection

    def close(self):
        """关闭连接"""
        if self.connection is not None and self.connection.is_connected():
            self.connection.close()
            print("✅ MySQL 连接已关闭")

    def query(self, sql, params=None):
        """执行查询语句（SELECT）"""
        conn = self.connect()
        cursor = conn.cursor(dictionary=True)  # 返回字典格式数据
        try:
            cursor.execute(sql, params)
            return cursor.fetchall()  # 返回所有结果
        finally:
            cursor.close()

    def execute(self, sql, params=None):
        """执行增删改（INSERT/UPDATE/DELETE）"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            conn.commit()
            return cursor.rowcount  # 受影响行数
        finally:
            cursor.close()

# ============== 初始化全局数据库实例 ==============
# 替换成你的 MySQL 信息
db = MySQLDatabase(
    host="localhost",    # 你的数据库地址
    port=3306,           # 端口默认 3306
    user="root",         # 用户名
    password="root",  # 密码
    database="my_resume_db"   # 数据库名
)