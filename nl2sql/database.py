import os
import networkx as nx
from typing import Dict, List, Any, Optional
from sqlalchemy import create_engine, inspect, text
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    def __init__(self, db_url: Optional[str] = None):
        self.db_url = db_url or os.getenv("DATABASE_URL", "sqlite:///./ecommerce.db")
        self.engine = create_engine(self.db_url)
        self.inspector = inspect(self.engine)
        self.graph = None

    def get_connection(self):
        """Get a raw connection from SQLAlchemy engine."""
        return self.engine.connect()

    def get_schema_info(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get schema information for all tables."""
        schema_info = {}
        for table_name in self.inspector.get_table_names():
            columns = self.inspector.get_columns(table_name)
            pk_columns = self.inspector.get_pk_constraint(table_name).get('constrained_columns', [])
            
            schema_info[table_name] = [
                {
                    "name": col['name'],
                    "type": str(col['type']),
                    "nullable": col['nullable'],
                    "pk": col['name'] in pk_columns
                }
                for col in columns
            ]
        return schema_info

    def build_schema_graph(self):
        """
        Build a NetworkX graph where:
        - Nodes are Table Names
        - Edges are Foreign Key relationships
        """
        G = nx.MultiDiGraph()
        
        # Add all tables as nodes
        for table_name in self.inspector.get_table_names():
            columns = self.inspector.get_columns(table_name)
            G.add_node(table_name, columns=[c['name'] for c in columns])
            
            # Get foreign keys
            fks = self.inspector.get_foreign_keys(table_name)
            for fk in fks:
                referred_table = fk['referred_table']
                for constrained_col, referred_col in zip(fk['constrained_columns'], fk['referred_columns']):
                    G.add_edge(table_name, referred_table, 
                              constrained_column=constrained_col,
                              referred_column=referred_col,
                              label=f"{table_name}.{constrained_col} -> {referred_table}.{referred_col}")
        
        self.graph = G
        return G

    def get_relevant_schema_subgraph(self, relevant_tables: List[str]) -> str:
        """
        Given a list of relevant tables, find the paths between them in the graph
        and return a descriptive schema string for LLM.
        """
        if not self.graph:
            self.build_schema_graph()
            
        if not relevant_tables:
            return ""

        # Find all nodes in the Steiner Tree or simple connections
        all_nodes = set(relevant_tables)
        
        # Simplistic approach: find shortest paths between all pairs of relevant tables
        import itertools
        for t1, t2 in itertools.combinations(relevant_tables, 2):
            try:
                # Undirected for finding paths
                undirected_G = self.graph.to_undirected()
                path = nx.shortest_path(undirected_G, t1, t2)
                all_nodes.update(path)
            except (nx.NetworkXNoPath, nx.NodeNotFound):
                continue
        
        # Construct schema prompt part
        schema_str = "Relevant Schema Context (Graph-based):\n"
        full_schema = self.get_schema_info()
        
        for table in all_nodes:
            if table in full_schema:
                schema_str += f"\nTable: {table}\n"
                for col in full_schema[table]:
                    schema_str += f"  - {col['name']} ({col['type']}){ ' [PK]' if col['pk'] else ''}\n"
        
        # Add Relationship info
        schema_str += "\nRelationships:\n"
        for u, v, data in self.graph.edges(data=True):
            if u in all_nodes and v in all_nodes:
                schema_str += f"- {data['label']}\n"
                
        return schema_str

# Singleton instance for general use
db_manager = DatabaseManager()

if __name__ == "__main__":
    # Test Graph Building
    print("Building schema graph...")
    g = db_manager.build_schema_graph()
    print(f"Nodes: {g.nodes()}")
    print(f"Edges: {list(g.edges(data=True))[:2]}") # Print first 2 edges
