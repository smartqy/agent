from typing import Any, Dict, List
from langchain_community.graphs import Neo4jGraph
from langchain_core.tools import BaseTool
from pydantic import Field

class GraphQueryTool(BaseTool):
    name: str = "graph_query"
    description: str = (
        "用于查询 Neo4j 图数据库中的营销活动数据。"
        "输入应为 Cypher 查询语句（不带反引号），如：MATCH (n) RETURN n LIMIT 10。"
        "适用于查询节点、关系、属性，或执行聚合分析。"
    )

    neo4j_graph: Neo4jGraph = Field(..., description="连接到的 Neo4j 图数据库实例")

    def _run(self, query: str) -> str:
        try:
            result = self.neo4j_graph.query(query)
            return self._format_output(result)
        except Exception as e:
            return f"查询执行失败: {str(e)}"

    async def _arun(self, query: str) -> str:
        return self._run(query)

    def _format_output(self, result: List[Dict[str, Any]]) -> str:
        if not result:
            return "查询未返回任何结果。"

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

    def get_schema(self) -> str:
        """返回图数据库的节点标签、关系类型及节点属性结构。"""
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
                "📦 图数据库结构",
                f"🏷️ 节点标签：{', '.join(node_labels)}",
                f"🔗 关系类型：{', '.join(rel_types)}",
                f"🔍 节点属性："
            ]

            for label, props in node_props.items():
                lines.append(f"  ▶ {label}:")
                for prop, meta in props["properties"].items():
                    lines.append(f"    - {prop}: {meta.get('type', 'unknown')}")

            return "\n".join(lines)

        except Exception as e:
            return f"❌ 获取数据库结构失败: {str(e)}"
