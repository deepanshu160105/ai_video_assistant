"""
Retry helper for Mistral rate-limit errors (HTTP 429).
Uses exponential backoff: waits 10s, 20s, 40s ... between retries.
"""
import time
import functools


def with_retry(func, max_retries: int = 5, base_wait: int = 10):
    """
    Call `func()` and retry on rate-limit (429) errors with exponential backoff.
    Usage:
        result = with_retry(lambda: chain.invoke(input))
    """
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            err = str(e)
            if "429" in err or "rate_limit" in err.lower() or "rate limit" in err.lower():
                wait = base_wait * (2 ** attempt)   # 10, 20, 40, 80, 160 seconds
                print(f"⏳ Rate limited. Waiting {wait}s before retry {attempt+1}/{max_retries}...")
                time.sleep(wait)
            else:
                raise  # not a rate-limit error — re-raise immediately
    raise RuntimeError(f"Failed after {max_retries} retries due to rate limiting.")
