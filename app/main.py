from agent import MarketingAnalyticsAgent
from tools import AnalyzeCampaignTool, AnalyzeUserBehaviorTool
from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph
import os
from dotenv import load_dotenv
import streamlit as st
import asyncio
from tools.graph_query_tool import GraphQueryTool

# Load environment variables
load_dotenv("config/.env_loader")

def init_neo4j():
    """初始化Neo4j连接"""
    url = os.getenv("NEO4J_URI")
    username = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")
    
    if not all([url, username, password]):
        raise ValueError("请确保在loader/.env_loader文件中设置了NEO4J_URI, NEO4J_USERNAME和NEO4J_PASSWORD")
    
    return Neo4jGraph(url=url, username=username, password=password)

neo4j_graph = init_neo4j()

def init_agent():
    """初始化营销分析代理系统"""
    # 初始化Neo4j连接
    graph = init_neo4j()
    
    # 初始化工具
    tools = [AnalyzeCampaignTool(neo4j_graph=graph), AnalyzeUserBehaviorTool(neo4j_graph=graph),GraphQueryTool(neo4j_graph=graph)]

    
    # 初始化语言模型
    llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini",
        temperature=0
    )
    
    # 创建代理
    agent = MarketingAnalyticsAgent(tools=tools, llm=llm)
    
    return agent


# Example usage
# Streamlit界面
async def main():
    st.title("营销分析智能代理系统")
    st.caption("基于Neo4j图数据库的营销活动分析系统")
    
    # 初始化会话状态
    if "agent" not in st.session_state:
        st.session_state.agent = init_agent()
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # 显示可用工具
    with st.expander("可用分析工具"):
        tools = st.session_state.agent.get_available_tools()
        for tool in tools:
            st.write(f"- {tool}")
    
    # 用户输入
    user_input = st.text_area("请输入您的分析需求：", height=100)
    
    if st.button("分析", type="primary"):
        if user_input:
            with st.spinner("正在分析..."):
                # 执行分析
                result = await st.session_state.agent.analyze(
                    query=user_input,
                    chat_history=st.session_state.chat_history
                )
                
                # 更新对话历史
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": user_input
                })
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": result["analysis"]
                })
                
                # 显示分析结果
                st.markdown("### 分析结果")
                st.write(result["analysis"])
                
                # 显示中间步骤（可选）
                with st.expander("查看分析过程"):
                    for step in result["intermediate_steps"]:
                        st.write(f"工具: {step[0].tool}")
                        st.write(f"输入: {step[0].tool_input}")
                        st.write(f"输出: {step[1]}")
                        st.write("---")
        else:
            st.warning("请输入分析需求")

if __name__ == "__main__":
    asyncio.run(main())