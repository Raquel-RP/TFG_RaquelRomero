from classes import TLSServer, TLSClient, TLSConnection
from termcolor import colored
import pyshark
import click


# Returns True if packet contains TLS layer, else False
def is_tls(pkt: pyshark.packet) -> bool:
    return "tls" in pkt


# If packet is ClientHello returns True, else False
def is_clienthello(pkt: pyshark.packet) -> bool:
    try:
        return pkt.tls.handshake_type == "1"
    except:
        return False


# If packet is ServerHello returns True, else False
def is_serverhello(pkt: pyshark.packet) -> bool:
    try:
        return pkt.tls.handshake_type == "2"
    except:
        return False


# Convert from hexadecimal value of TLS versions to text
def prettify_tls_version(hex_versions: list) -> list:
    prettified_tls_version = []

    for hex_version in hex_versions:
        version = hex_version.showname_value
        prettified_tls_version.append(version)

    return prettified_tls_version


# Convert from hexadecimal value of cipher suites to text
def prettify_ciphersuite(hex_ciphers: list) -> list:
    prettified_ciphers = []

    for hex_cipher in hex_ciphers:
        cipher = hex_cipher.showname_value
        prettified_ciphers.append(cipher)

    return prettified_ciphers


# Convert from hexadecimal value of supported groups to text
def prettify_supp_groups(hex_groups: list) -> list:
    prettified_groups = []

    for hex_group in hex_groups:
        group = hex_group.showname_value
        prettified_groups.append(group)

    return prettified_groups


@click.command()
@click.option(
    "-c", "--capture_file", required=True, help="Wireshark pcap filename to parse"
)
def main(capture_file: str) -> None:
    cap = pyshark.FileCapture(capture_file)
    connections = []
    client = None
    server = None
    conn = None

    # Iterate pcap/pcapng packets and detect TLS connections
    for pkt in cap:

        if is_tls(pkt):
            # If ClientHello packet found, create TLS Client
            if is_clienthello(pkt):
                supported_versions = []
                if hasattr(pkt.tls, "handshake_extensions_supported_version"):
                    supported_versions = prettify_tls_version(
                        pkt.tls.handshake_extensions_supported_version.all_fields
                    )
                client = TLSClient(
                    pkt.ip.addr,
                    pkt.tcp.port,
                    supp_tls_versions=supported_versions
                )
                client.supp_ciphers = prettify_ciphersuite(
                    pkt.tls.handshake_ciphersuite.all_fields
                )
                client.supp_ecs = prettify_supp_groups(
                    pkt.tls.handshake_extensions_supported_group.all_fields
                )
                if hasattr(pkt.tls, "handshake_certificate"):
                    client.cert = pkt.tls.handshake_certificate.show
                    client.has_cert = True
                
            # If ServerHello packet found, create TLS Server
            elif is_serverhello(pkt):
                server = TLSServer(
                    pkt.ip.addr,
                    pkt.tcp.port,
                    supp_tls_versions=pkt.tls.handshake_version.showname_value
                )
                server.supp_ciphers = prettify_ciphersuite(
                    pkt.tls.handshake_ciphersuite.all_fields
                )
                if hasattr(pkt.tls, "handshake_certificate"):
                    server.cert = pkt.tls.handshake_certificate.show

        if client and server:
            conn = TLSConnection(server, client)
            connections.append(conn)
            client = None
            server = None
            conn = None

    count = 0
    for conn in connections:
        print(colored(f"Connection: {count}", "light_yellow"))
        print(colored(f"\t{conn.server}", "light_blue"))
        print(colored(f"\t{conn.client}", "light_cyan"))
        count += 1


if __name__ == "__main__":
    main()
