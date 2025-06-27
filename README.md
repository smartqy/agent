# 🧠 Marketing Analytics Agent

一个基于 [LangChain](https://github.com/langchain-ai/langchain) 和 [Neo4j](https://neo4j.com/) 的智能 Agent，用于通过自然语言进行营销数据分析。

## 📌 项目简介

本系统构建了一个上下文感知、工具驱动的智能分析代理（Agent），可执行以下操作：

- 📊 广告活动分析（ROI、点击、转化等）
- 🧍‍♂️ 用户行为分析（浏览、点击、转化等）
- 🔍 图数据库查询（Cypher）
- 🧠 数据模型展示（节点、属性、关系）
- 💬 闲聊支持（非分析类问题）

## 🔧 核心模块

### `MarketingAnalyticsAgent`

封装了分析逻辑的核心类，支持同步和异步查询：

```python
agent = MarketingAnalyticsAgent(tools=[...], llm=..., memory=...)
agent.analyze_sync("How did Campaign Alpha perform?")

marketing-agent/
│
├── agent.py                 # 主 Agent 类
├── tools/
│   ├── campaign_tool.py
│   ├── user_tool.py
│   ├── graph_tool.py
│   ├── schema_tool.py
│   └── fallback_tool.py
├── app.py                   # CLI 或 Streamlit 界面（可选）
├── requirements.txt
└── README.md
```
