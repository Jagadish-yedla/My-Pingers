# PROJECT OVERVIEW
This project is divided into three parts, implementing ping protocols using UDP, TCP, and ICMP. Each part simulates a ping server and client, allowing clients to send packets and measure round-trip times (RTT) while handling packet loss.

# REQUIRED TOOLS
Python 3
Linux machine (for tc-netem packet loss simulation)

tc (traffic control) utility:
Install with: sudo apt-get install iproute2

# REQUIREMENTS
libraries:
* socket - for importing sockets
* threading - to run multiple clients concurrently(TCP concurrency)
* time - to calculate RTTs
* random - for generating random numbers

linux utilities:
* tc - for NIC level packetloss stimulation

# UDP PINGER 
In part-1 we creating a simple UDP-based ping client and server, mimicking the behavior of standard ICMP-based ping programs. The server responds to ping messages by sending  messages back in uppercase, while the client measures round-trip times (RTTs), simulates packet loss, and reports statistics as minimum,maximum and average RTT as well as packet loss rate.
This project introduces artificial packet loss in two ways:
-->Application-level loss simulation (default server)
-->NIC-level loss simulation using tc-netem (modified server)

icmp_error:
This script combines both a UDP client and server to simulate sending and receiving ping requests and handling ICMP error messages.
The client sends UDP ping requests to a server and listens for potential ICMP "Destination Unreachable" errors.
The ICMP messages are processed using raw sockets and checksum functions to ensure message integrity.
The server can simulate ICMP errors by generating them randomly and sending them to the client.
The script is designed to simulate real-world network behavior, including packet loss and errors.


## FILES
server - UDPPingerServer.py
client - UDPPingerClient.py
modifiedserver - UDPModifiedPingerServer.py
icmp_error server - UDPPingerICMPerrorserver.py
icmp_error client - UDPPingerICMPerrorclient.py

## HOW TO RUN 
--> to run the UDPserver - python3 UDPPingerServer.py 
--> to run UDP client - python3 UDPPingerClient.py
Modiffied server
-->to inject 20% packet loss on the server's NIC. - sudo tc qdisc add dev <interface> root netem loss 20%
--> to remove loss - sudo tc qdisc del dev <interface> root

interfaces:
--> lo interface is the loopback interface used for internal network communication within the host
-->enp0s3 - physical network interface typically used for connecting to an external network or the internet. 

to run icmp_error_codes:
run icmp_error_server: python3
and then run icmp_error_client: 
## HOW IT WORKS
1. After entering server_address(IP), server_port, N(no. of pings).
2. The client sends a series of N UDP ping messages to a specified server.
3. For each ping, the client calculates the time it was taken to receive a reply back from the server(RTT).
4. If successful_pings are greater than 0 then client calculates  :
    - MINIMUM RTT
    - MAXIMUM RTT
    - AVERAGE RTT
    - PACKET LOSS PERCENT
5. for UDP modified server , injecting loss using tc-netem 

icmp_error_code: 
 - The client sends a UDP ping to the server and waits for a response or ICMP error messages using raw sockets.
 - The server listens on port 12000 and randomly decides whether to respond to the ping or simulate an ICMP error.
 - If the server simulates an ICMP error, it sends a properly constructed ICMP "Port Unreachable" message using a checksum function.
 - The client listens for ICMP error messages and prints human-readable messages based on the error type.
 - The process repeats for a set number of pings, and both the UDP and ICMP sockets are closed when finished.

## Error Handling
If timeout occurs, print the timeout message by catching a timeout exception and increment the packet loss count



# TCP PINGER
In part-2 we are implementing TCP SERVER, TCP CLIENT, TCP CONCURRENT_CLIENT
TCP CONCURRENT_SERVER accepts multiple clients concurrently and handling each connection on a separate thread
TCP client sends ping messages and recieves responses from the TCP SERVER , also calculates the RTTs min,max and avg same like as above udp client.
In this part, we switch from the connectionless UDP protocol to the connection-oriented TCP protocol. TCP ensures that all packets are reliably delivered in the correct order, but we still simulate packet loss at the server to emulate unreliable network behavior

