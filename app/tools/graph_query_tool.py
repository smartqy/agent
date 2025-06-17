from langchain_core.tools import BaseTool
from typing import List, Dict, Any
from pydantic import Field
from langchain_community.graphs import Neo4jGraph

class GraphQueryTool(BaseTool):
    name = "graph_query"
    description = "查询Neo4j图数据库的工具,接受Cypher语句作为输入,返回查询结果。"
    neo4j_graph: Neo4jGraph = Field(..., description="连接到的Neo4j图数据库实例")

    def _run(self, query: str) -> str:
        try:
            results = self.neo4j_graph.query(query)
            return str(results)
        except Exception as e:
            return f"查询失败: {str(e)}"

    async def _arun(self, query: str) -> str:
        return self._run(query)
