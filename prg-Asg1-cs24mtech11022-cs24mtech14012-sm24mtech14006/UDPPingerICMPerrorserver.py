from socket import *
import socket
import random
import struct
import os

# Constants for ICMP message
ICMP_TYPE_DEST_UNREACHABLE = 3
ICMP_CODE_PORT_UNREACHABLE = 3

# Function to create an ICMP error packet (simulates unreachable port)
def create_icmp_error(dest_addr, code=ICMP_CODE_PORT_UNREACHABLE):
    packet_type = ICMP_TYPE_DEST_UNREACHABLE
    checksum = 0  # Placeholder for now, we'll calculate it next
    packet_id = os.getpid() & 0xFFFF  # Use the process ID for identification
    seq_number = 1  # Just a simple sequence number

    # Create the ICMP header (checksum is zero for now)
    header = struct.pack('bbHHh', packet_type, code, checksum, packet_id, seq_number)
    checksum = calculate_checksum(header)  # Calculate correct checksum
    # Pack the header again with the correct checksum
    header = struct.pack('bbHHh', packet_type, code, socket.htons(checksum), packet_id, seq_number)
   
    return header  # Return the final ICMP header

# Calculate checksum for ICMP (used for error detection)
def calculate_checksum(source_string):
    countTo = (len(source_string) // 2) * 2
    sum = 0
    count = 0

    # Add 2 bytes at a time
    while count < countTo:
        this_val = source_string[count + 1] * 256 + source_string[count]
        sum = sum + this_val
        sum = sum & 0xffffffff  # Keep within 32 bits
        count = count + 2

    # Handle any remaining byte (if the data length is odd)
    if countTo < len(source_string):
        sum = sum + source_string[len(source_string) - 1]
        sum = sum & 0xffffffff

    # Fold 32-bit sum into 16 bits
    sum = (sum >> 16) + (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum  # Invert the bits for the checksum
    answer = answer & 0xffff  # Mask to 16 bits
    # Swap bytes because network uses big-endian
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

# Function for the UDP server
def udp_server():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create UDP socket
    udp_socket.bind(("0.0.0.0", 12000))  # Bind to port 12000

    # Create raw ICMP socket for sending ICMP errors
    icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))

    print("Server is running and waiting for UDP connections...")
   
    while True:
        # Receive UDP data and client addressx
        data, addr = udp_socket.recvfrom(1024)
        print(f"Received UDP request from {addr}")

        # Generate a random number (to decide if we'll simulate an ICMP error)
        rand_num = random.randint(1, 10)
        print(f"Random number: {rand_num}")
       
        if rand_num > 8:
            # If random number is high, simulate ICMP error
            print(f"Simulating ICMP error for {addr}")
            icmp_error = create_icmp_error(addr[0])
            icmp_socket.sendto(icmp_error, addr)
        else:
            # Otherwise, just echo back the data to the client
            print(f"Sending normal UDP response to {addr}")
            udp_socket.sendto(data, addr)

# Run the server
udp_server()