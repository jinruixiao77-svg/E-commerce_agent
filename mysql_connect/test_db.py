from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
from mysql_db import db  # 导入我们的数据库工具

# 1. 定义 LangGraph 状态（基础消息状态）
class AgentState(MessagesState):
    pass

# 2. 定义节点：从 MySQL 查询数据
def query_mysql_node(state: AgentState):
    """LangGraph 节点：查询数据库"""
    # 示例：查询用户表（替换成你的表和 SQL）
    sql = "SELECT * FROM sales LIMIT 5;"
    result = db.query(sql)
    
    # 打印结果
    print("\n📊 数据库查询结果：")
    for row in result:
        print(row)
    
    # 返回状态
    return {"messages": [f"查询到 {len(result)} 条用户数据"]}

# 3. 定义节点：写入数据到 MySQL
def insert_mysql_node(state: AgentState):
    """LangGraph 节点：插入数据"""
    sql = "INSERT INTO users (username, password) VALUES (%s, %s);"
    rows = db.execute(sql, ("wangwu", "123456"))
    return {"messages": [f"成功插入 {rows} 条数据"]}

# 4. 构建 LangGraph 工作流
workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("query_db", query_mysql_node)
workflow.add_node("insert_db", insert_mysql_node)

# 设置入口
workflow.set_entry_point("query_db")

# 构建流程
workflow.add_edge("query_db", "insert_db")

# 编译图
app = workflow.compile()

# 5. 运行 LangGraph
if __name__ == "__main__":
    try:
        # 执行工作流
        final_state = app.invoke({"messages": []})
        print("\n✅ 流程执行完成：", final_state["messages"][-1])
    finally:
        # 程序结束关闭数据库连接
        db.close()