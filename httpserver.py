"""
 Implements a simple HTTP/1.0 Server

"""

import socket
import io
import sys
class WSGIServer(object):

    def __init__(self, server_address):
        # Define socket host and port
        SERVER_HOST = '0.0.0.0'
        SERVER_PORT = 8888

        # Create socket:
        self.listen_socket = listen_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listen_socket.bind((SERVER_HOST, SERVER_PORT))
        listen_socket.listen(1)
        print('Listening on port %s ...' % SERVER_PORT)
        host, port = self.listen_socket.getsockname()[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port
        # Return headers set by Web framework/Web application
        self.headers_set = []

    def set_app(self, application):
        self.application = application
   
    def serve_forever(self):
        listen_socket = self.listen_socket
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
            #   Send HTTP response
    
            client_connection.sendall(response.encode())
            # Close socket
            client_connection.close()

def make_server(server_address, application):
    server = WSGIServer(server_address)
    server.set_app(application)
    return server

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Provide a WSGI application object as module:callable')
    app_path = sys.argv[1]
    module, application = app_path.split(':')
    module = __import__(module)
    application = getattr(module, application)
    httpd = make_server(('', 8888), application)
    print('WSGIServer: Serving HTTP on port  ...\n')
    httpd.serve_forever()