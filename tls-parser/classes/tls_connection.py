# Class to represent a TLS connection

from .client import TLSClient
from .server import TLSServer

class TLSConnection:

    def __init__(self, server: TLSServer, client: TLSClient, is_mtls: bool = False, tls_version: str = None):
        self.server = server
        self.client = client
        self.is_mtls = is_mtls
        self.tls_version = tls_version 

