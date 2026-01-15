import os
import time
import logging
from typing import Optional
from cerebras.cloud.sdk import Cerebras
from dotenv import load_dotenv

from nl2sql.cache import get_cache
from nl2sql.rate_limiter import get_rate_limiter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure Cerebras API
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
if not CEREBRAS_API_KEY:
    logger.error("CEREBRAS_API_KEY not found in environment variables")
    raise ValueError("CEREBRAS_API_KEY not found in environment variables")

# Initialize Cerebras Client
client = Cerebras(api_key=CEREBRAS_API_KEY)

# Initialize Cerebras model
model_name = os.getenv("CEREBRAS_MODEL", "llama-3.3-70b")
logger.info(f"Initializing Cerebras model: {model_name}")

# Initialize cache and rate limiter
CACHE_TTL = int(os.getenv("CACHE_TTL_SECONDS", "3600"))  # 1 hour default
RPM_LIMIT = int(os.getenv("CEREBRAS_RPM_LIMIT", "60"))   # 60 requests/min default
RPD_LIMIT = int(os.getenv("CEREBRAS_RPD_LIMIT", "10000"))  # 10000 requests/day default

cache = get_cache(ttl=CACHE_TTL)
rate_limiter = get_rate_limiter(rpm=RPM_LIMIT, rpd=RPD_LIMIT)

logger.info(f"Cache TTL: {CACHE_TTL}s, Rate limits: {RPM_LIMIT} RPM, {RPD_LIMIT} RPD")

def call_llm(prompt: str, max_retries: int = 3, temperature: float = 0.1) -> str:
    """
    Call Cerebras API with retry logic, caching, and rate limiting.
    
    Args:
        prompt: The prompt to send to the LLM
        max_retries: Maximum number of retry attempts
        temperature: Temperature for response generation
        
    Returns:
        The generated text response
    """
    logger.info(f"Calling Cerebras API with prompt length: {len(prompt)}")
    
    # Check cache first
    cached_response = cache.get(prompt)
    if cached_response:
        logger.info("Returning cached response")
        return cached_response
    
    # Apply rate limiting - uses blocking=True to wait gracefully for tokens
    if not rate_limiter.acquire(blocking=True, timeout=60):
        wait_time = rate_limiter.get_wait_time()
        error_msg = (
            f"Rate limit exceeded (timeout). Please wait {wait_time:.0f} seconds. "
            f"Limits: {RPM_LIMIT} requests/min, {RPD_LIMIT} requests/day"
        )
        logger.error(error_msg)
        raise Exception(error_msg)
    
    for attempt in range(max_retries):
        try:
            logger.debug(f"Attempt {attempt + 1}/{max_retries}")
            
            # Call Cerebras API using chat completions format
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=temperature,
                max_completion_tokens=2048,
            )
            
            # Extract text from response
            if response.choices and len(response.choices) > 0:
                result = response.choices[0].message.content.strip()
                logger.info("Successfully received response from Cerebras")
                
                # Cache the successful response
                cache.set(prompt, result)
                
                # Log cache stats periodically
                if (cache.get_stats()["hits"] + cache.get_stats()["misses"]) % 10 == 0:
                    logger.info(f"Cache stats: {cache.get_stats()}")
                
                return result
            else:
                logger.warning("Empty response from Cerebras API")
                raise ValueError("Empty response from Cerebras API")
                
        except Exception as e:
            error_str = str(e)
            
            # Check if it's a quota/rate limit error
            if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
                logger.error(f"Cerebras API quota exceeded: {error_str}")
                raise Exception(
                    f"Cerebras API quota exceeded. This shouldn't happen with rate limiting enabled. "
                    f"Error: {error_str}"
                )
            
            logger.error(f"Error calling Cerebras API (Attempt {attempt + 1}): {error_str}")
            if attempt < max_retries - 1:
                # Use exponential backoff
                wait_time = 5 * (2 ** attempt)
                logger.info(f"Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logger.error(f"Failed after {max_retries} attempts")
                raise Exception(f"Failed to call Cerebras API after {max_retries} attempts: {e}")
    
    return ""

def call_llm_with_system(system_prompt: str, user_prompt: str, temperature: float = 0.1) -> str:
    """
    Call Cerebras API with separate system and user prompts.
    
    Args:
        system_prompt: System-level instructions
        user_prompt: User's actual prompt
        temperature: Temperature for response generation
        
    Returns:
        The generated text response
    """
    logger.info(f"Calling Cerebras API with system prompt length: {len(system_prompt)}, user prompt length: {len(user_prompt)}")
    
    # Create cache key from both prompts
    cache_key = f"{system_prompt}\n\n{user_prompt}"
    
    # Check cache first
    cached_response = cache.get(cache_key)
    if cached_response:
        logger.info("Returning cached response")
        return cached_response
    
    # Apply rate limiting
    if not rate_limiter.acquire(blocking=True, timeout=60):
        wait_time = rate_limiter.get_wait_time()
        error_msg = (
            f"Rate limit exceeded (timeout). Please wait {wait_time:.0f} seconds. "
            f"Limits: {RPM_LIMIT} requests/min, {RPD_LIMIT} requests/day"
        )
        logger.error(error_msg)
        raise Exception(error_msg)
    
    try:
        # Call Cerebras API with system and user messages
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            temperature=temperature,
            max_completion_tokens=2048,
        )
        
        # Extract text from response
        if response.choices and len(response.choices) > 0:
            result = response.choices[0].message.content.strip()
            logger.info("Successfully received response from Cerebras")
            
            # Cache the successful response
            cache.set(cache_key, result)
            
            return result
        else:
            logger.warning("Empty response from Cerebras API")
            raise ValueError("Empty response from Cerebras API")
            
    except Exception as e:
        logger.error(f"Error calling Cerebras API with system prompt: {str(e)}")
        raise Exception(f"Failed to call Cerebras API: {e}")

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
