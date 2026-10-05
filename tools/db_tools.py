from langchain.tools import tool
from mysql_connect.mysql_db import db

@tool
def query_users(sql: str):
    """当需要查询数据库信息时，调用这个函数查询条件"""
    return db.query(sql)

@tool
def insert_users(username: str, password: str):
    """插入用户表数据，username：用户名，password：密码"""
    sql = f"INSERT INTO users (username, password) VALUES (%s, %s);"
    return db.execute(sql, (username, password))
