"""
 Implements a simple HTTP/1.0 Server

"""

import socket


# Define socket host and port
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8000

# Create socket:
listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind((SERVER_HOST, SERVER_PORT))
listen_socket.listen(1)
print('Listening on port %s ...' % SERVER_PORT)

while True:
    # Wait for client connections
    client_connection, client_address = listen_socket.accept()

    # Get the client request
    request_data = client_connection.recv(1024).decode()
    print(request_data)

# Parse HTTP headers
    headers = request_data.split('\n')
    filename = headers[0].split()[1]

    # Get the content of the file
    if filename == '/':
        filename = '/index.html'
    try:
        fin = open('htdocs' + filename)
        content = fin.read()
        fin.close()
        response = 'HTTP/1.0 200 OK\n\n' + content
        
    except FileNotFoundError:
        response = 'HTTP/1.0 404 NOT FOUND\n\nFile Not Found'
    # Send HTTP response
    
    client_connection.sendall(response.encode())
    # Close socket
    client_connection.close()


