from dotenv import load_dotenv
from pathlib import Path
from langchain_community.graphs import Neo4jGraph
import os
import json


class BaseLogger:
    def __init__(self) -> None:
        self.info = print


def load_graph():
    """
    Function to load the graph client
    """
    # Environment set up
    root_dir = Path(__file__).parent.parent

    env_path = root_dir / "config" / ".env_loader"
    load_dotenv(dotenv_path=env_path)

    url = os.getenv("NEO4J_URI")
    username = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")

    print("Loaded config:", url, username, password) 

    # if Neo4j is local, you can go to http://localhost:7474/ to browse the database
    neo4j_graph = Neo4jGraph(url=url, 
                             username=username, 
                             password=password) 
    
    return neo4j_graph


def load_data() -> dict:
    '''
    Function to load in the dummy data
    '''
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, "../data/dummy_graph_data.json")
    with open(file_path) as data:
        data_json = json.load(data)
    return data_json


def insert_data(data: dict, neo4j_graph) -> None:
    '''
    Function to upload the dummy data to Neo4J
    '''
    # Define query bases
    node_query_base = """
    MERGE (n:{type} {{
        id: $id,
    """
    relationship_query_base = """
    MATCH (a {{id: $from}}), (b {{id: $to}})
    MERGE (a)-[r:{type}]->(b)
    ON CREATE SET """

    # Loop through the data to insert
    for node in data['nodes']:
        # Reset the query
        node_query = node_query_base

        # Format the query and add the properties individually
        properties = node.get("properties", {})

        for k, v in properties.items():
            node_query += f"{k}: '{v}',\n"

        node_query = node_query[:-2] + "}})"

        # Format the query and execute
        node_query_fmt = node_query.format(type=node['label']) 

        neo4j_graph.query(node_query_fmt, params={'id':node['id']})


    print("--- All Nodes Inserted ---")
    

    for relationship in data['relationships']:
        # Reset the query
        relationship_query = relationship_query_base

        properties = relationship.get("properties", None)

        if properties:
            for k, v in properties.items():
                relationship_query += f"r.{k} = '{v}', "

            relationship_query = relationship_query[:-2] 

            # Format the query and execute
            relationship_query_fmt = relationship_query.format(type=relationship['label'])

        else:
            relationship_query_fmt = relationship_query.format(type=relationship['label']).strip('ON CREATE SET ')

        neo4j_graph.query(relationship_query_fmt, 
                          params={'from':relationship['from'], 'to':relationship['to']})
        

    print("--- All Relationships Inserted ---")

    return True



