import socket #importing sockets for creating and to manage sockets
import os #importing os to access system functionalities
import time #importing time module for for time-related purpose
import struct #importing strruct module for working with packed binary data
import select # importing select module to monitor sockets for events

# using dictionary for mapping ICMP error codes to human-readable messages for "Destination Unreachable" errors
ICMP_CODE_UNREACHABLE = {
    0: "Destination Network Unreachable",
    1: "Destination Host Unreachable",
    3: "Port Unreachable",
}

# Checksum calculation function
def checksum(source_string):
    sum = 0  # Initializing checksum sum to 0
    count = 0  # Initializing byte counter to 0
    countTo = (len(source_string) // 2) * 2  # Calculating the number of 16-bit words to process

    # Loop through the data in 2-byte chunks and sum them up
    while count < countTo:
        sum = sum + (source_string[count + 1] * 256 + source_string[count])  # Combining two bytes into a 16-bit word
        sum = sum & 0xffffffff  # Ensuring that the sum stays within 32 bits
        count += 2  # Moving to the next pair of bytes

    # If there's an odd number of bytes, handling  the last byte separately
    if countTo < len(source_string):
        sum = sum + source_string[len(source_string) - 1]
        sum = sum & 0xffffffff  # making sure that the sum stays within 32 bits

    # Carry over the high-order bits
    sum = (sum >> 16) + (sum & 0xffff)
    sum = sum + (sum >> 16)  # Adding carry if any

    answer = ~sum  # One's complement of sum
    answer = answer & 0xffff  # Mask to 16 bits
    answer = answer >> 8 | (answer << 8 & 0xff00)  # Byte swap to network byte order
    return answer  # Return the checksum

# Function to capture and handle ICMP error messages (like "Destination Unreachable")
def receive_icmp_error(my_socket, timeout):
    time_left = timeout  # Set the timeout period for receiving the ICMP packet
    while True:
        start_time = time.time()  # Record the time before select call
        # Wait for data to be available on the socket (with a timeout)
        ready = select.select([my_socket], [], [], time_left)
        time_in_select = (time.time() - start_time)  # Measure time spent in select

        # If no data is present within the timeout, return a timeout message
        if ready[0] == []:
            return "Request timed out."

        time_received = time.time()  # Recording the time when the packet was received
        rec_packet, addr = my_socket.recvfrom(1024)  # Receiving the ICMP packet from the socket
        # Unpack the ICMP header (the first 8 bytes of the ICMP message)
        icmp_header = rec_packet[20:28]
        icmp_type, code, checksum, packet_id, sequence = struct.unpack("bbHHh", icmp_header)

        # If it's a "Destination Unreachable" message (ICMP Type 3)
        if icmp_type == 3:
            if code in ICMP_CODE_UNREACHABLE:  # Look up the error code in the dictionary
                return f"Error: {ICMP_CODE_UNREACHABLE[code]}"  # Return the appropriate error message
            else:
                return f"Error: Unknown ICMP error code {code}"  # Handle unknown ICMP error codes

        # Adjust the remaining time for the next select call
        time_left = time_left - time_in_select
        if time_left <= 0:  # If no time is left, return a timeout message
            return "Request timed out."

# TCP Client function that sends requests and handles ICMP errors
def tcp_client(server_ip, num_requests=10, timeout=1):
    # Create a raw socket for ICMP (to capture error messages)
    icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))

    # Loop to send multiple TCP requests
    for i in range(num_requests):
        try:
            print(f"Sending TCP request {i+1}/{num_requests} to {server_ip}")

            # Create a TCP socket
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.settimeout(timeout)  # Set a timeout for the TCP connection

            try:
                tcp_socket.connect((server_ip, 12002))  # Try to connect to the server on port 12001
                response = tcp_socket.recv(1024)  # Receive response data from the server
                print(f"Received response from server: {response.decode()}")  # Print the server response

            # Handle timeout if the server doesn't respond within the timeout period
            except socket.timeout:
                print("TCP connection timed out.")
            # Handle connection refusal (if the server is not listening on the port)
            except ConnectionRefusedError:
                print("TCP connection refused.")
            finally:
                tcp_socket.close()  # Close the TCP socket after the request

            # Check for ICMP error messages (like "Destination Unreachable")
            icmp_error = receive_icmp_error(icmp_socket, timeout)
            if "Error" in icmp_error:
                print(icmp_error)  # Print any ICMP error messages if detected

        # Catch any other unexpected errors and print the exception
        except Exception as e:
            print(f"An error occurred: {e}")
        time.sleep(1)  # Wait for 1 second before sending the next request

    icmp_socket.close()  # Close the ICMP socket after all requests are done

# Run the TCP client
tcp_client("192.168.195.217", num_requests=30)  # Call the client function with 30 requests to the localhost