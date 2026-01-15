import os
import time
import logging
from typing import Optional
import google.generativeai as genai
from dotenv import load_dotenv

from nl2sql.cache import get_cache
from nl2sql.rate_limiter import get_rate_limiter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY not found in environment variables")
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini model
model_name = 'gemini-1.5-flash-latest'
logger.info(f"Initializing Gemini model: {model_name}")
model = genai.GenerativeModel(model_name)

# Initialize cache and rate limiter
CACHE_TTL = int(os.getenv("CACHE_TTL_SECONDS", "3600"))  # 1 hour default
RPM_LIMIT = int(os.getenv("GEMINI_RPM_LIMIT", "10"))     # 10 requests/min
RPD_LIMIT = int(os.getenv("GEMINI_RPD_LIMIT", "1500"))   # 1500 requests/day

cache = get_cache(ttl=CACHE_TTL)
rate_limiter = get_rate_limiter(rpm=RPM_LIMIT, rpd=RPD_LIMIT)

logger.info(f"Cache TTL: {CACHE_TTL}s, Rate limits: {RPM_LIMIT} RPM, {RPD_LIMIT} RPD")

def call_llm(prompt: str, max_retries: int = 3, temperature: float = 0.1) -> str:
    """
    Call Gemini API with retry logic, caching, and rate limiting.
    """
    logger.info(f"Calling Gemini API with prompt length: {len(prompt)}")
    
    # Check cache first
    cached_response = cache.get(prompt)
    if cached_response:
        logger.info("Returning cached response")
        return cached_response
    
    # Apply rate limiting
    if not rate_limiter.acquire():
        wait_time = rate_limiter.get_wait_time()
        error_msg = (
            f"Rate limit exceeded. Please wait {wait_time:.0f} seconds. "
            f"Limits: {RPM_LIMIT} requests/min, {RPD_LIMIT} requests/day"
        )
        logger.error(error_msg)
        raise Exception(error_msg)
    
    for attempt in range(max_retries):
        try:
            # Configure generation parameters
            generation_config = genai.GenerationConfig(
                temperature=temperature,
                top_p=0.95,
                top_k=40,
                max_output_tokens=2048,
            )
            
            logger.debug(f"Attempt {attempt + 1}/{max_retries}")
            
            # Generate response
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Extract text from response
            if response.text:
                logger.info("Successfully received response from Gemini")
                result = response.text.strip()
                
                # Cache the successful response
                cache.set(prompt, result)
                
                # Log cache stats periodically
                if cache.get_stats()["hits"] + cache.get_stats()["misses"] % 10 == 0:
                    logger.info(f"Cache stats: {cache.get_stats()}")
                
                return result
            else:
                logger.warning("Empty response from Gemini API")
                raise ValueError("Empty response from Gemini API")
                
        except Exception as e:
            error_str = str(e)
            
            # Check if it's a quota/rate limit error from Gemini
            if "429" in error_str or "quota" in error_str.lower():
                logger.error(f"Gemini API quota exceeded: {error_str}")
                raise Exception(
                    f"Gemini API quota exceeded. This shouldn't happen with rate limiting enabled. "
                    f"Error: {error_str}"
                )
            
            logger.error(f"Error calling Gemini API (Attempt {attempt + 1}): {error_str}")
            if attempt < max_retries - 1:
                # Use larger backoff for rate limits: 5s, 10s, 20s
                wait_time = 5 * (2 ** attempt)
                logger.info(f"Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logger.error(f"Failed after {max_retries} attempts")
                raise Exception(f"Failed to call Gemini API after {max_retries} attempts: {e}")
    
    return ""

def call_llm_with_system(system_prompt: str, user_prompt: str, temperature: float = 0.1) -> str:
    """
    Call Gemini API with separate system and user prompts.
    
    Args:
        system_prompt: System instructions
        user_prompt: User query
        temperature: Generation temperature
    
    Returns:
        Generated text response
    """
    combined_prompt = f"{system_prompt}\n\n{user_prompt}"
    return call_llm(combined_prompt, temperature=temperature)

def get_cache_stats() -> dict:
    """Get cache statistics."""
    return cache.get_stats()

def get_rate_limit_stats() -> dict:
    """Get rate limiter statistics."""
    return rate_limiter.get_stats()

def clear_cache() -> None:
    """Clear the cache."""
    cache.clear()
    logger.info("Cache cleared manually")

