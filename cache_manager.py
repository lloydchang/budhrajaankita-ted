"""
Simple file-based caching system for API responses
Reduces OpenRouter API calls and helps with rate limiting
"""
import json
import hashlib
import os
from datetime import datetime, timedelta
from pathlib import Path
import time

class ResponseCache:
    def __init__(self, cache_dir=".cache", ttl_hours=24):
        """
        Initialize the cache system
        
        Args:
            cache_dir: Directory to store cache files
            ttl_hours: Time-to-live for cached responses in hours
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
        
    def _get_cache_key(self, endpoint: str, data: dict) -> str:
        """Generate a unique cache key based on endpoint and request data"""
        # Create a stable string representation of the data
        data_str = json.dumps(data, sort_keys=True)
        # Combine endpoint and data, then hash
        key_str = f"{endpoint}:{data_str}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get the file path for a cache key"""
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, endpoint: str, data: dict):
        """
        Retrieve cached response if available and not expired
        
        Args:
            endpoint: API endpoint name
            data: Request data
            
        Returns:
            Cached response or None if not found/expired
        """
        cache_key = self._get_cache_key(endpoint, data)
        cache_path = self._get_cache_path(cache_key)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r') as f:
                cached = json.load(f)
            
            # Check if cache is expired
            cached_time = datetime.fromisoformat(cached['timestamp'])
            if datetime.now() - cached_time > self.ttl:
                # Cache expired, delete it
                cache_path.unlink()
                return None
            
            print(f"✅ Cache HIT for {endpoint} (age: {datetime.now() - cached_time})")
            return cached['response']
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"⚠️ Cache read error: {e}")
            # Delete corrupted cache file
            cache_path.unlink(missing_ok=True)
            return None
    
    def set(self, endpoint: str, data: dict, response):
        """
        Store response in cache
        
        Args:
            endpoint: API endpoint name
            data: Request data
            response: Response to cache
        """
        cache_key = self._get_cache_key(endpoint, data)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            cached_data = {
                'timestamp': datetime.now().isoformat(),
                'endpoint': endpoint,
                'response': response
            }
            
            with open(cache_path, 'w') as f:
                json.dump(cached_data, f, indent=2)
            
            print(f"💾 Cached response for {endpoint}")
            
        except Exception as e:
            print(f"⚠️ Cache write error: {e}")
    
    def clear_expired(self):
        """Remove all expired cache entries"""
        removed = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r') as f:
                    cached = json.load(f)
                
                cached_time = datetime.fromisoformat(cached['timestamp'])
                if datetime.now() - cached_time > self.ttl:
                    cache_file.unlink()
                    removed += 1
                    
            except Exception:
                # Remove corrupted files
                cache_file.unlink(missing_ok=True)
                removed += 1
        
        if removed > 0:
            print(f"🗑️ Removed {removed} expired cache entries")
        
        return removed
    
    def clear_all(self):
        """Remove all cache entries"""
        removed = 0
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
            removed += 1
        
        print(f"🗑️ Cleared all cache ({removed} entries)")
        return removed
    
    def get_stats(self):
        """Get cache statistics"""
        total = 0
        expired = 0
        valid = 0
        
        for cache_file in self.cache_dir.glob("*.json"):
            total += 1
            try:
                with open(cache_file, 'r') as f:
                    cached = json.load(f)
                
                cached_time = datetime.fromisoformat(cached['timestamp'])
                if datetime.now() - cached_time > self.ttl:
                    expired += 1
                else:
                    valid += 1
                    
            except Exception:
                expired += 1
        
        return {
            'total': total,
            'valid': valid,
            'expired': expired,
            'cache_dir': str(self.cache_dir)
        }


class RateLimiter:
    """Simple rate limiter to prevent hitting API limits"""
    
    def __init__(self, min_interval_seconds=120):
        """
        Initialize rate limiter
        
        Args:
            min_interval_seconds: Minimum seconds between API calls (default 120s)
        """
        self.min_interval = min_interval_seconds
        self.last_call_time = {}
    
    def wait_if_needed(self, endpoint: str):
        """
        Wait if necessary to respect rate limits
        
        Args:
            endpoint: API endpoint name
        """
        if endpoint in self.last_call_time:
            elapsed = time.time() - self.last_call_time[endpoint]
            if elapsed < self.min_interval:
                wait_time = self.min_interval - elapsed
                print(f"⏳ Rate limit: waiting {wait_time:.1f}s before calling {endpoint}")
                time.sleep(wait_time)
        
        self.last_call_time[endpoint] = time.time()
