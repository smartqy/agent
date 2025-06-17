import streamlit as st
from streamlit.logger import get_logger
import json
import asyncio
import sys
import os


# ✅ Streamlit 页面配置必须在最前面
st.set_page_config(page_title="营销分析智能代理系统", layout="centered")

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
    st.markdown("<h1 style='text-align: center;'>📊 营销分析智能代理系统</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>基于 Neo4j 图数据库的营销活动分析助手</p>", unsafe_allow_html=True)

    # 初始化 Agent
    if "agent" not in st.session_state:
        st.session_state.agent = init_agent()

    # ✅ 提问提示
    with st.expander("📘 提问提示", expanded=True):
        st.markdown("""
- ✅ **支持的问题示例**：
    - 哪些用户点击了广告 A？
    - 活动 C 的 ROI 表现如何？
    - 用户 user_12 最近有哪些行为？
- ❌ **不支持的问题示例**：
    - 我是谁？
    - 今天天气怎么样？
    - 你爱我吗？
        """)

    # ✅ 显示可用工具
    with st.expander("🛠️ 可用分析工具"):
        tools = st.session_state.agent.get_available_tools()
        for tool in tools:
            st.markdown(f"- `{tool}`")

    # ✅ 用户输入框
    user_input = st.text_area("✍️ 请输入您的分析需求：", height=100, placeholder="例如：用户 user_23 最近点击了哪些广告？")

    # ✅ 分析按钮
    if st.button("🔍 分析", type="primary"):
        if user_input.strip():
            with st.spinner("正在分析，请稍候..."):
                try:
                    result = await st.session_state.agent.analyze(query=user_input)

                    # ✅ 分析结果
                    st.markdown("### ✅ 分析结果")
                    st.write(result["analysis"])

                    # ✅ 中间步骤
                    with st.expander("📂 查看分析过程"):
                        for step in result["intermediate_steps"]:
                            st.markdown(f"**工具：** `{step[0].tool}`")
                            st.markdown(f"**输入：** `{step[0].tool_input}`")
                            st.markdown(f"**输出：**\n```\n{step[1]}\n```")
                            st.markdown("---")
                except Exception as e:
                    st.error(f"发生错误：{str(e)}")
        else:
            st.warning("⚠️ 请输入有效的分析需求。")

    # ✅ 显示对话历史
    with st.expander("💬 对话历史"):
        for msg in st.session_state.agent.agent_executor.memory.chat_memory.messages:
            st.write(f"**{msg.type.title()}**: {msg.content}")
    
    with st.expander("🧠 当前记忆内容（调试用）"):
        for msg in st.session_state.agent.agent_executor.memory.chat_memory.messages:
            st.markdown(f"**{msg.type.title()}**: {msg.content}")

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