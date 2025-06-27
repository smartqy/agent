from typing import Any, Dict, List
from langchain_community.graphs import Neo4jGraph
from langchain_core.tools import BaseTool
from pydantic import Field

class GraphQueryTool(BaseTool):
    name: str = "graph_query"
    description: str = (
    "Execute Cypher queries against the Neo4j graph database that stores marketing-related data.\n\n"
    "-Input format: a valid Cypher query string (without backticks).\n"
    "   For example: MATCH (n) RETURN n LIMIT 10\n\n"
    "- Supported operations:\n"
    "- Retrieve nodes, relationships, or properties\n"
    "- Filter entities based on attributes (e.g., age > 30)\n"
    "- Perform graph pattern matching (e.g., campaigns → users)\n"
    "- Execute aggregations, counts, groupings, etc.\n\n"
    "-Ensure that your query uses correct Cypher syntax.\n"
    "This tool is ideal when the user explicitly asks a technical query involving structure or data from the graph."
    )

    neo4j_graph: Neo4jGraph = Field(..., description="Connected Neo4j graph database instance")

    def _run(self, query: str) -> str:
        try:
            result = self.neo4j_graph.query(query)
            return self._format_output(result)
        except Exception as e:
            return f"Query execution failed: {str(e)}"

    async def _arun(self, query: str) -> str:
        return self._run(query)

    def _format_output(self, result: List[Dict[str, Any]]) -> str:
        if not result:
            return "No results returned from the query."

        formatted_result = []
        for row in result:
            row_str = []
            for key, value in row.items():
                if isinstance(value, dict):
                    if "labels" in value:
                        labels = value.get("labels", [])
                        props = value.get("properties", {})
                        row_str.append(f"{key}: Node{labels} {props}")
                    elif "type" in value:
                        rel_type = value.get("type", "")
                        props = value.get("properties", {})
                        row_str.append(f"{key}: ->{rel_type} {props}")
                    else:
                        row_str.append(f"{key}: {value}")
                else:
                    row_str.append(f"{key}: {value}")
            formatted_result.append(" | ".join(row_str))
        return "\n".join(formatted_result)

   
        """Return the node labels, relationship types, and node property structure of the graph database."""
        try:
            node_labels = self.neo4j_graph.query("""
                CALL db.labels()
                YIELD label
                RETURN collect(label) AS labels
            """)[0]["labels"]

            rel_types = self.neo4j_graph.query("""
                CALL db.relationshipTypes()
                YIELD relationshipType
                RETURN collect(relationshipType) AS types
            """)[0]["types"]

            node_props = self.neo4j_graph.query("""
                CALL apoc.meta.schema()
                YIELD value
                RETURN value
            """)[0]["value"]

            lines = [
                "Graph Database Schema",
                f" Node Labels: {', '.join(node_labels)}",
                f" Relationship Types: {', '.join(rel_types)}",
                f" Node Properties:"
            ]

            for label, props in node_props.items():
                lines.append(f"  ▶ {label}:")
                for prop, meta in props["properties"].items():
                    lines.append(f"    - {prop}: {meta.get('type', 'unknown')}")

            return "\n".join(lines)

        except Exception as e:
            return f"❌ Failed to get database schema: {str(e)}"
