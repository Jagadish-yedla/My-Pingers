
#import random         # importing random to generate the random numbers
from socket import *   #importing fucntions and constants from the socket module

serverSocket = socket(AF_INET, SOCK_DGRAM)   #creating UDP socket

# Assign IP address and port number to socket
serverSocket.bind(('', 11000))       # binding socket to the IP address
print("Server is ready to receive pings...")   #printing message server is ready  

while True:

    message, address = serverSocket.recvfrom(1024)
   
    # Capitalize the message from the client
    message = message.upper()
   
    print(f"Received message: {message.decode()} from {address}") # print the recieved message, client adrress
   
   # send the response back to the client
    serverSocket.sendto(message, address)
    print("Responding to the client...") #print the responding message
