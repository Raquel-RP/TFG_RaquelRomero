import argparse
from scapy.all import *

def analyze_pcap(pcap_file):
    packets = rdpcap(pcap_file)

    total_packets = len(packets)
    protocols = {}

    for packet in packets:
        if packet.haslayer(Ether):
            protocol = packet[Ether].name
        else:
            protocol = "Unknown"

        if protocol not in protocols:
            protocols[protocol] = 1
        else:
            protocols[protocol] += 1

    print("Total packets:", total_packets)
    print("Used protocols:")
    for protocol, count in protocols.items():
        print(f"{protocol}: {count} packets")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PCAP Analyzer and parser")
    parser.add_argument("pcap_file", type=str, help="Path to the pcap file")

    args = parser.parse_args()

    analyze_pcap(args.pcap_file)
