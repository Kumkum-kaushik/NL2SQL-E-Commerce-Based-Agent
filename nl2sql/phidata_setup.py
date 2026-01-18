"""
Phidata Setup Module
Initializes Gemini LLM, GeminiEmbedder, and Pinecone Vector Database
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from phi.model.google import Gemini
from phi.embedder.google import GeminiEmbedder
from phi.vectordb.pineconedb import PineconeDB
from phi.knowledge.text import TextKnowledgeBase
import json

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if os.getenv("PHI_DEBUG", "false").lower() == "true" else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
logger.info("Environment variables loaded")

# Verify required API keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

if not GOOGLE_API_KEY:
    logger.error("GOOGLE_API_KEY not found in environment variables")
    raise ValueError("GOOGLE_API_KEY is required")
logger.info(f"Google API Key loaded: {GOOGLE_API_KEY[:10]}...")

if not PINECONE_API_KEY:
    logger.error("PINECONE_API_KEY not found in environment variables")
    raise ValueError("PINECONE_API_KEY is required")
logger.info(f"Pinecone API Key loaded: {PINECONE_API_KEY[:10]}...")

# Gemini Model Configuration
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "models/text-embedding-004")

logger.info(f"Initializing Gemini model: {GEMINI_MODEL}")
gemini_model = Gemini(
    id=GEMINI_MODEL,
)
logger.info("Gemini model initialized successfully")

# Gemini Embedder Configuration
logger.info(f"Initializing GeminiEmbedder with model: {GEMINI_EMBEDDING_MODEL}")
gemini_embedder = GeminiEmbedder(
    model=GEMINI_EMBEDDING_MODEL,
)
logger.info("GeminiEmbedder initialized successfully")

# Pinecone Configuration
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "nl2sql-examples")
PINECONE_DIMENSION = int(os.getenv("PINECONE_DIMENSION", "768"))
PINECONE_CLOUD = os.getenv("PINECONE_CLOUD", "aws")
PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1")

logger.info(f"Initializing Pinecone DB: index={PINECONE_INDEX_NAME}, dimension={PINECONE_DIMENSION}")
pinecone_db = PineconeDB(
    name=PINECONE_INDEX_NAME,
    dimension=PINECONE_DIMENSION,
    metric="cosine",
    api_key=PINECONE_API_KEY,
    spec={
        "serverless": {
            "cloud": PINECONE_CLOUD,
            "region": PINECONE_REGION,
        }
    },
    embedder=gemini_embedder,
    use_hybrid_search=False,
)
logger.info("Pinecone DB initialized successfully")

# Knowledge Base Setup
def create_knowledge_base_from_examples(examples_file: str = None) -> TextKnowledgeBase:
    """
    Create a Pinecone knowledge base from few-shot examples.
    
    Args:
        examples_file: Path to JSON file with examples (default: tests/test_queries.json)
    
    Returns:
        TextKnowledgeBase instance
    """
    if examples_file is None:
        examples_file = Path(__file__).parent.parent / "tests" / "test_queries.json"
    
    logger.info(f"Loading examples from: {examples_file}")
    
    if not Path(examples_file).exists():
        logger.warning(f"Examples file not found: {examples_file}")
        return None
    
    try:
        with open(examples_file, 'r') as f:
            examples = json.load(f)
        
        logger.info(f"Loaded {len(examples)} examples")
        
        # Format examples as text for knowledge base
        texts = []
        for i, example in enumerate(examples):
            text = f"Question: {example['question']}\nSQL: {example['sql']}"
            texts.append(text)
            logger.debug(f"Example {i+1}: {example['question'][:50]}...")
        
        logger.info(f"Creating knowledge base with {len(texts)} text entries")
        knowledge_base = TextKnowledgeBase(
            texts=texts,
            vector_db=pinecone_db,
        )
        
        logger.info("Loading knowledge base into Pinecone (this may take a moment)...")
        knowledge_base.load(upsert=True)
        logger.info("Knowledge base loaded successfully")
        
        return knowledge_base
        
    except Exception as e:
        logger.error(f"Error creating knowledge base: {str(e)}", exc_info=True)
        raise

# Initialize knowledge base (lazy loading)
_knowledge_base = None

def get_knowledge_base() -> TextKnowledgeBase:
    """Get or create the knowledge base singleton."""
    global _knowledge_base
    if _knowledge_base is None:
        logger.info("Initializing knowledge base for the first time")
        _knowledge_base = create_knowledge_base_from_examples()
    return _knowledge_base

# Export configured instances
__all__ = [
    'gemini_model',
    'gemini_embedder',
    'pinecone_db',
    'get_knowledge_base',
    'create_knowledge_base_from_examples'
]

logger.info("Phidata setup module loaded successfully")
