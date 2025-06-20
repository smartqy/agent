from agent import MarketingAnalyticsAgent
from langchain_openai import ChatOpenAI
from langchain_community.graphs import Neo4jGraph
import os
from dotenv import load_dotenv
from tools.analyze_campaign_tool import AnalyzeCampaignTool
from tools.analyze_userBehavior_tool import AnalyzeUserBehaviorTool
from tools.graph_query_tool import GraphQueryTool
from langchain.memory import ConversationBufferMemory
from tools.fallback_tool import FallbackTool
from tools.schema_tool import SchemaTool
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

    
    # 初始化语言模型
    llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-3.5-turbo",
        temperature=0.7
    )
     
    # 初始化工具
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    tools = [
        AnalyzeCampaignTool(neo4j_graph=graph), 
        AnalyzeUserBehaviorTool(neo4j_graph=graph),
        GraphQueryTool(neo4j_graph=graph),
        FallbackTool(llm=llm, memory=memory),
        SchemaTool(neo4j_graph=graph)
    ]

    
    # 创建代理
    agent = MarketingAnalyticsAgent(tools=tools, llm=llm, memory=memory)
    
    return agent

