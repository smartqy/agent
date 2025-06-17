# tools/fallback_tool.py
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from pydantic import Field
from typing import Optional
from langchain.memory import ConversationBufferMemory

class FallbackTool(BaseTool):
    name: str = "fallback_tool"
    description: str = "用于与用户闲聊、回答无关问题，例如：你是谁、天气如何等。"
    return_direct: bool = True  # ✅ 防止陷入死循环

    llm: ChatOpenAI
    memory: ConversationBufferMemory  # 新增 memory 字段
    fallback_prompt: str = Field(
        default=(
            "你是一个友好、健谈且乐于助人的 AI 助手。"
            "你可以参考与用户的对话历史，结合用户之前说过的话来回答。"
            "你不会回答与营销分析或数据库相关的专业问题。"
            "请用简洁、自然、有趣的方式和用户闲聊。"
            "如果用户问你是谁、天气如何、喜欢什么等，请随意发挥。"
            "对话历史：\n{history}\n用户问："
        )
    )

    def _run(self, query: str) -> str:
        # 拼接历史
        history = ""
        if self.memory:
            for msg in self.memory.chat_memory.messages:
                history += f"{msg.type.title()}: {msg.content}\n"
        prompt = self.fallback_prompt.format(history=history) + query
        return self.llm.invoke(prompt).content

    async def _arun(self, query: str) -> str:
        history = ""
        if self.memory:
            for msg in self.memory.chat_memory.messages:
                history += f"{msg.type.title()}: {msg.content}\n"
        prompt = self.fallback_prompt.format(history=history) + query
        return (await self.llm.ainvoke(prompt)).content
