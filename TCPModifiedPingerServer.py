import socket       #importing socket for network communication
import threading    #importing threading module for multiple clients
import random      #importing random to generate the random numbers


def handle_client(client_socket, client_address):   # Function to handle incoming client connections
    print(f"Connected to {client_address}")         #printing a client ip address
    while True:
        try:
            data = client_socket.recv(1024)         #Receive data(up to 1024 bytes) from the client
            if not data:                            #checking from client side data received or not
                print(f"Connection closed by {client_address}")     #no data recieved print connection is closed by client
                break

            # Log the received packet
            print(f"Received packet from {client_address}: {data.decode()}")

            
            random_integer = random.randint(1, 10)    # Simulate packet loss
            if random_integer >= 8:                   #if random number is greater than or equal to 3 successful tansmission
                upper_data = data.upper()
                client_socket.send(upper_data)        #sending modified data back to client
                print(f"Sent response to {client_address}: {upper_data.decode()}")  #printing the sent message 
            else:
                print(f"Packet lost (no response) to {client_address}")             #printing the packet loss message
        
        except ConnectionResetError:                          #client connection closed forcefully
            print(f"Connection reset by {client_address}") 
            break

    client_socket.close()       #close the client socket

# Main server function
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   #creating tcp socket 
    server.bind(('', 12000))                                     #binding socket to the IP address
    server.listen(5)                                             # Listen for up to 5 connections
    print('TCP Ping server is listening on port 12000...')       

    while True:
        client_socket, client_address = server.accept()         #waiting for incoming client connection and accepting that connection

        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))  # Creating new thread to handle the client
        client_thread.start()           #client hadnling thread for concurrent client

if __name__ == "__main__":
    start_server()