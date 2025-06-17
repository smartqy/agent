from typing import List, Dict, Any
from langchain.agents import AgentExecutor
from langchain.tools import BaseTool
from langchain.agents import initialize_agent, AgentType
from typing import List, Dict, Any, Optional
from langchain.memory import ConversationBufferMemory

class MarketingAnalyticsAgent:
    """核心营销分析代理类"""
    
    def __init__(self, tools: List[BaseTool], llm: Any, memory: ConversationBufferMemory):
        """
        初始化营销分析代理
        
        Args:
            tools: 代理可用的工具列表
            llm: 语言模型实例
        """
        self.tools = tools
        self.llm = llm
        self.memory = memory
        self.agent_executor = self._create_agent_executor()
        
    def _create_agent_executor(self) -> AgentExecutor:
        """构建基于 Function Calling 的 Agent"""
        return initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
        )
    
    def analyze_sync(self, query: str) -> str:
        """同步调用分析"""
        return self.agent_executor.run(query)

    async def analyze(self, query: str,  chat_history: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        异步执行分析任务（可用于 Streamlit）

        Args:
            query: 用户输入的自然语言请求
            chat_history: 可选的对话历史（暂未使用）

        Returns:
            包含分析结果与中间步骤的字典
        """
        result = await self.agent_executor.ainvoke({"input": query})
        return {
            "analysis": result["output"],
            "intermediate_steps": result.get("intermediate_steps", [])
        }
    
    def get_available_tools(self) -> List[str]:
        """获取可用工具列表"""
        return [tool.name for tool in self.tools] 