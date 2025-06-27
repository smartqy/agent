from langchain.tools import BaseTool
from typing import Dict, Any
from langchain_community.graphs import Neo4jGraph
from pydantic import Field
from langchain_core.tools import BaseTool


from langchain.tools import BaseTool
from typing import Dict, Any
from langchain_community.graphs import Neo4jGraph
from pydantic import Field

class AnalyzeCampaignTool(BaseTool):
    name: str = "analyze_campaign"
    description: str = (
        "Analyze campaign performance, demographic targeting, and ad engagement in the Neo4j graph.\n\n"
        "Input: campaign name or partial name (string).\n"
        "Returns: budget, duration, targeted demographics, total ads, views, clicks, conversions, ROI.\n"
        "Use when asked:\n"
        "- What is the performance of Campaign X?\n"
        "- How many ads were there, and how well did they perform?\n"
        "- Who was targeted and what is the ROI?"
    )

    neo4j_graph: Neo4jGraph = Field(description="Neo4j graph instance for querying campaign data.")

    def _run(self, campaign_name: str) -> Dict[str, Any]:
        query = """
        MATCH (c:Campaign)
        WHERE toLower(c.name) CONTAINS toLower($campaign_name)
        OPTIONAL MATCH (c)-[:TARGETS]->(d:Demographic)
        OPTIONAL MATCH (a:Ad)-[:PART_OF]->(c)
        OPTIONAL MATCH (u:User)-[v:VIEWED]->(a)
        OPTIONAL MATCH (u)-[cl:CLICKED]->(a)
        OPTIONAL MATCH (u)-[conv:CONVERTED]->(p:Product)
        RETURN 
            c.name AS campaign_name,
            c.start_date AS start,
            c.end_date AS end,
            c.campaign_budget AS budget,
            collect(DISTINCT d.age_group + "-" + d.gender) AS targets,
            count(DISTINCT a) AS ad_count,
            count(DISTINCT v) AS views,
            count(DISTINCT cl) AS clicks,
            sum(toInteger(cl.click_count)) AS total_clicks,
            count(DISTINCT p) AS conversions,
            sum(toFloat(conv.conversion_value)) AS total_conversion_value
        """

        result = self.neo4j_graph.query(query, params={"campaign_name": campaign_name})
        if not result:
            return {"error": f"No campaign matched name: {campaign_name}"}

        r = result[0]
        roi = (
            float(r["total_conversion_value"] or 0) / float(r["budget"])
            if r["budget"] not in (None, 0, "N/A") else None
        )

        return {
            "campaign_name": r.get("campaign_name", "Unknown"),
            "start_date": r.get("start", "N/A"),
            "end_date": r.get("end", "N/A"),
            "budget": r.get("budget", "N/A"),
            "target_demographics": r.get("targets", []),
            "ad_count": r["ad_count"],
            "views": r["views"],
            "clicks": r["clicks"],
            "total_clicks": r["total_clicks"] or 0,
            "conversions": r["conversions"],
            "total_conversion_value": float(r["total_conversion_value"] or 0),
            "roi": round(roi, 2) if roi is not None else "N/A",
            "summary": (
                f"Campaign '{r.get('campaign_name')}' ran from {r.get('start')} to {r.get('end')} "
                f"with ${r.get('budget')} budget, targeting {', '.join(r.get('targets', []))}. "
                f"It had {r['ad_count']} ads, {r['views']} views, {r['total_clicks']} clicks, and "
                f"{r['conversions']} conversions totaling ${r['total_conversion_value']:.2f}. "
                f"ROI: {round(roi, 2) if roi else 'N/A'}."
            )
        }

    async def _arun(self, campaign_name: str) -> Dict[str, Any]:
        return self._run(campaign_name)
