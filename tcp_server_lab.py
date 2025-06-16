import socket


bal=0
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)     
server.bind(('127.0.0.1', 12000))                                                       

server.listen(1)
print(f'server is listening....')       

def handle_client(connection):
    global bal
    while True:
        data = connection.recv(1024).decode()
        if not data:
            break
        
        parts = data.split(",")
        command = parts[0].strip()
        if command == "Deposit":
            try:
                amount = float(parts[1].strip())
                if amount > 0:
                    bal += amount
                    response = f"{amount} deposited. Total balance: {bal}"
                else:
                    response = "Deposit amount must be positive."
            except ValueError:
                response = "Invalid amount format."
        elif command == "Withdrawal":
            try:
                amount = float(parts[1].strip())
                if amount>0:
                    if bal-amount>0:
                        bal-=amount
                        response = f"{amount} withdrawn, Total balance: {bal}"
                    else:
                        response = "you don't have that much amount to withdraw..."
                else :
                    response = "withdrawing amount must be postive"
            except ValueError:
                response = "Invalid amount format"

        elif command == "Check":
            response = f"Total balance: {bal}"
       
        else:
            response = "Unknown command."
       
        connection.sendall(response.encode())
   
    connection.close()

while True:
    client, client_address = server.accept()
    print(f"Client connected from {client_address}")
    handle_client(client)
                              