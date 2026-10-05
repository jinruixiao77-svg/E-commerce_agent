
import os
import json
from dotenv import load_dotenv
load_dotenv()
# --------------------- 你原来的代码（完全不变） ---------------------
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"] = "main_agent"

from langgraph.graph import MessagesState
from langchain.chat_models import init_chat_model
from agent.db_agent import graph
from agent.product_inquiry_agent import graph_product
from agent.db_agent import respond_user
from agent.product_search_agent import graph_search

response_model = init_chat_model(
    model="qwen-plus",
    model_provider="openai",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    temperature=0.5,
)

PROMPT="""用户问题{question}

请判断用户意图,只能从以下类型选择一个:
- 商品查询(查商品，推荐，找东西，价格，库存)
- 订单查询(查订单，物流，发货，退款)
- 客服咨询(售后，规则，包邮，退货，发货时间)
- 数据统计(销量，销售额，订单量，日报)
- 其它(闲聊，无关内容)

输出格式(严格json):
{{
    "intent":"选择其中一个",
    "confidence":0~1,
    "key_info":{{
        "商品关键词":"",
        "订单号":"",
        "用户ID":"",
        "时间范围":""
    }}
}}
"""
def respond_user_main(state:MessagesState):
    question=state["messages"][0].content
    prompt=PROMPT.format(question=question)
    messages=[{"role":"system","content":prompt},*state["messages"]]
    response=response_model.invoke(messages)

    return {"messages":[response]}


def route_intent(state: MessagesState):
    """
    核心逻辑：
    识别到【订单查询】→ 调用 graph（db_agent）
    其他 → 直接结束
    """
    try:
        # 解析AI返回的JSON
        intent_json = json.loads(state["messages"][-1].content)
        intent = intent_json["intent"]
        
        if intent == "订单查询":
            return "graph"  # 跳转到子图
        if intent == "数据统计":
            return "graph_product"
        if intent == "其它":
            return "respond_user"
        if intent == "商品查询":
            return "graph_search"
        else:
            return END  # 结束
        
    except Exception as e:
        return END



from langgraph.graph import StateGraph,START,END
from langgraph.prebuilt import ToolNode

workflow=StateGraph(MessagesState)

workflow.add_node("respond_user_main",respond_user_main)

workflow.add_node("graph",graph)
workflow.add_node("graph_product",graph_product)
workflow.add_node("respond_user",respond_user)
workflow.add_node("graph_search",graph_search)


workflow.add_edge(START,"respond_user_main")
workflow.add_conditional_edges(
    "respond_user_main",
    route_intent,
    {
        "graph": "graph",
        "graph_product":"graph_product", 
        "respond_user":"respond_user",
        "graph_search":"graph_search", # 路由返回"graph" → 跳转到graph节点
        END: END           # 路由返回END → 直接结束
    }
)

workflow.add_edge("respond_user",END)


app=workflow.compile()

if __name__=="__main__":
    user=input("输入问题")

    result=app.invoke({
        "messages":[{"role":"user","content":user}]
    })
    ai_msg=result["messages"][-1].content

    print(ai_msg)