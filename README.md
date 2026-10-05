# E-commerce Agent

基于 **LangGraph + LangChain** 的电商智能客服 Agent，支持意图识别、订单/商品查询、数据统计，以及基于 RAG 的售后政策问答，并通过 FastAPI 提供流式接口。

## 功能特性

- **意图识别**：自动判断用户输入属于「商品查询 / 订单查询 / 客服咨询 / 数据统计 / 其它」五类之一
- **订单查询**：通过 MySQL 查询订单、物流、退款等信息
- **商品查询**：按关键词检索商品、价格、库存
- **数据统计**：销量、销售额、订单量等日报统计
- **客服咨询（RAG）**：基于 FAQ 知识库（Chroma 向量库）回答售后、包邮、退货、退款、发货时间等问题
- **流式输出**：FastAPI + SSE 向前端实时推送回答

## 技术栈

- **Agent 框架**：LangGraph、LangChain
- **模型**：通义千问 `qwen-plus`（DashScope OpenAI 兼容接口）
- **向量检索**：Chroma + `text-embedding-v3`
- **后端**：FastAPI + Uvicorn
- **数据库**：MySQL（mysql-connector-python）
- **追踪**：LangSmith

## 项目结构

```
E-commerce_agent/
├── app.py                        # FastAPI 入口，提供 /chat/stream 流式接口
├── main.py                       # 主 Agent：意图识别 + 路由（LangGraph）
├── index.html                    # 前端聊天页面
├── requirements.txt              # Python 依赖
├── agent/
│   ├── db_agent.py               # 订单查询子 Agent
│   ├── product_inquiry_agent.py  # 数据统计子 Agent
│   ├── product_search_agent.py   # 商品查询子 Agent
│   └── rag_agent.py              # 客服咨询 RAG 子 Agent
├── tools/
│   ├── db_tools.py               # MySQL 查询工具
│   ├── rag_tools.py              # 知识库检索工具
│   └── ingest_docs.py            # 知识库文档入库脚本
├── mysql_connect/
│   ├── mysql_db.py               # MySQL 连接封装
│   └── test_db.py                # 数据库连接测试
├── orders.sql / product.sql / user.sql   # 数据库表结构
├── FAQ.txt / FAQ.pdf             # 客服知识库文档
└── chroma_db/                    # 向量库（入库后生成，已忽略）
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

在项目根目录创建 `.env` 文件：

```
DASHSCOPE_API_KEY=你的阿里云百炼 API Key
LANGCHAIN_API_KEY=你的 LangSmith API Key（可选，用于追踪）
```

> `.env` 已在 `.gitignore` 中忽略，请勿提交。

### 3. 初始化数据库

导入表结构：

```bash
mysql -u root -p < user.sql
mysql -u root -p < product.sql
mysql -u root -p < orders.sql
```

并修改 `mysql_connect/mysql_db.py` 末尾的数据库连接信息：

```python
db = MySQLDatabase(
    host="localhost",
    port=3306,
    user="root",
    password="你的密码",
    database="你的数据库名"
)
```

### 4. 构建知识库（RAG）

将 FAQ 文档写入向量库：

```bash
python -m tools.ingest_docs
```

该脚本会扫描根目录下的 `.txt` / `.pdf` 文档，切分后写入 `chroma_db/`（按文件 MD5 去重）。

### 5. 启动服务

```bash
uvicorn app:app --reload
```

访问 `http://localhost:8000` 打开前端页面。

## API 说明

### `POST /chat/stream`

流式对话接口（SSE）。

请求体：

```json
{
  "messages": [{"role": "user", "content": "满多少包邮？"}],
  "thread_id": "会话ID"
}
```

响应为 `text/event-stream`，每段数据格式：

```
data: {"text": "累计的完整回答内容"}
```

## 意图路由

| 用户意图 | 示例 | 路由到 |
|---------|------|--------|
| 商品查询 | 查商品、推荐、价格、库存 | `product_search_agent` |
| 订单查询 | 查订单、物流、发货、退款 | `db_agent` |
| 客服咨询 | 售后、规则、包邮、退货、发货时间 | `rag_agent` |
| 数据统计 | 销量、销售额、订单量、日报 | `product_inquiry_agent` |
| 其它 | 闲聊、无关内容 | 直接回复 |
