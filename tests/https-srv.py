from http.server import HTTPServer, SimpleHTTPRequestHandler
import ssl
import os.path

DIR_HERE=os.path.normpath(os.path.abspath(os.path.dirname(__file__)))
MY_KEY_FILE = os.path.join(DIR_HERE, 'my-key.pem')
MY_CERT_FILE = os.path.join(DIR_HERE, 'my-cert.pem')

httpd = HTTPServer(('localhost', 8080), SimpleHTTPRequestHandler)
httpd.socket = ssl.wrap_socket (httpd.socket, keyfile=MY_KEY_FILE, certfile=MY_CERT_FILE, server_side=True)
httpd.serve_forever()
