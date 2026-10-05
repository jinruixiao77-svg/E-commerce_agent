import os
# --------------------- 你原来的代码（完全不变） ---------------------
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"] = "db_agent"
from dotenv import load_dotenv
load_dotenv()

from tools.db_tools import query_users, insert_users
from langgraph.graph import MessagesState
from langchain.chat_models import init_chat_model

# ===== 1. 导入记忆存储 =====
from langgraph.checkpoint.memory import InMemorySaver

response_model = init_chat_model(
    model="qwen-plus",
    model_provider="openai",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    temperature=0.5,
)

def generate_query_or_respond(state: MessagesState):
    prompt = """
    你的任务：
    1. 如果需要查询数据库 → 只回复：是
    2. 不需要查询 → 直接正常回答
    """
    messages = [{"role": "system", "content": prompt}, *state["messages"]]
    response = response_model.invoke(messages)
    return {"messages": [response]}

Response_PROMPT = "根据问题{question}和数据{context}回答"

def respond_user(state: MessagesState):
    question = state["messages"][0].content
    context = state["messages"][1].content if len(state["messages"]) > 1 else ""
    prompt = Response_PROMPT.format(question=question, context=context)
    messages = [{"role": "system", "content": prompt}, *state["messages"]]
    response = response_model.invoke(messages)
    return {"messages": [response]}

SQL_PROMPT = """
你是一个专业的订单查询智能客服，只回答订单相关问题{question}。
你可以查询的信息包括：订单号、订单状态、订单金额、商品名称、创建时间、支付时间、发货时间、用户名、手机号。

数据库表结构：
1. orders 表：order_id, user_id, product_id, order_amount, order_status, pay_time, ship_time, create_time
2. user 表：user_id, username, phone
3. product 表：product_id, product_name

订单状态：待支付、已支付、已发货、已完成、已取消

回答规则：
1. 用户必须提供【订单号】或【手机号】或【用户名】才能查询
2. 未提供关键信息时，引导用户补充
3. 回答简洁、准确、口语化
4. 不泄露数据库字段，只返回用户可理解的内容"""

def generate_mysql(state: MessagesState):
    llm_with_tools = response_model.bind_tools([query_users, insert_users])
    question = state["messages"][0].content
    prompt = SQL_PROMPT.format(question=question)
    messages = [{"role": "system", "content": prompt}, *state["messages"]]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def route_to_mysql(state: MessagesState):
    last = state["messages"][-1].content.strip()
    if last == "是":
        return "generate_mysql"
    return "respond_user"

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

workflow = StateGraph(MessagesState)
workflow.add_node("generate_query_or_respond", generate_query_or_respond)
workflow.add_node("tool_node", ToolNode([query_users, insert_users]))
workflow.add_node("respond_user", respond_user)
workflow.add_node("generate_mysql", generate_mysql)

workflow.add_edge(START, "generate_query_or_respond")
workflow.add_conditional_edges("generate_query_or_respond", route_to_mysql)
workflow.add_edge("generate_mysql", "tool_node")
workflow.add_edge("tool_node", "respond_user")
workflow.add_edge("respond_user", END)
 
# ===== 2. 编译时加入记忆（唯一关键改动） =====
memory = InMemorySaver()  # 内存记忆
graph = workflow.compile(checkpointer=memory,interrupt_after=[],)  # 打开记忆功能


