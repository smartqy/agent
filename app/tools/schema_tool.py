from typing import Type
from pydantic import BaseModel
from langchain_core.tools import BaseTool
from langchain_community.graphs import Neo4jGraph
from pydantic import Field


class SchemaInput(BaseModel):
    query: str = Field(default="", description="可选的提示输入，当前不使用")


class SchemaTool(BaseTool):
    name: str = "schema_tool"
    description: str = "展示图数据库结构，包括节点标签、关系类型和属性。"
    args_schema: Type[BaseModel] = SchemaInput  # ✅ 添加类型注解
    neo4j_graph: Neo4jGraph = Field(..., description="Neo4j 图数据库实例")

    def _run(self, query: str) -> str:
        try:
            node_labels = self.neo4j_graph.query("CALL db.labels() YIELD label RETURN collect(label) AS labels")[0]["labels"]
            rel_types = self.neo4j_graph.query("CALL db.relationshipTypes() YIELD relationshipType RETURN collect(relationshipType) AS types")[0]["types"]
            node_props = self.neo4j_graph.query("CALL apoc.meta.schema() YIELD value RETURN value")[0]["value"]

            lines = [
                "📦 图数据库结构：",
                f"🏷️ 节点标签: {', '.join(node_labels)}",
                f"🔗 关系类型: {', '.join(rel_types)}",
                "🔍 节点属性："
            ]
            for label, props in node_props.items():
                lines.append(f"  ▶ {label}:")
                for prop, meta in props.get("properties", {}).items():
                    lines.append(f"    - {prop}: {meta.get('type', 'unknown')}")
            return "\n".join(lines)
        except Exception as e:
            return f"❌ 获取结构失败: {str(e)}"

    async def _arun(self, query: str) -> str:
        return self._run(query)
