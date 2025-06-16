import socket   

server_address = ('127.0.0.1',12000)                     
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   #creating the tcp socket
client.connect(server_address)                               #connecting client to server
 

while True:
    query = input("Enter command (Deposit, Withdrawal, Check) or 'exit' to quit: ")
    if query.lower() == 'exit':
        break
   
    if query.startswith('Deposit') or query.startswith('Withdrawal'):
        try:
            parts = query.split()
            command = parts[0]
            amount = float(parts[1])
            query = f"{command}, {amount}"
        
        except (IndexError, ValueError):
            print("Invalid format.")
            continue
    elif query=="Check" :
        query = "Check"
        
    else :
        print("unknown command")
        continue

    client.sendall(query.encode())
    response = client.recv(1024).decode()
    print(response)

client.close()              
