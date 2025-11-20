import time
import hashlib
import json
from typing import Any, Optional
from collections import OrderedDict
import threading

class CacheManager:
    def __init__(self, max_size: int = 1000, ttl: int = 300):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.ttl = ttl
        self.lock = threading.Lock()
    
    def _generate_key(self, *args, **kwargs) -> str:
        key_data = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True)
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                if time.time() - timestamp < self.ttl:
                    self.cache.move_to_end(key)
                    return value
                else:
                    del self.cache[key]
            return None
    
    def set(self, key: str, value: Any):
        with self.lock:
            if key in self.cache:
                del self.cache[key]
            elif len(self.cache) >= self.max_size:
                self.cache.popitem(last=False)
            
            self.cache[key] = (value, time.time())
    
    def clear(self):
        with self.lock:
            self.cache.clear()
    
    def remove(self, key: str):
        with self.lock:
            if key in self.cache:
                del self.cache[key]
    
    def get_stats(self):
        with self.lock:
            current_time = time.time()
            active_entries = sum(1 for _, (_, ts) in self.cache.items() 
                               if current_time - ts < self.ttl)
            return {
                'total_entries': len(self.cache),
                'active_entries': active_entries,
                'max_size': self.max_size,
                'ttl': self.ttl
            }
