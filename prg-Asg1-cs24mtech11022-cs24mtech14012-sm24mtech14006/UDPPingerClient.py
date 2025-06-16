import socket             #importing socket for network communication
import time               #importing time module to measure RTT time
from math import inf      #importing math module for mathematicas function

# Input from the user
server_address = ('172.21.133.63', 11000)                          #write the ip address of server 
server_port = int(input("Enter server port: "))       #write the server port number
N = int(input("Enter number of pings: "))             #enter the number of pings


min_rtt=inf          #set min_rtt to poisitive infinity to find min rtt
max_rtt=-inf         #set max_rtt to poisitive infinity to find max rtt
total_rtt=0          #intialize total rtt to 0 to calculate the avg rtt
lost_packets=0       #initalize lost packet to 0


client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)     #creating udp server
client_socket.settimeout(2)                                        # Set timeout of 1 second for waiting for the response

for sequence_number in range(1, N + 1):
    message = f"Ping {sequence_number} {time.time()}"               # Preparing the message with sequence number
    
    try:
        start_time = time.time()                                   # Record the time before sending the message
        
        client_socket.sendto(message.encode(), ('172.21.133.63', server_port))   # Sending the ping message to the server
        
        response, addr = client_socket.recvfrom(1024)        # receive data (upto 1024 bytes) from server
        
        end_time = time.time()
        
        # Calculate RTT in milliseconds
        rtt = (end_time - start_time) * 1000
        min_rtt = min(min_rtt, rtt)
        max_rtt = max(max_rtt, rtt)
        total_rtt += rtt
        
        
        print(f"Response from server: {response.decode()}")              #printing server response
        print(f"Sequence number: {sequence_number}, RTT: {rtt:.3f} ms")  #printing rtt 
    
    except socket.timeout:                                               # Handle packet loss where server does not respond within time
        print(f"Request timed out for the packet #{sequence_number}")
        lost_packets+= 1

client_socket.close()       # Close the socket after the loop


successful_pings = N - lost_packets                #calculating number of successfull pings
packet_loss_percent = (lost_packets/N) * 100       #calculating packet loss percentage
if successful_pings > 0:
    avg_rtt = total_rtt/successful_pings           #calculating avg rtt for successful pings

else:                                              #if no successful pings then avg rtt 0
    avg_rtt = 0

if successful_pings>0:                             #print rtt for successful pings
    print(f"Min RTT: {min_rtt:.2f} ms")
    print(f"Max RTT: {max_rtt:.2f} ms")
    print(f"Average RTT: {avg_rtt:.2f} ms")
    
print(f"Packet Loss Rate: {packet_loss_percent:.2f}%")      #print the packet loss rate