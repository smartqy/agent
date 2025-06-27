import streamlit as st
from streamlit.logger import get_logger
import json
import asyncio
import sys
import os


#  Streamlit page config must be at the top
st.set_page_config(page_title="Marketing Analytics Agent System", layout="centered")

# Add project root to Python path
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
    st.markdown("<h1 style='text-align: center;'>📊 Marketing Analytics Agent System</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>A marketing campaign analysis assistant based on Neo4j graph database</p>", unsafe_allow_html=True)

    # Initialize Agent
    if "agent" not in st.session_state:
        st.session_state.agent = init_agent()

    # Question hints
    with st.expander("📘 Question Hints", expanded=False):
        st.markdown("""
### 📈 Campaign Analysis
- What is the performance of campaign_12?
- What’s the ROI of campaign 'Back to School'?
- Which campaign had the best ROI?
- How many ads were linked to campaign Black Friday?

### 🎯 Demographic Targeting
- Who did the ‘Summer Sale’ campaign target?
- What gender and age group was campaign Holiday Deals aimed at?

### 📢 Ad Engagement
- How many ads were created in campaign_01?
- What’s the total number of ad views and clicks for campaign C?

### 🛍️ Product Conversion
- How many products were converted via campaign_08?
- What is the total conversion value of 'Spring Promo'?

---

### 👤 User Profile
- Who is user Christopher Cross?
- Tell me about user Alice.
- Where is user Bob from? How old is he?

### 👁️ Viewing Behavior
- How many ads has Lisa seen?
- Which ads did James view?

### 🖱️ Clicking Behavior
- How many ads did user_12 click?
- What’s the total click count for Tom?

### 💰 Conversion Behavior
- Did Sarah convert any product?
- How much value did user_23 generate?

### 🧾 User Summary
- Summarize user Emma’s behavior.
- What did Bob do across ads and products?

---

### 🧪 Technical (Cypher Queries)
- MATCH (u:User) WHERE u.age > 30 RETURN u.name
- Show me all relationships involving Product
- List all users who clicked an ad

---

### 🧬 Schema Inspection
- What labels exist in this graph?
- Show all relationship types in the database.
- What properties do Campaign nodes have?
""")


    # Show available tools
    with st.expander("🛠️ Available Analysis Tools"):
        tools = st.session_state.agent.get_available_tools()
        for tool in tools:
            st.markdown(f"- `{tool}`")

    # User input box
    user_input = st.text_area("✍️ Please enter your analysis request:", height=100, placeholder="e.g.: What ads did user_23 click recently?")

    # Analyze button
    if st.button("🔍 Analyze", type="primary"):
        if user_input.strip():
            with st.spinner("Analyzing, please wait..."):
                try:
                    result = await st.session_state.agent.analyze(query=user_input)

                    # Analysis result
                    st.markdown("### ✅ Analysis Result")
                    st.write(result["analysis"])

                    # Intermediate steps
                    with st.expander("📂 View Analysis Steps"):
                        for step in result["intermediate_steps"]:
                            st.markdown(f"**Tool:** `{step[0].tool}`")
                            st.markdown(f"**Input:** `{step[0].tool_input}`")
                            st.markdown(f"**Output:**\n```{step[1]}\n```")
                            st.markdown("---")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("⚠️ Please enter a valid analysis request.")

    # ✅ Show memory content (for debugging)
    # with st.expander("💬 Chat History"):
    #     for msg in st.session_state.agent.agent_executor.memory.chat_memory.messages:
    #         st.write(f"**{msg.type.title()}**: {msg.content}")

    with st.expander("🧠 Current Memory Content (Debug)"):
        for msg in st.session_state.agent.agent_executor.memory.chat_memory.messages:
            st.markdown(f"**{msg.type.title()}**: {msg.content}")

def render_chat_history():
    st.header("💬 Query History")
    if "agent" in st.session_state:
        messages = st.session_state.agent.agent_executor.memory.chat_memory.messages
        if not messages:
            st.info("No history records.")
            return

        # Show Human-AI pairs
        for i in range(0, len(messages), 2):
            user_msg = messages[i]
            ai_msg = messages[i+1] if i+1 < len(messages) else None
            st.markdown(f"**🧑 User:** {user_msg.content}")
            if ai_msg:
                st.markdown(f"**🤖 AI:** {ai_msg.content}")
            st.markdown("---")
    else:
        st.info("No tool usage records yet. Please ask a question in Marketing Analysis first.")


def render_tool_debug():
    st.header("🧪 Tool Call Debug")
    if "agent" in st.session_state:
        try:
            result = st.session_state.agent.last_result  # Assume you save the last result in analyze()
            st.markdown("### 🔧 Tool Call Process")
            for step in result["intermediate_steps"]:
                st.markdown(f"**Tool:** `{step[0].tool}`")
                st.markdown(f"**Input:** `{step[0].tool_input}`")
                st.markdown(f"**Output:**\n```{step[1]}\n```")
                st.markdown("---")
        except Exception:
            st.info("No tool usage records yet. Please ask a question in Marketing Analysis first.")
    else:
        st.info("Agent is not initialized.")

def main():
    # Create sidebar navigation
    st.sidebar.title("Function Navigation")
    page = st.sidebar.radio("Select Function", ["Data Loader", "Marketing Analysis", "Query History", "Tool Debug"])
    
    if page == "Data Loader":
        render_data_loader()
    elif page == "Marketing Analysis":
        asyncio.run(render_marketing_analysis())
    elif page == "Query History":
        render_chat_history()
    elif page == "Tool Debug":
        render_tool_debug()
    else:
        asyncio.run(render_marketing_analysis())

if __name__ == "__main__":
    main() 