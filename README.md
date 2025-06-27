# 💡 Marketing Analytics Agent System

An intelligent marketing data analytics assistant powered by LangChain and Neo4j.

---

## 📌 Project Overview

This project is a **marketing data analysis system** built with the Neo4j graph database and LangChain Agent framework. Users can query campaigns, ads, user behavior, demographics, and more using natural language. The system automatically selects the appropriate tools to perform the analysis and returns structured results.

---

## 🔧 Features

- **Campaign ROI Analysis** (budget, total conversions, ROI)
- **Audience Segmentation** (by age group, gender, etc.)
- **User Behavior Analysis** (views, clicks, conversions)
- **Behavior Summary** (aggregate user actions)
- **Graph Data Exploration** (node types, relationship types, attribute fields)
- **Multi-turn Conversation Memory** (maintains context via Agent memory)
- **Pluggable Tool System** (supports Cypher queries and more)

---

## 🚀 Setup & Run

1. **Clone the Repository**:

   ```bash
   git clone git@github.com:smartqy/agent.git
   ```

2. **Install Dependencies**:

   ```bash
   pip3 install -r requirements.txt
   ```

3. **Configure Neo4j and OpenAI Keys**:  
   Create a `.env_loader` file and include the following:

   ```env
   OPENAI_API_KEY=your_openai_key
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=your_password
   ```

4. **Run the Streamlit App**:

   ```bash
   streamlit run app/ui/streamlit_app.py
   ```

---

## 🥪 Sample Questions

### Campaign Analysis

- How is campaign_12 performing?
- What is the ROI of the "Back to School" campaign?
- Which campaign has the highest conversion rate?

### User Behavior

- Show me the click and conversion records of user_12.
- How many ads has user Alice viewed?
- What is the total conversion value for Sarah?

### Graph Exploration

- What node types exist in the graph?
- What attributes do the nodes have?
- Use Cypher to query user click behavior.

---

## 🛠️ Built-in Tools

| Tool Name               | Description                                             |
| ----------------------- | ------------------------------------------------------- |
| `analyze_campaign`      | Analyze ROI, ad count, target audience of campaigns     |
| `analyze_user_behavior` | Summarize user actions: views, clicks, conversions      |
| `schema_tool`           | Inspect graph schema (nodes, relationships, attributes) |
| `graph_query`           | Execute Cypher queries (for technical requests)         |
| `fallback_tool`         | Handle chit-chat or unrelated questions                 |

---

## 📁 Project Structure

```
.
├── app/
│   ├── __pycache__/                # Cache directory (can be ignored)
│   ├── tools/                      # Built-in tools (e.g. campaign analysis, graph queries)
│   │   ├── analyze_campaign_tool.py
│   │   ├── analyze_userBehavior_tool.py
│   │   ├── graph_query_tool.py
│   │   ├── fallback_tool.py
│   │   └── schema_tool.py
│   └── ui/
│       └── streamlit_app.py        # Main UI (Streamlit page)
├── config/
│   └── .env_loader/                # Environment variable loader
├── data/
│   └── dummy_graph_data.json       # Sample graph data
├── .env                            # Environment variables (.env file: API keys, DB config)
├── agent.py                        # Agent builder class
├── data_loader.py                  # Functions for importing and writing data to Neo4j
├── main.py                         # Entry point for initializing the Agent
├── requirements.txt                # Python project dependencies
└── README.md                       # Project documentation
```

---

## 🧠 Tech Stack

- [LangChain](https://www.langchain.com/)
- [Neo4j](https://neo4j.com/)
- [OpenAI GPT](https://platform.openai.com/)
- [Streamlit](https://streamlit.io/)
- Python 3.10+
