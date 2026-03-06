from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
load_dotenv()


class Neo4jReader:
    def __init__(self):
        self.driver = GraphDatabase.driver((os.getenv("NEO4J_URI")), auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")))


    def close(self):
        self.driver.close()

    def fetch_relations(self, node_name: str):
        query = """
        MATCH (n:Entity {name: $name})-[r:RELATION*1..4]-(m:Entity)
        UNWIND r AS rel
        RETURN DISTINCT
            startNode(rel).name AS source,
            rel.type AS relation,
            endNode(rel).name AS target;

        """
        with self.driver.session() as session:
            result = session.run(query, name=node_name)
            return [record.data() for record in result]
