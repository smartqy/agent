# tools/fallback_tool.py
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI
from pydantic import Field
from typing import Optional
from langchain.memory import ConversationBufferMemory

class FallbackTool(BaseTool):
    name: str = "fallback_tool"
    description: str = "Used for casual conversation with the user and answering unrelated questions, such as: who are you, how is the weather, etc."
    return_direct: bool = True  # ✅ Prevent infinite loops

    llm: ChatOpenAI
    memory: ConversationBufferMemory  # Added memory field
    fallback_prompt: str = Field(
        default=(
        "You are a friendly, humorous, and talkative AI assistant who enjoys casual conversation with the user. "
        "You have access to the full conversation history below.\n\n"
        "If the user asks about something they mentioned earlier (e.g., 'What did I just say my name is?'), please look through the conversation history and answer based on the user's previous statements.\n\n"
        "Your role is to answer **non-technical** questions that are unrelated to marketing analytics, data science, or databases. "
        "For example, feel free to chat about yourself, the weather, hobbies, movies, or anything light-hearted.\n\n"
        "If the user's question is about **analytics, tools, graphs, campaigns, or data**, do NOT answer it. "
        "Instead, politely say: 'That sounds like something my expert teammate would be better at. Try rephrasing that in the analysis section.'\n\n"
        "Conversation history:\n{history}\n\n"
        "Now the user asks: {query}\n"
        "Respond naturally and helpfully:"
        )
    )

    def _run(self, query: str) -> str:
        # Concatenate history
        history = ""
        if self.memory:
            for msg in self.memory.chat_memory.messages:
                history += f"{msg.type.title()}: {msg.content}\n"
        prompt = self.fallback_prompt.format(history=history, query=query)
        return self.llm.invoke(prompt).content

    async def _arun(self, query: str) -> str:
        history = ""
        if self.memory:
            for msg in self.memory.chat_memory.messages:
                history += f"{msg.type.title()}: {msg.content}\n"
        prompt = self.fallback_prompt.format(history=history, query=query)
        return (await self.llm.ainvoke(prompt)).content
