from langchain_core.prompts import prompt
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import MessagesState
import os
from dotenv import load_dotenv
load_dotenv()
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"] = "product_inquiry_agent"

from agent.db_agent import response_model

from tools.db_tools import query_users, insert_users

from langgraph.checkpoint.memory import InMemorySaver

Response_product_Prompt="根据问题{question}和数据{context}回答"

def respond_user(state:MessagesState):
    question=state['messages'][0].content
    context=state['messages'][1].content if len(state['messages']) > 1 else''
    prompt=Response_product_Prompt.format(question=question,context=context)
    messages=[{"role":"system","content":prompt},*state['messages']]
    response=response_model.invoke(messages)
    return {"messages":[response]}

STATISTIC_PROMPT = """
你是订单数据统计智能体。
用户的问题{question}需要查询MySQL数据库，请你**调用工具 query_users(sql)** 来获取数据。

数据库表结构：
1. orders 订单表：order_id, user_id, product_id, order_amount, order_status, pay_time, create_time
2. product 商品表：product_id, product_name, price

规则：
1. 只统计 order_status = '已完成' 的有效订单
2. 按日统计用 create_time 分组
3. 必须通过调用工具 query_users(sql) 查询数据，不要直接回答
4. 生成正确可执行的SQL作为参数传入工具
"""

def generate_product_mysql(state:MessagesState):
    llm_with_tools=response_model.bind_tools([query_users,insert_users])
    question=state["messages"][0].content
    prompt=STATISTIC_PROMPT.format(question=question)
    messages=[{"role":"system","content":prompt},*state["messages"]]
    response=llm_with_tools.invoke(messages)
    return {"messages":[response]}

from langgraph.graph import StateGraph,START,END
from langgraph.prebuilt import ToolNode

workflow=StateGraph(MessagesState)
workflow.add_node("respond_user",respond_user)
workflow.add_node("generate_product_mysql",generate_product_mysql)
workflow.add_node("tool_node",ToolNode([query_users,insert_users]))

workflow.add_edge(START,"generate_product_mysql")
workflow.add_edge("generate_product_mysql","tool_node")
workflow.add_edge("tool_node","respond_user")
workflow.add_edge("respond_user",END)

memory=InMemorySaver()
graph_product=workflow.compile(checkpointer=memory,interrupt_after=[],)





