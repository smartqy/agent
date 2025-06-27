from typing import Type
from pydantic import BaseModel
from langchain_core.tools import BaseTool
from langchain_community.graphs import Neo4jGraph
from pydantic import Field


class SchemaInput(BaseModel):
    query: str = Field(default="", description="Optional prompt input, currently unused")


class SchemaTool(BaseTool):
    name: str = "schema_tool"
    description: str = ("Use this tool to display the structure of the graph database, including node labels, "
        "relationship types, and the properties of each node. "
        "This is useful when the user asks about the data model, what types of nodes exist, "
        "or what properties are available."
    )
    args_schema: Type[BaseModel] = SchemaInput  # Add type annotation
    neo4j_graph: Neo4jGraph = Field(..., description="Neo4j graph database instance")

    def _run(self, query: str) -> str:
        try:
            node_labels = self.neo4j_graph.query("CALL db.labels() YIELD label RETURN collect(label) AS labels")[0]["labels"]
            rel_types = self.neo4j_graph.query("CALL db.relationshipTypes() YIELD relationshipType RETURN collect(relationshipType) AS types")[0]["types"]
            node_props = self.neo4j_graph.query("CALL apoc.meta.schema() YIELD value RETURN value")[0]["value"]

            lines = [
                "📦 Graph Database Schema:",
                f"🏷️ Node Labels: {', '.join(node_labels)}",
                f"🔗 Relationship Types: {', '.join(rel_types)}",
                "🔍 Node Properties:"
            ]
            for label, props in node_props.items():
                lines.append(f"  ▶ {label}:")
                for prop, meta in props.get("properties", {}).items():
                    lines.append(f"    - {prop}: {meta.get('type', 'unknown')}")
            return "\n".join(lines)
        except Exception as e:
            return f"❌ Failed to get schema: {str(e)}"

    async def _arun(self, query: str) -> str:
        return self._run(query)
