from http.server import BaseHTTPRequestHandler, HTTPServer
from ssl import SSLContext, PROTOCOL_TLS_SERVER
import requests

port = 443
api_port = 8443

class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    close_connection = True

    def do_POST(self):
        host = self.headers.get('Host')
        host = host.split(':')[0] + ':' + str(api_port)
        url = f'https://{host}{self.path}'
        content_len = int(self.headers.get('Content-Length'))
        req_body = self.rfile.read(content_len)

        incomplete = True
        while incomplete:
            resp = requests.post(url, headers=self.headers,
                                 data=req_body, verify=False)
            content_len = resp.headers['Content-Length']
            if len(resp.content) == int(content_len):
                incomplete = False

        self.send_response(resp.status_code)
        for h in resp.headers:
            if h not in ['Server', 'Date']:
                self.send_header(h, resp.headers[h])
        self.send_header('Connection', 'close')
        self.end_headers()
        self.wfile.write(resp.content)

def start(port):
    server_address = ('', port)
    httpd = HTTPServer(server_address, ProxyHTTPRequestHandler)
    certfile = '../key/api.crt'
    keyfile = '../key/api.key'
    context = SSLContext(PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile, keyfile)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    # uncomment to debug SSL errors
##    httpd.socket.accept()

    print(f'Reverse proxy is running on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    start(port)
