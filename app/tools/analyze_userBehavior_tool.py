from langchain.tools import BaseTool
from typing import Dict, Any
from langchain_community.graphs import Neo4jGraph
from pydantic import Field

class AnalyzeUserBehaviorTool(BaseTool):
    name: str = "analyze_user_behavior"
    description: str = "Analyzes user behavior data to identify patterns and insights."
    neo4j_graph: any = Field(description="Neo4j graph instance for querying user behavior data.")

    def _run(self, user_id: str) -> Dict[str, Any]:
        # Query Neo4j for user behavior data
        query = """
        MATCH (u:User {id: $user_id})
        RETURN u
        """
        result = self.neo4j_graph.query(query, params={"user_id": user_id})
        if not result:
            return {"error": "User not found"}
        user_data = result[0]
        return {
            "user_id": user_id,
            "behavior_pattern": user_data.get("behavior_pattern", "Unknown"),
            "insights": user_data.get("insights", "No insights available.")
        }

    async def _arun(self, user_id: str) -> Dict[str, Any]:
        return self._run(user_id) 