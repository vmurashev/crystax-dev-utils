import socket
import ssl
import pprint
HOST = 'www.openssl.org'
ctx = ssl.create_default_context()
conn = ctx.wrap_socket(socket.socket(socket.AF_INET), server_hostname=HOST)
conn.connect((HOST, 443))
cert = conn.getpeercert()
pprint.pprint(cert)

