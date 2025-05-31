import pickle
import threading
import time

from dnslib import QTYPE


class DNSCache:
    def __init__(self, default_ttl=60):
        self.cache = {}  # {(qname, qtype): (expire_time, record)}
        self.lock = threading.Lock()
        self.default_ttl = default_ttl  # TTL по умолчанию (60 секунд)

    def add_record(self, rr):
        """Добавляем запись с ограниченным TTL"""
        normalized_name = str(rr.rname).lower().rstrip('.')
        cache_key = (normalized_name, QTYPE[rr.rtype])

        # Ограничиваем TTL значением default_ttl
        ttl = min(rr.ttl if rr.ttl > 0 else float('inf'), self.default_ttl)
        expire_time = time.time() + ttl

        with self.lock:
            self.cache[cache_key] = (expire_time, rr)
            print(f"Добавлено: {cache_key}, TTL: {ttl}сек")

    def get_records(self, qname, qtype):
        normalized_name = str(qname).lower()
        if normalized_name.endswith('.'):
            normalized_name = normalized_name[:-1]

        cache_key = (normalized_name, QTYPE[qtype])
        print(f"Ищем в кэше: {cache_key}")

        now = time.time()
        with self.lock:
            if cache_key in self.cache:
                expire_time, rr = self.cache[cache_key]
                if now <= expire_time:
                    print(f"Найдено в кэше: {rr.rname} {QTYPE[rr.rtype]} (TTL: {expire_time - now:.0f}сек)")
                    return [rr]
                del self.cache[cache_key]
        return None

    def clean_expired(self):
        now = time.time()
        with self.lock:
            keys = list(self.cache.keys())
            for key in keys:
                expire_time, _ = self.cache[key]
                if now > expire_time:
                    del self.cache[key]

    def save(self, filename='dns_cache.pkl'):

        with self.lock:
            self.clean_expired()
            with open(filename, 'wb') as f:
                pickle.dump({
                    'cache': self.cache,
                    'default_ttl': self.default_ttl}, f)

    def load(self, filename='dns_cache.pkl'):

        try:
            with open(filename, 'rb') as f:
                data = pickle.load(f)
                with self.lock:
                    self.cache = data.get('cache', {})
                    self.default_ttl = data.get('default_ttl', 60)
                    self.clean_expired()
        except (FileNotFoundError, pickle.PickleError):
            self.cache = {}