# Class to represent a TLS 

from .peer import TLSPeer

class TLSClient (TLSPeer):

    def __init__(self, ip: str, port: int, supp_tls_versions: list[str] = None, supp_ecs: list[str] = None, supp_ciphers: list[str] = None, has_cert: bool = False):
        self.is_server = False
        self.has_cert = has_cert
        super(TLSClient, self).__init__(ip, port, supp_tls_versions, supp_ecs, supp_ciphers)

    def __str__(self) -> str:
        output = f'Client\n\t------\n\tIP: {self.ip}\n\tPort: {self.port}\n\tSupported TLS versions: {self.supp_tls_versions}\n\tSupported ECs: {self.supp_ecs}\n\tSupported ciphers: \n'
        for cipher in self.supp_ciphers:
            output += f'\t\t{cipher}\n'
        return output
