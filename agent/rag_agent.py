import os
from dotenv import load_dotenv
load_dotenv()
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"] = "rag_agent"

from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import InMemorySaver

from agent.db_agent import response_model
from tools.rag_tools import search_knowledge

RAG_PROMPT = """
你是电商客服，负责回答用户关于售后政策、包邮、退货、退款、发货时间等问题。
用户问题：{question}

规则：
1. 必须先调用 search_knowledge 工具检索知识库
2. 严格依据检索到的知识库内容回答，不要编造
3. 回答简洁、准确、口语化
"""

def generate_rag(state: MessagesState):
    llm_with_tools = response_model.bind_tools([search_knowledge])
    question = state["messages"][0].content
    prompt = RAG_PROMPT.format(question=question)
    messages = [{"role": "system", "content": prompt}, *state["messages"]]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def respond_user(state: MessagesState):
    question = state["messages"][0].content
    # 取工具返回的知识库内容（最后一条 tool 消息）
    context = ""
    for m in state["messages"]:
        if getattr(m, "type", "") == "tool":
            context = m.content
    prompt = f"根据用户问题{question}和知识库内容{context}，生成最终回答。"
    messages = [{"role": "system", "content": prompt}, *state["messages"]]
    response = response_model.invoke(messages)
    return {"messages": [response]}

workflow = StateGraph(MessagesState)
workflow.add_node("generate_rag", generate_rag)
workflow.add_node("tool_node", ToolNode([search_knowledge]))
workflow.add_node("respond_user", respond_user)

workflow.add_edge(START, "generate_rag")
workflow.add_edge("generate_rag", "tool_node")
workflow.add_edge("tool_node", "respond_user")
workflow.add_edge("respond_user", END)

memory = InMemorySaver()
graph_rag = workflow.compile(checkpointer=memory, interrupt_after=[])
