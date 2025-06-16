import socket  # We'll need the socket module for network communication
import os  # Used for accessing OS-level functions like process ID
import time  # We'll use the time module to handle timeouts and delays
import struct  # Needed for packing and unpacking binary data (like ICMP headers)
import select  # For monitoring socket readiness with a timeout

# ICMP constants: type 8 is for Echo Request (i.e., a ping request)
ICMP_ECHO_REQUEST = 8

# Mapping ICMP "Destination Unreachable" codes to human-readable messages
ICMP_CODE_UNREACHABLE = {
    0: "Destination Network Unreachable",
    1: "Destination Host Unreachable",
    3: "Port Unreachable",
}

# Function to calculate the checksum for the ICMP packet (essentially a way to ensure data integrity)
def checksum(source_string):
    sum = 0  # This will accumulate the sum of the data
    # We'll process two bytes at a time, so we calculate how many full 2-byte chunks there are
    countTo = (len(source_string) // 2) * 2
    count = 0

    # Loop through the string two bytes at a time
    while count < countTo:
        # Convert the two bytes into a single 16-bit value (big-endian format)
        thisVal = source_string[count + 1] * 256 + source_string[count]
        sum = sum + thisVal  # Add the value to the running sum
        sum = sum & 0xffffffff  # Make sure we don't overflow beyond 32 bits
        count = count + 2  # Move to the next two bytes

    # If the length of the string is odd, we have one last byte to process
    if countTo < len(source_string):
        sum = sum + source_string[len(source_string) - 1]
        sum = sum & 0xffffffff  # Again, ensure we don't exceed 32 bits

    # Fold the sum into 16 bits by adding the upper 16 bits to the lower 16 bits
    sum = (sum >> 16) + (sum & 0xffff)
    sum = sum + (sum >> 16)  # Add any remaining carry
    answer = ~sum  # Perform a bitwise NOT to get the checksum
    answer = answer & 0xffff  # Mask to 16 bits
    # Swap bytes (because network order is big-endian)
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer  # Return the calculated checksum

# Function to receive ICMP error messages (e.g., Destination Unreachable)
def receive_icmp_error(my_socket, timeout):
    time_left = timeout  # Start with the full timeout value
    while True:
        start_time = time.time()  # Record the start time of this cycle
        ready = select.select([my_socket], [], [], time_left)  # Wait for the socket to be ready or timeout
        time_in_select = (time.time() - start_time)  # Measure how long select() took

        if ready[0] == []:  # If no socket is ready (timeout expired)
            return "Request timed out."

        time_received = time.time()  # Time when the packet is received
        rec_packet, addr = my_socket.recvfrom(1024)  # Read the incoming packet (max 1024 bytes)
        icmp_header = rec_packet[20:28]  # Extract the ICMP header from the packet
        icmp_type, code, checksum, packet_id, sequence = struct.unpack("bbHHh", icmp_header)  # Unpack it

        # If the ICMP message is of type 3 (Destination Unreachable)
        if icmp_type == 3:
            if code in ICMP_CODE_UNREACHABLE:
                # Return the appropriate human-readable error message
                return f"Error: {ICMP_CODE_UNREACHABLE[code]}"
            else:
                # If we don't know the code, return a generic error message
                return f"Error: Unknown ICMP error code {code}"

        # Subtract the time spent in select() from the remaining time
        time_left = time_left - time_in_select
        if time_left <= 0:  # If we've run out of time
            return "Request timed out."

# Function to send a basic UDP ping message to the server
def send_udp_ping(udp_socket, dest_addr):
    udp_socket.sendto(b"Ping", (dest_addr, 12000))  # Send a "Ping" message to the server at port 12000

# Main function that runs the UDP client, sends pings, and listens for ICMP errors
def udp_client(server_ip, num_pings=10, timeout=1):
    # Create a UDP socket for sending the ping messages
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Create a raw ICMP socket to listen for ICMP error messages (like "Destination Unreachable")
    icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))

    # Loop through the number of pings we want to send
    for i in range(num_pings):
        try:
            print(f"Sending ping {i+1}/{num_pings} to {server_ip}")
            send_udp_ping(udp_socket, server_ip)  # Send a ping via UDP

            # After sending the ping, listen for any ICMP errors
            icmp_error = receive_icmp_error(icmp_socket, timeout)
            if "Error" in icmp_error:
                # If we receive an ICMP error, print it
                print(icmp_error)
            else:
                # If no error, assume we received a valid response
                print(f"Received from {server_ip}")

        # Handle cases where the socket times out waiting for a response
        except socket.timeout:
            print("Request timed out.")
        # Catch any other errors that might occur during the process
        except Exception as e:
            print(f"An error occurred: {e}")

        time.sleep(1)  # Wait for 1 second before sending the next ping

    # Close both the UDP and ICMP sockets when we're done
    udp_socket.close()
    icmp_socket.close()

# Run the UDP client to send pings to the specified server
udp_client("192.168.195.217", num_pings=20)