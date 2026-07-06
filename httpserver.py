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
   
    def start_response(self, status, response_headers, exc_info=None):
        # Add necessary server headers
        server_headers = [
            ('Date', 'Sun, 05 Jul 2026 5:54:48 GMT'),
            ('Server', 'WSGIServer 0.2'),
        ]
        self.headers_set = [status, response_headers + server_headers]

    
    def send_response(self, result):
        status, response_headers = self.headers_set
        response = f'HTTP/1.1 {status}\r\n'
        for header in response_headers:
            response += '{0}: {1}\r\n'.format(*header)
            response += '\r\n'
        for data in result:
            response += data.decode('utf-8')
        return response
    
    def serve_forever(self):
        listen_socket = self.listen_socket
        while True:
     
            self.client_connection, _ = listen_socket.accept()
            self.request_data = self.client_connection.recv(1024).decode()
            request_line = self.parse_data(self.request_data)
            (self.request_method,  # GET
            self.path,            # /hello
            self.request_version  # HTTP/1.1
            ) = request_line.split()

            env = self.get_environ()
            result = self.application(env, self.start_response)
            try:
                response=self.send_response(result)
                response_bytes = response.encode()
                self.client_connection.sendall(response_bytes)
            finally:
                self.client_connection.close()

    def parse_data(self, request_data: str):
        request_line = self.request_data.splitlines()[0]
        request_line = request_line.rstrip('\r\n')
        return request_line
    

    def get_environ(self):
        env = {}
        # Required WSGI variables
        env['wsgi.version']      = (1, 0)
        env['wsgi.url_scheme']   = 'http'
        env['wsgi.input']        = io.StringIO(self.request_data)
        env['wsgi.errors']       = sys.stderr
        env['wsgi.multithread']  = False
        env['wsgi.multiprocess'] = False
        env['wsgi.run_once']     = False
        # Required CGI variables
        env['REQUEST_METHOD']    = self.request_method    # GET
        env['PATH_INFO']         = self.path              # /hello
        env['SERVER_NAME']       = self.server_name       # localhost
        env['SERVER_PORT']       = str(self.server_port)  # 8888
        return env

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