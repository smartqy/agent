from langchain.tools import BaseTool
from typing import Dict, Any
from langchain_community.graphs import Neo4jGraph
from pydantic import Field

class AnalyzeUserBehaviorTool(BaseTool):
    name: str = "analyze_user_behavior"
    description: str = (
    "Analyze a user's interaction with ads and products using their name.\n\n"
    "Input: a user name or partial name as a plain string (e.g., 'Christopher Cross')\n"
    "Output: behavior summary including views, clicks, conversions, and demographic info.\n\n"
    "Do not wrap the input in 'user_name = ...' format. Just pass the name as-is."
)


    neo4j_graph: Neo4jGraph = Field(description="Neo4j graph instance for querying user behavior data.")

    def _resolve_user_name(self, user_input: str) -> str:
        # Try to find user by name
        name_query = """
        MATCH (u:User)
        WHERE toLower(u.name) CONTAINS toLower($name)
        RETURN u.name AS name
        """
        matches = self.neo4j_graph.query(name_query, params={"name": user_input})

        if not matches:
            raise ValueError(f"No user found with name containing '{user_input}'")

        if len(matches) == 1:
            return matches[0]["name"]

        options = ", ".join([m["name"] for m in matches])
        raise ValueError(f"Multiple users matched: {options}. Please be more specific.")

    def _run(self, user_input: str) -> Dict[str, Any]:
        try:
            user_name = self._resolve_user_name(user_input)
        except Exception as e:
            return {"error": str(e)}

        query = """
        MATCH (u:User)
        WHERE u.name = $user_name
        OPTIONAL MATCH (u)-[v:VIEWED]->(ad1:Ad)
        OPTIONAL MATCH (u)-[c:CLICKED]->(ad2:Ad)
        OPTIONAL MATCH (u)-[conv:CONVERTED]->(p:Product)
        RETURN u.name AS name, u.age AS age, u.location AS location,
               count(DISTINCT ad1) AS views,
               count(DISTINCT ad2) AS clicks,
               sum(toInteger(c.click_count)) AS total_clicks,
               count(DISTINCT p) AS conversions,
               sum(toFloat(conv.conversion_value)) AS total_conversion_value
        """

        result = self.neo4j_graph.query(query, params={"user_name": user_name})
        if not result:
            return {"error": f"No behavior data found for user '{user_name}'"}

        r = result[0]
        return {
            "name": r.get("name", "Unknown"),
            "age": r.get("age", "N/A"),
            "location": r.get("location", "N/A"),
            "views": r["views"] or 0,
            "clicks": r["clicks"] or 0,
            "total_clicks": r["total_clicks"] or 0,
            "conversions": r["conversions"] or 0,
            "total_conversion_value": float(r["total_conversion_value"] or 0),
            "summary": (
                f"{r.get('name')} (age {r.get('age')}) viewed {r['views']} ads, "
                f"clicked {r['total_clicks']} times on {r['clicks']} ads, "
                f"and converted on {r['conversions']} products totaling "
                f"${r['total_conversion_value']:.2f}."
            )
        }

    async def _arun(self, user_input: str) -> Dict[str, Any]:
        return self._run(user_input)
