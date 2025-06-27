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
    """Initialize Neo4j connection"""
    url = os.getenv("NEO4J_URI")
    username = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")
    
    if not all([url, username, password]):
        raise ValueError("Please make sure NEO4J_URI, NEO4J_USERNAME, and NEO4J_PASSWORD are set in loader/.env_loader")
    
    return Neo4jGraph(url=url, username=username, password=password)

neo4j_graph = init_neo4j()

def init_agent():
    """Initialize the marketing analytics agent system"""
    # Initialize Neo4j connection
    graph = init_neo4j()

    # Initialize language model
    llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-3.5-turbo",
        temperature=0.7
    )
     
    # Initialize memory
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )
    
    # Initialize tools
    tools = [
        AnalyzeCampaignTool(neo4j_graph=graph), 
        AnalyzeUserBehaviorTool(neo4j_graph=graph),
        GraphQueryTool(neo4j_graph=graph),
        FallbackTool(llm=llm, memory=memory),
        SchemaTool(neo4j_graph=graph)
    ]

    # Create agent
    agent = MarketingAnalyticsAgent(tools=tools, llm=llm, memory=memory)
    
    return agent

