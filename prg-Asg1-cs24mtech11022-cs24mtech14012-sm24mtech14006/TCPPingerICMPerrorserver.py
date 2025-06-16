import socket  # We'll use the socket module to create both TCP and ICMP sockets
import random  # For generating random numbers and to simulate error conditions
import struct  # To work with binary data for creating ICMP packet headers
import os  # We'll use os to get the process ID, which we'll use as a packet identifier

# Define ICMP constants for "Destination Unreachable" and "Port Unreachable"
ICMP_TYPE_DEST_UNREACHABLE = 3  # Type 3 is "Destination Unreachable"
ICMP_CODE_PORT_UNREACHABLE = 3  # Code 3 means "Port Unreachable" within Destination Unreachable

# Function to create an ICMP error packet which will simulate sending an ICMP "Port Unreachable" message back to the client
def create_icmp_error(dest_addr, code=ICMP_CODE_PORT_UNREACHABLE):
    packet_type = ICMP_TYPE_DEST_UNREACHABLE  # We're creating a "Destination Unreachable" type of packet
    checksum = 0  # Checksum is initially 0
    packet_id = os.getpid() & 0xFFFF  # Use the process ID as the packet identifier, but limit it to 16 bits
    seq_number = 1  # Sequence number is set to 1 for simplicity

    # Pack the ICMP header (type, code, checksum placeholder, packet ID, and sequence number)
    header = struct.pack('bbHHh', packet_type, code, checksum, packet_id, seq_number)
    
    # Calculate the correct checksum for the packet
    checksum = calculate_checksum(header)
    
    # Repack the header with the correct checksum value in network byte order (big-endian)
    header = struct.pack('bbHHh', packet_type, code, socket.htons(checksum), packet_id, seq_number)
    
    return header  # Return the ICMP header, which we will use for the error message

# Function to calculate the checksum of a packet (standard for ICMP packets)
def calculate_checksum(source_string):
    countTo = (len(source_string) // 2) * 2  # We process two bytes (16 bits) at a time
    sum = 0  # Initialize the checksum sum
    count = 0  # Start from the first byte

    # Loop through the data, summing up all 16-bit words
    while count < countTo:
        this_val = source_string[count + 1] * 256 + source_string[count]  # Combine two bytes into a 16-bit word
        sum = sum + this_val  # Add the value to the sum
        sum = sum & 0xffffffff  # Keep it within 32 bits to avoid overflow
        count = count + 2  # Move to the next two bytes

    # If there's an odd byte left over, add it separately
    if countTo < len(source_string):
        sum = sum + source_string[len(source_string) - 1]
        sum = sum & 0xffffffff  # Again, ensure the sum doesn't overflow

    # Fold the carry bits (from the upper 16 bits) back into the lower 16 bits
    sum = (sum >> 16) + (sum & 0xffff)
    sum = sum + (sum >> 16)  # Add any remaining carry

    # Perform the one's complement of the sum
    answer = ~sum
    answer = answer & 0xffff  # Ensure it fits in 16 bits
    answer = answer >> 8 | (answer << 8 & 0xff00)  # Swap bytes to match network byte order (big-endian)
    return answer  # Return the checksum

# Main function for the TCP server
def tcp_server():
    # Create a TCP socket that will listen for incoming connections
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind(("0.0.0.0", 12001))  # Bind to all available interfaces on port 12001
    tcp_socket.listen(1)  # Listen for incoming connection requests, with a backlog of 1

    # Create a raw socket for sending ICMP error messages
    icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
   
    print("Server is running and waiting for TCP connections...")

    # Main loop to handle incoming connections
    while True:
        conn, addr = tcp_socket.accept()  # Accepting connection from a client
        print(f"Accepted connection from {addr}")  # Print the client's address

        # Generate a random number to decide whether to simulate an ICMP error or not
        rand_num = random.randint(1, 10)
        print(f"Random number: {rand_num}")  #  displaying the random number

        # If the random number is greater than 8, generate an ICMP error
        if rand_num > 8:
            print(f"Simulating ICMP error for {addr}")
            icmp_error = create_icmp_error(addr[0])  # Create an ICMP "Port Unreachable" packet
            icmp_socket.sendto(icmp_error, addr)  # Send the ICMP error packet to the client
            conn.close()  # Close the TCP connection after sending the ICMP error
        else:
            # Otherwise, send a normal response to the client
            print(f"Sending normal TCP response to {addr}")
            conn.close()  # Close the TCP connection once the message is sent

# Start the server
tcp_server()  # Run the TCP server function