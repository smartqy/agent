from typing import List, Dict, Any, Optional
from langchain.agents import AgentExecutor
from langchain.tools import BaseTool
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import SystemMessage

class MarketingAnalyticsAgent:
    """Core marketing analytics agent class"""
    
    def __init__(self, tools: List[BaseTool], llm: Any, memory: ConversationBufferMemory):
        """
        Initialize the marketing analytics agent
        
        Args:
            tools: List of available tools for the agent
            llm: Language model instance
        """
        self.tools = tools
        self.llm = llm
        self.memory = memory
        self.agent_executor = self._create_agent_executor()
        
    def _create_agent_executor(self) -> AgentExecutor:
        system_message = SystemMessage(content="""
        You are an intelligent marketing analytics agent. You have access to prior conversation history.
        Always resolve references like "he", "she", or "they" by checking the memory for prior user mentions.
        Use tools only if necessary and maintain context between user turns.
        """)
        return initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent_type=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,  
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            agent_kwargs={"system_message": system_message}, 
        )

    
    def analyze_sync(self, query: str) -> str:
        """Synchronous analysis call"""
        return self.agent_executor.run(query)

    async def analyze(self, query: str,  chat_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Asynchronous analysis task (for use with Streamlit)

        Args:
            query: User's natural language request
            chat_history: Optional conversation history (currently unused)

        Returns:
            Dictionary containing analysis result and intermediate steps
        """
        result = await self.agent_executor.ainvoke({"input": query})
        return {
            "analysis": result["output"],
            "intermediate_steps": result.get("intermediate_steps", [])
        }
    
    def get_available_tools(self) -> List[str]:
        """Get the list of available tools"""
        return [tool.name for tool in self.tools] 