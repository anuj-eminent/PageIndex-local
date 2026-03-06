from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

class Neo4jKG:
    # Set clear_on_connect=True to clear out the database on initialization (simulating a fresh database)
    def __init__(self, clear_on_connect=True):
        self.driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI"), 
            auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
        )
        if clear_on_connect:
            self.clear_database()

    def clear_database(self):
        """Clears all nodes and relationships to start fresh."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("Neo4j database cleared successfully.")

    def close(self):
        self.driver.close()

    def insert_triple(self, subject, relation, obj):
        query = """
        MERGE (s:Entity {name: $subject})
        MERGE (o:Entity {name: $object})
        MERGE (s)-[r:RELATION {type: $relation}]->(o)
        """
        with self.driver.session() as session:
            session.run(
                query,
                subject=subject,
                object=obj,
                relation=relation
            )
