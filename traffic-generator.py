#!/usr/bin/env python3

import socket
import threading
import time
import requests
import os


# Function to generate HTTP traffic
def send_http_traffic():
    print("Generating HTTP traffic...")
    end_time = time.time() + 15  # Run for 15 seconds
    try:
        while time.time() < end_time:
            requests.get("http://www.google.com")  # Send HTTP GET request
            time.sleep(0.1)  # Pause briefly between requests
    except KeyboardInterrupt:
        pass  # Handle keyboard interrupt gracefully


# Function to generate ICMP traffic
def send_icmp_traffic(destination_ip):
    print("Generating ICMP traffic...")
    end_time = time.time() + 15  # Run for 15 seconds
    try:
        while time.time() < end_time:
            os.system(f"ping -c 1 {destination_ip}")  # Send one ping packet
            time.sleep(0.1)  # Pause briefly between pings
    except KeyboardInterrupt:
        pass  # Handle keyboard interrupt gracefully


# Function to generate UDP traffic
def send_udp_traffic(destination_ip, port):
    print("Generating UDP traffic...")
    end_time = time.time() + 15  # Run for 15 seconds
    try:
        while time.time() < end_time:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.sendto(b"UDP Traffic", (destination_ip, port))  # Send UDP packet
                time.sleep(0.1)  # Pause briefly between packets
    except KeyboardInterrupt:
        pass  # Handle keyboard interrupt gracefully


# Function to generate TCP traffic
def send_tcp_traffic(destination_ip, port):
    print("Generating TCP traffic...")
    end_time = time.time() + 15  # Run for 15 seconds
    try:
        while time.time() < end_time:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((destination_ip, port))  # Establish TCP connection
                s.send(b"TCP Traffic")  # Send TCP packet
                s.close()  # Close connection
                time.sleep(0.1)  # Pause briefly between packets
    except KeyboardInterrupt:
        pass  # Handle keyboard interrupt gracefully


# Main function to start traffic generation
def main():
    destination_ip = "192.168.1.1"  # Target IP address
    udp_port = 12345  # Target UDP port
    tcp_port = 54321  # Target TCP port

    # Create threads for each type of traffic
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

    # Ensure all threads have finished
    for thread in threads:
        thread.join()

    print("Traffic generation completed.")


if __name__ == "__main__":
    main()
