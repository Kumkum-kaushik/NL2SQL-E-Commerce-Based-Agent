from nl2sql.vector_store import create_vector_store_from_file
from pathlib import Path

class FewShotStore:
    """Store for managing few-shot examples with semantic search."""
    
    def __init__(self, examples_file: str):
        """
        Initialize few-shot store from JSON file.
        
        Args:
            examples_file: Path to JSON file with examples
        """
        self.examples_file = examples_file
        self.vector_store = None
        
        # Load examples if file exists
        if Path(examples_file).exists():
            try:
                self.vector_store = create_vector_store_from_file(examples_file)
            except Exception as e:
                print(f"Warning: Could not load examples from {examples_file}: {e}")
    
    def retrieve(self, question: str, top_k: int = 5):
        """
        Retrieve top-k most similar examples using semantic search.
        
        Args:
            question: Natural language question
            top_k: Number of examples to retrieve
        
        Returns:
            List of most similar examples
        """
        if self.vector_store is None:
            return []
        
        return self.vector_store.retrieve(question, top_k)
