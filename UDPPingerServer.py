
import random          # importing random to generate the random numbers
from socket import *   #importing fucntions and constants from the socket module

serverSocket = socket(AF_INET, SOCK_DGRAM)   #creating UDP socket

# Assign IP address and port number to socket
serverSocket.bind(('', 11000))       # binding socket to the IP address
print("Server is ready to receive pings...")   #printing message server is ready  

while True:
    # Generate a random number between 1 to 10 (both inclusive)
    rand = random.randint(1, 10)
   
    # Receive the client packet along with the address it is coming from
    message, address = serverSocket.recvfrom(1024)
   
    # Capitalize the message from the client
    message = message.upper()
   
    print(f"Received message: {message.decode()} from {address}, Random value: {rand}") # print the recieved message, client adrress
   
    # If rand is greater than 8, we consider the packet lost and do not respond to the client
    if rand > 8:
        print("Simulating packet loss...") #print the packet loss message
        continue                              
   
    # Otherwise, send the response back to the client
    serverSocket.sendto(message, address)
    print("Responding to the client...") #print the responding message
