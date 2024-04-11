#!/usr/bin/env python3

import socket
import threading
import time
import requests
import os

def send_http_traffic():
    print("Generating HTTP traffic...")
    end_time = time.time() + 15
    try:
        while time.time() < end_time:
            # Replace www.example.com with the actual destination IP if needed
            requests.get("http://www.example.com")
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass

def send_icmp_traffic(destination_ip):
    print("Generating ICMP traffic...")
    end_time = time.time() + 15
    try:
        while time.time() < end_time:
            os.system(f"ping -c 1 {destination_ip}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass

def send_udp_traffic(destination_ip, port):
    print("Generating UDP traffic...")
    end_time = time.time() + 15
    try:
        while time.time() < end_time:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.sendto(b"UDP Traffic", (destination_ip, port))
                time.sleep(0.1)
    except KeyboardInterrupt:
        pass

def send_tcp_traffic(destination_ip, port):
    print("Generating TCP traffic...")
    end_time = time.time() + 15
    try:
        while time.time() < end_time:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((destination_ip, port))
                s.send(b"TCP Traffic")
                s.close()
                time.sleep(0.1)
    except KeyboardInterrupt:
        pass

def main():
    
    ### Replace here with needed ###
    destination_ip = "192.168.1.1"  
    udp_port = 12345 
    tcp_port = 54321

    threads = [
        threading.Thread(target=send_http_traffic),
        threading.Thread(target=send_icmp_traffic, args=(destination_ip,)),
        threading.Thread(target=send_udp_traffic, args=(destination_ip, udp_port)),
        threading.Thread(target=send_tcp_traffic, args=(destination_ip, tcp_port)),
    ]

    # Start all threads
    for thread in threads:
        thread.start()

    # Run for 15 seconds
    time.sleep(15)

    # Stop all threads
    for thread in threads:
        thread.join()

    print("Traffic generation completed.")

if __name__ == "__main__":
    main()
