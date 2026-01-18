"""
Phidata Setup Module
Initializes Gemini LLM, GeminiEmbedder, and Pinecone Vector Database with Rate Limiting
"""
import os
import logging
import time
from pathlib import Path
from dotenv import load_dotenv
from phi.model.google import Gemini
from phi.embedder.google import GeminiEmbedder
from phi.vectordb.pineconedb import PineconeDB
from phi.knowledge.text import TextKnowledgeBase
from pinecone import ServerlessSpec
import json
from nl2sql.rate_limiter import get_rate_limiter

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

# Rate Limiting Configuration for Gemini
GEMINI_RPM_LIMIT = int(os.getenv("GEMINI_RPM_LIMIT", 4))  # Free tier: 5 requests/min (using 4 for safety)
GEMINI_RPD_LIMIT = int(os.getenv("GEMINI_RPD_LIMIT", 100))  # Conservative daily limit

# Initialize rate limiter for Gemini API
gemini_rate_limiter = get_rate_limiter(rpm=GEMINI_RPM_LIMIT, rpd=GEMINI_RPD_LIMIT)
logger.info(f"Gemini rate limiter initialized: {GEMINI_RPM_LIMIT} RPM, {GEMINI_RPD_LIMIT} RPD")

class RateLimitedGemini(Gemini):
    """Gemini model wrapper with rate limiting and retry logic"""
    
    def response(self, messages, **kwargs):
        """Generate response with rate limiting and retry logic"""
        max_retries = 3
        base_delay = 1
        
        for attempt in range(max_retries):
            try:
                # Check rate limiter before making request
                if not gemini_rate_limiter.acquire(blocking=True, timeout=60):
                    wait_time = gemini_rate_limiter.get_wait_time()
                    logger.warning(f"Rate limit exceeded, waiting {wait_time:.1f}s")
                    time.sleep(wait_time + 1)  # Add 1s buffer
                    
                # Make the API call
                logger.debug(f"Making Gemini API call (attempt {attempt + 1}/{max_retries})")
                return super().response(messages, **kwargs)
                
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                    # Extract retry delay from error message if available
                    retry_delay = base_delay * (2 ** attempt)  # Exponential backoff
                    
                    # Try to parse retry delay from Google's error message
                    if "retry in" in error_str:
                        try:
                            import re
                            match = re.search(r'retry in ([\d.]+)s', error_str)
                            if match:
                                retry_delay = float(match.group(1)) + 1  # Add 1s buffer
                        except:
                            pass
                    
                    if attempt < max_retries - 1:
                        logger.warning(f"Rate limit hit, retrying in {retry_delay:.1f}s (attempt {attempt + 1}/{max_retries})")
                        time.sleep(retry_delay)
                        continue
                    else:
                        logger.error(f"Rate limit exceeded after {max_retries} attempts")
                        raise
                else:
                    # Non-rate-limit error, re-raise immediately
                    raise

# Gemini Model Configuration
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "models/text-embedding-004")

logger.info(f"Initializing Gemini model with rate limiting: {GEMINI_MODEL}")
gemini_model = RateLimitedGemini(
    id=GEMINI_MODEL,
)
logger.info("Rate-limited Gemini model initialized successfully")

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
    spec=ServerlessSpec(
        cloud=PINECONE_CLOUD,
        region=PINECONE_REGION
    ),
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
        # Create a temporary path for the knowledge base
        kb_path = Path("temp_knowledge_base")
        knowledge_base = TextKnowledgeBase(
            path=kb_path,
            texts=texts,
            vector_db=pinecone_db,
        )
        
        logger.info("Loading knowledge base into Pinecone (this may take a moment)...")
        try:
            knowledge_base.load(upsert=True)
            logger.info("Knowledge base loaded successfully into Pinecone")
        except Exception as pinecone_error:
            logger.warning(f"Pinecone setup failed: {str(pinecone_error)}")
            logger.info("Falling back to local knowledge base without vector database...")
            
            # Create fallback knowledge base without vector database
            knowledge_base = TextKnowledgeBase(
                path=kb_path,
                texts=texts,
            )
            knowledge_base.load(upsert=True)
            logger.info("Local knowledge base loaded successfully")
        
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
    'create_knowledge_base_from_examples',
    'gemini_rate_limiter'  # Export rate limiter for monitoring
]

def get_rate_limiter_stats():
    """Get current rate limiter statistics"""
    return gemini_rate_limiter.get_stats()

logger.info("Phidata setup module loaded successfully with rate limiting enabled")
