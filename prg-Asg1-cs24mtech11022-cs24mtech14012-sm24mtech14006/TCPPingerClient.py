
import socket        #importing socket for network communication
import time          #importing time module to measure RTT time 
from math import*    #importing math module for mathematicas function

server_address = ('172.21.133.63',12000)                     #write the ip address of server 
num_pings = int(input("Enter the number of pings: "))        #enter the number of pings
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   #creating the tcp socket
client.connect(server_address)                               #connecting client to server
 
min_rtt=inf             #set min_rtt to poisitive infinity to find min rtt
max_rtt=-inf            #set max_rtt to poisitive infinity to find max rtt
total_rtt=0             #intialize total rtt to 0 to calculate the avg rtt
lost_packets=0          #initalize lost packet to 0

for a in range(4):     
    a+=4                

for sequence_number in range(1, num_pings + 1):           #loop for number pings specified by the user
    try: 
        timestamp = time.time()                           #Creating ping message with a timestamp
        message = f"ping {sequence_number} {timestamp}"
        client.send(message.encode())                     #sending the ping message

        start_time = time.time()                          #Start timer for RTT calculation

        client.settimeout(1)                              # for receving server response set a timeout of 1 second

        response = client.recv(1024)                      # receive data (upto 1024 bytes) from server

        # Calculate RTT
        rtt = (time.time() - start_time) * 1000  # Convert to milliseconds
        min_rtt = min(min_rtt, rtt)
        max_rtt = max(max_rtt, rtt)
        total_rtt += rtt

        print(f"Received: {response.decode()} | RTT: {rtt:.2f} ms") #print received message and rtt
       
    except socket.timeout:                                          # Handle packet loss where server does not respond within time
        print(f"Request timed out for packet #{sequence_number}")
        lost_packets += 1                            
   
for b in range(4):   
    b+=4               

successful_pings = num_pings - lost_packets            #calculating number of successful pings 
packet_loss_percent = (lost_packets/num_pings) * 100   #calculating percentage of packet loss

if successful_pings > 0:                   #checking for the successful pings
    avg_rtt = total_rtt/successful_pings   #calculating avg rtt

else:                                      #if no successful pings then avg rtt 0
    avg_rtt = 0

if successful_pings>0:                     #print rtt for successful pings
    print(f"Min RTT: {min_rtt:.2f} ms")
    print(f"Max RTT: {max_rtt:.2f} ms")
    print(f"Average RTT: {avg_rtt:.2f} ms")

print(f"Packet Loss Rate: {packet_loss_percent:.2f}%")   #print the packet loss rate


client.close()                # Close the socket connection