TCP_PINGER_ICMP_ERROR_SERVER: This program simulates a TCP server that randomly sends either a normal TCP response or an ICMP "Port Unreachable" error. It uses two sockets: one for TCP communication and another raw socket for sending ICMP error messages. The server listens on port 12001, and upon receiving a connection, a random number determines whether to reply with a normal message or simulate a port unreachable error via ICMP. The ICMP packet is manually constructed with a calculated checksum before being sent back to the client.

TCP_PINGER_ICMP_ERROR_CLIENT:
This implements a TCP client that sends multiple connection requests to a server and checks for ICMP error messages like "Destination Unreachable." The client connects to a specified server using TCP and listens for ICMP error responses using raw sockets.

## FILES
server - TCPPingerServer.py
client - TCPPingerCLient.py
modifiedserver - TCPModifiedPingerServer.py
icmp_error_server - TCPPingerICMPerrorserver.py
icmp_error_client - TCPPingerICMPerrorclient.py

## HOW TO RUN 
to run tcpserver - python3 TCPPingerServer.py
to run tcp client - python3 TCPPingerCLient.py

to run tcp concurrentserver - python3 TCPModifiedPingerServer.py
and then run multiple clients 

to run tcp_icmp_error_server- python3 TCPPingerICMPerrorserver.py
and then run client - python3 TCPPingerICMPerrorclient.py


## HOW IT WORKS
1. The user needs to enter Number of pings needed to be sent to sever
2. The TCP client sends a series of ping messages to the TCP server and records the round-trip time (RTT) for each  ping
3.  If a response is not received within 1 second, it considers the packet lost and prints a timeout message.
4. After all pings, the client calculates :
    - MAXIMUM RTT
    - MINIMUM RTT
    - AVERAGE RTT
    - PACKET LOSS PERCENT
TCP Modified_Server:
1. Start running the server,then starts running on multiple clients , it will establish a connection
2. enter no. of pings in multiple clients then it starts sending the ping messages and outputs RTTs min,avg,Max and packet loss rate

TCP_PINGER_ICMP_ERROR_SERVER: 
 - The server listens for TCP connections on port 12001 and, upon accepting a connection, 
 - generates a random number, If the number is greater than 8, it simulates an ICMP "Port Unreachable" error and sends it to the client. 
 - Otherwise, the server sends a normal "Hello, client" TCP response.

TCP_PINGER_ICMP_ERROR_CLIENT:
 - TCP Requests: The client sends TCP connection requests to a server on a specified IP and port. It receives a response or handles connection timeouts/refusals.
 - ICMP Error Handling: If a connection fails due to network issues, the client listens for ICMP "Destination Unreachable" messages (like Port Unreachable) and prints relevant errors.
 - Loop and Retry: The process repeats for a specified number of requests, waiting 1 second between each attempt, handling errors and responses accordingly.

## Error Handling
If timeout occurs, print the timeout message by catching a timeout exception and increment the packet loss count


# ICMP PINGER

The ICMP client script is designed to perform network diagnostics by sending ICMP echo requests and measuring the response time. It begins by creating raw sockets to handle ICMP packets and constructs an echo request packet with a calculated checksum. This packet is sent to the target host, and the script then waits for an ICMP echo reply. Upon receiving a reply, it calculates the round-trip time (RTT) by comparing the time of sending and receiving the packet. The script also handles ICMP error messages, such as "Destination Unreachable," to detect and report network issues. After a series of pings, the script summarizes the results, providing statistics on minimum, maximum, and average RTT, as well as packet loss, to assess network performance and connectivity.

# FILES
icmp_code: <put file name here>

# HOW TO RUN
python3 <putfilename.py>


# HOW IT WORKS

* Sending Pings: The sendOnePing function constructs and sends an ICMP echo request (ping) to the specified destination. It includes a checksum for error-checking.

* Receiving Responses: The receiveOnePing function waits for an ICMP echo reply. It extracts and processes the reply to measure the round-trip time (RTT). It also handles ICMP error messages like "Destination Unreachable."

* Statistics Collection: The ping function repeatedly sends pings and collects RTT data. It calculates minimum, maximum, and average RTT, as well as packet loss statistics, and prints the results.

# LICENSE
This project is licensed under the MIT License. See the LICENSE file for details.
```
This `README.md` provides a complete overview, usage instructions, and example output for your UDP ping client script, including a detailed breakdown of the script’s components and instructions on how to update and run the code. Adjust any sections that need further customization based on your specific environment or requirements!
```