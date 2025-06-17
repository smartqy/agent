from typing import List, Dict, Any
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import BaseTool
from langchain_core.messages import AIMessage, HumanMessage

class MarketingAnalyticsAgent:
    """核心营销分析代理类"""
    
    def __init__(self, tools: List[BaseTool], llm: Any):
        """
        初始化营销分析代理
        
        Args:
            tools: 代理可用的工具列表
            llm: 语言模型实例
        """
        self.tools = tools
        self.llm = llm
        self.agent_executor = self._create_agent_executor()
        
    def _create_agent_executor(self) -> AgentExecutor:
        """创建代理执行器"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个专业的营销分析专家，擅长分析营销活动数据并提供有价值的商业洞察。
            你可以使用各种工具来分析数据,包括活动分析、用户行为分析、ROI计算等。
            请根据用户的需求，选择合适的工具进行分析，并提供清晰的分析结果和建议。
            必须通过图数据库(Neo4j)查询实现,不能靠臆断"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = (
            {
                "input": lambda x: x["input"],
                "chat_history": lambda x: x["chat_history"],
                "agent_scratchpad": lambda x: format_to_openai_function_messages(
                    x["intermediate_steps"]
                ),
            }
            | prompt
            | self.llm
            | OpenAIFunctionsAgentOutputParser()
        )
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )
    
    async def analyze(self, query: str, chat_history: List[Dict] = None) -> Dict[str, Any]:
        """
        执行分析任务
        
        Args:
            query: 用户的分析请求
            chat_history: 对话历史
            
        Returns:
            分析结果和建议
        """
        if chat_history is None:
            chat_history = []
            
        result = await self.agent_executor.ainvoke({
            "input": query,
            "chat_history": chat_history
        })
        
        intermediate_steps = result.get("intermediate_steps", [])
        
        return {
            "analysis": result["output"],
            "intermediate_steps": intermediate_steps
        }
    
    def get_available_tools(self) -> List[str]:
        """获取可用工具列表"""
        return [tool.name for tool in self.tools] 