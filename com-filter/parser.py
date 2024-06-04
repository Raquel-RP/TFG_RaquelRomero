import pyshark
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from datetime import datetime

def analyze_tls_connections(pcap_file):
    # Abre el archivo pcap para análisis
    capture = pyshark.FileCapture(pcap_file)

    # Diccionario para almacenar información sobre las conexiones TLS
    tls_connections = {}

    # Iterar sobre cada paquete en la captura
    for packet in capture:
        # Verifica si el paquete utiliza el protocolo TLS
        if 'TLS' in packet:
            src_ip = packet.ip.src
            src_port = packet.tcp.srcport
            dst_ip = packet.ip.dst
            dst_port = packet.tcp.dstport

            # Crea una clave única para cada conexión basada en las direcciones IP y los puertos
            connection_key = f"{src_ip}:{src_port} -> {dst_ip}:{dst_port}"

            # Verifica si ya hemos visto esta conexión
            if connection_key not in tls_connections:
                tls_connections[connection_key] = {
                    'client_ip': src_ip,
                    'client_port': src_port,
                    'server_ip': dst_ip,
                    'server_port': dst_port,
                    'handshake': False,
                    'mutual_authentication': False,
                    'client_certificate': None,
                    'server_certificate': None
                }

            # Verifica si el paquete contiene un handshake TLS
            if hasattr(packet.tls, 'handshake_type'):
                tls_connections[connection_key]['handshake'] = True

                # Si el handshake es un cliente enviando certificados
                if packet.tls.handshake_type == '1': # 1 = Certificate
                    tls_connections[connection_key]['client_certificate'] = extract_certificate_info(packet.tls)

                # Si el handshake es un servidor solicitando certificados
                if packet.tls.handshake_type == '11': # 11 = Server Hello Done
                    tls_connections[connection_key]['server_certificate'] = extract_certificate_info(packet.tls)

    # Cierra la captura
    capture.close()

    # Imprime los resultados
    for key, connection in tls_connections.items():
        print(f"Conexión TLS: {connection['client_ip']}:{connection['client_port']} -> {connection['server_ip']}:{connection['server_port']}")
        if connection['handshake']:
            print("  Handshake TLS: Sí")
            if connection['client_certificate'] and connection['server_certificate']:
                print("    Autenticación mutua: Sí")
                print(f"    Cliente autenticado: {connection['client_certificate']['common_name']}, CA: {connection['client_certificate']['ca']}")
                print(f"    Servidor autenticado: {connection['server_certificate']['common_name']}, CA: {connection['server_certificate']['ca']}")
            else:
                print("    Autenticación mutua: No")
                if connection['client_certificate']:
                    print(f"    Cliente autenticado: {connection['client_certificate']['common_name']}, CA: {connection['client_certificate']['ca']}")
                if connection['server_certificate']:
                    print(f"    Servidor autenticado: {connection['server_certificate']['common_name']}, CA: {connection['server_certificate']['ca']}")
        else:
            print("  Handshake TLS: No")
        print()

def extract_certificate_info(tls_packet):
    cert_hex = tls_packet.handshake_certificate
    certificate_bytes = bytes.fromhex(cert_hex.replace(":", "").replace(" ", ""))
    certificate = x509.load_der_x509_certificate(certificate_bytes, default_backend())

    if certificate:
        common_name = certificate.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)
        ca = certificate.issuer.get_attributes_for_oid(x509.NameOID.COMMON_NAME)

        return {
            'common_name': common_name[0].value if common_name else None,
            'ca': ca[0].value if ca else None
        }
    else:
        return None

# Llama a la función con el archivo pcap como argumento
analyze_tls_connections('archivo.pcapng')
