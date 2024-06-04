import pyshark

pcap_file = 'archivo.pcapng'

def get_certificate_expiry_tls(pcap_file,destination="192.168.1.97"):
    capture = pyshark.FileCapture(pcap_file, display_filter='tls.handshake.type == 11')
    found = False
    for packet in capture:
            dest_ip = "192.168.1.97"
            if (destination !="" and dest_ip == destination) or destination == "":
                cert_hex = packet.tls.handshake_certificate
                certificate_bytes = bytes.fromhex(cert_hex.replace(":", "").replace(" ", ""))
                certificate = x509.load_der_x509_certificate(certificate_bytes, default_backend())

                # Extract certificate details
                issuer = certificate.issuer
                cert_sn = certificate.serial_number
                not_before = datetime.strptime(str(certificate.not_valid_before), "%Y-%m-%d %H:%M:%S")
                not_after = datetime.strptime(str(certificate.not_valid_after), "%Y-%m-%d %H:%M:%S")
                days_left = (not_after - datetime.now()).days
                too_early = False
                too_late = False
                if not_before > datetime.now():
                    too_early = True
                if datetime.now() > not_after:
                    too_late = True

                print(f'Certificate Validity for destination {dest_ip}')
                print(f'Issuer: {issuer}')
                print(f'Serial Number: {cert_sn}')
                if too_early:
                    print(f'>>>Not Before: {not_before}<<<')
                else:
                    print(f'   Not Before: {not_before}')
                if too_late:
                    print(f'>>>Not After: {not_after}<<<')
                else:
                    print(f'   Not After: {not_after}')
                print(f'  Days Left: {days_left} days')
                print('---')
                found = True
    if not found:
       print(f'No certificate found on destination {destination}')

    capture.close()
    return()

get_certificate_expiry_tls(pcap_file)