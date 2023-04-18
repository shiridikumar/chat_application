import hashlib

class ConsistentHashing:
    def __init__(self, servers, replicas=3):
        self.servers = []
        self.replicas = replicas
        self.hash_ring = {}
        
        for server in servers:
            self.add_server(server)
            
    def add_server(self, server):
        self.servers.append(server)
        
        for i in range(self.replicas):
            replica_server = f"{server}:{i}"
            key = self.hash_key(replica_server)
            self.hash_ring[key] = server
            
    def remove_server(self, server):
        self.servers.remove(server)
        
        for i in range(self.replicas):
            replica_server = f"{server}:{i}"
            key = self.hash_key(replica_server)
            del self.hash_ring[key]
            
    def get_server(self, request):
        if not self.servers:
            return None
        
        hash_key = self.hash_key(request)
        sorted_keys = sorted(self.hash_ring.keys())
        
        for k in sorted_keys:
            if hash_key <= k:
                return self.hash_ring[k]
            
        return self.hash_ring[sorted_keys[0]]
    
    def hash_key(self, key):
        return int(hashlib.sha1(key.encode()).hexdigest(), 16)
