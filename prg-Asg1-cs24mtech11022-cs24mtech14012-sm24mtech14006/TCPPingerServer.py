import socket      #importing socket for network communication
import random      #importing random to generate the random numbers

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)     #creating tcp socket
server.bind(('', 12000))                                       #binding socket to the IP address

server.listen(4)                                               #listens for incoming connection with queue upto 4

print('TCP_Pingserver is listening now ... ')                   

while True:
    client_socket, client_address = server.accept()           #accepting the incoming connection 

    print(f'Connected to {client_address}')                   #printing the client address

    while True:                                               #hadnle connection with clients
        data = client_socket.recv(1024)                       #recieve the data from client
 
        if not data:                                          #if no data recieved from the client side loop will break 
            break         
        random_integer = random.randint(1, 10)                
        print(f"Received packet: {data.decode()}")
        if random_integer >= 8:                               #randome int greater than or equal to 3 respond to client
            upper_data = data.upper()
            client_socket.send(upper_data)

            print(f"Sent response: {upper_data.decode()}")
        else:
            print(f"Packet lost (no response)")

    # Close the client socket
    client_socket.close()                                     #close the client socket