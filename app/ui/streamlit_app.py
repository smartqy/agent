import streamlit as st
from streamlit.logger import get_logger
import json
import asyncio
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_loader import load_data, insert_data, load_graph
from main import init_agent

# Define the logger
logger = get_logger(__name__)

def render_data_loader():
    st.header("Data Catalogue Data Loader")
    st.caption("Go to http://localhost:7474/ to explore the graph.")

    if st.button("Import", type="primary"):
        with st.spinner("Loading... This might take a minute or two."):
            try:
                data = load_data()
                graph = load_graph()
                success = insert_data(data=data, neo4j_graph=graph)
                st.success("Import successful", icon="✅")
                st.caption("Go to http://localhost:7474/ to interact with the database")
            except Exception as e:
                st.error(f"Error: {e}", icon="🚨")

async def render_marketing_analysis():
    st.header("营销分析智能代理系统")
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

def main():
    # 创建侧边栏导航
    st.sidebar.title("功能导航")
    page = st.sidebar.radio("选择功能", ["数据加载", "营销分析"])
    
    if page == "数据加载":
        render_data_loader()
    else:
        asyncio.run(render_marketing_analysis())

if __name__ == "__main__":
    main() 