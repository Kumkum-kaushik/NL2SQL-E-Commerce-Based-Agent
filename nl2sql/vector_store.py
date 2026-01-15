import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict
from pathlib import Path

class VectorStore:
    """FAISS-based vector store for few-shot example retrieval."""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize vector store with sentence transformer model.
        
        Args:
            model_name: Name of the sentence transformer model
        """
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.examples = []
        self.dimension = 384  # Dimension for all-MiniLM-L6-v2
        
    def add_examples(self, examples: List[Dict[str, str]]):
        """
        Add few-shot examples to the vector store.
        
        Args:
            examples: List of dicts with 'question' and 'sql' keys
        """
        self.examples = examples
        
        # Generate embeddings for questions
        questions = [ex['question'] for ex in examples]
        embeddings = self.model.encode(questions, convert_to_numpy=True)
        
        # Create FAISS index
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(embeddings.astype('float32'))
        
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, str]]:
        """
        Retrieve top-k most similar examples for a query.
        
        Args:
            query: Natural language question
            top_k: Number of examples to retrieve
        
        Returns:
            List of most similar examples
        """
        if self.index is None or len(self.examples) == 0:
            return []
        
        # Generate embedding for query
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        
        # Search for similar examples
        k = min(top_k, len(self.examples))
        distances, indices = self.index.search(query_embedding.astype('float32'), k)
        
        # Return top-k examples
        return [self.examples[i] for i in indices[0]]
    
    def save(self, filepath: str):
        """Save vector store to disk."""
        if self.index is None:
            raise ValueError("No index to save")
        
        # Save FAISS index
        faiss.write_index(self.index, f"{filepath}.index")
        
        # Save examples
        with open(f"{filepath}.json", 'w') as f:
            json.dump(self.examples, f, indent=2)
    
    def load(self, filepath: str):
        """Load vector store from disk."""
        # Load FAISS index
        self.index = faiss.read_index(f"{filepath}.index")
        
        # Load examples
        with open(f"{filepath}.json", 'r') as f:
            self.examples = json.load(f)

def create_vector_store_from_file(filepath: str) -> VectorStore:
    """
    Create and populate vector store from JSON file.
    
    Args:
        filepath: Path to JSON file with examples
    
    Returns:
        Initialized VectorStore
    """
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Extract examples
    if isinstance(data, list):
        examples = data
    elif 'examples' in data:
        examples = data['examples']
    else:
        raise ValueError("Invalid JSON format. Expected list or dict with 'examples' key")
    
    # Create and populate vector store
    store = VectorStore()
    store.add_examples(examples)
    
    return store
