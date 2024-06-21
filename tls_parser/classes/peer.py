# Class to represent TLS peers

class TLSPeer:

    def __init__(self, ip: str, port: int, supp_tls_versions: list[str] = None, supp_ecs: list[str] = None, supp_ciphers: list[str] = None, cert: str = None):
        self.ip = ip
        self.port = port
        self.supp_tls_versions = supp_tls_versions
        self.supp_ecs = supp_ecs
        self.supp_ciphers = supp_ciphers
        self.cert = cert

    def __str__(self) -> str:
        output = f'\tIP: {self.ip}\n\tPort: {self.port}\n\tSupported TLS versions: {self.supp_tls_versions}\n\tSupported ECs: {self.supp_ecs}\n\tSupported ciphers: {self.supp_ciphers}'
        return output

