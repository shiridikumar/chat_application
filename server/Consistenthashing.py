import hashlib


class ConsistentHashing:
    def __init__(self, servers, replicas=1):
        self.servers = []
        self.replicas = replicas
        self.hash_ring = {}

        for server in servers:
            self.add_server(server)
        print(self.servers, "********************************")

    def add_server(self, server):
        self.servers.append(server)

        for i in range(self.replicas):
            replica_server = f"{server}:{i}"
            key = self.hash_key(replica_server.encode('utf-8'))
            self.hash_ring[key] = server

    def remove_server(self, server):
        self.servers.remove(server)

        for i in range(self.replicas):
            replica_server = f"{server}:{i}"
            key = self.hash_key(replica_server.encode('utf-8'))
            del self.hash_ring[key]

    def get_server(self, request):
        if not self.servers:
            return None

        hash_key = self.hash_key(request.encode('utf-8'))
        sorted_keys = sorted(self.hash_ring.keys())
        print(sorted_keys, hash_key)

        for k in sorted_keys:
            if hash_key <= k:
                print("yahooooo", "found*******************")
                return self.hash_ring[k]

        return self.hash_ring[sorted_keys[0]]

    def hash_key(self, key):
        return int.from_bytes(hashlib.sha256(key).digest(), byteorder='big')
