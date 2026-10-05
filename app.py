from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json

from main import app as graph_app

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    messages: list
    thread_id: str

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    async def generate():
        config = {"configurable": {"thread_id": request.thread_id}}
        full_content = ""  # 用来累加完整的回答内容

        async for event in graph_app.astream_events(
            {"messages": request.messages},
            config=config,
            version="v1"
        ):
            # 只监听 respond_user 节点的 LLM 输出
            if (
                event["event"] == "on_chat_model_stream"
                and event["metadata"].get("langgraph_node") == "respond_user"
            ):
                chunk = event["data"]["chunk"]
                if chunk and chunk.content:
                    full_content += chunk.content  # 累加内容
                    yield f"data: {json.dumps({'text': full_content})}\n\n"#向前端推送东西

    return StreamingResponse(generate(), media_type="text/event-stream")