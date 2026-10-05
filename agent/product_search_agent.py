
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, MessagesState, StateGraph,END
import os

from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv
load_dotenv()
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"] = "product_search_agent"

from agent.db_agent import response_model
from tools.db_tools import query_users,insert_users

from agent.db_agent import graph, respond_user, workflow

STATISTIC_PROMPT = """
你是订单数据统计智能体。
用户的问题{question}需要查询MySQL数据库，请你**调用工具 query_users(sql)** 来获取数据。

数据库表结构：
1. product 商品表：product_id, product_name, price,category

规则：
1. 必须通过调用工具 query_users(sql) 查询数据，不要直接回答
2. 生成正确可执行的SQL作为参数传入工具
"""

def generate_search_mysql(state: MessagesState):
    llm_with_tools = response_model.bind_tools([query_users, insert_users])
    question = state["messages"][0].content
    prompt = STATISTIC_PROMPT.format(question=question)
    messages = [{"role": "system", "content": prompt}, *state["messages"]]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


workflow=StateGraph(MessagesState)
workflow.add_node("respond_user",respond_user)
workflow.add_node("generate_search_mysql",generate_search_mysql)
workflow.add_node("tool_node",ToolNode([query_users,insert_users]))

workflow.add_edge(START,"generate_search_mysql")
workflow.add_edge("generate_search_mysql","tool_node")
workflow.add_edge("tool_node","respond_user")
workflow.add_edge("respond_user",END)

memory=InMemorySaver()
graph_search=workflow.compile(checkpointer=memory,interrupt_after=[],)