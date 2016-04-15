import socket
import ssl
import pprint
import os.path

HOST = 'www.openssl.org'

DIR_HERE = os.path.normpath(os.path.abspath(os.path.dirname(__file__)))
CERT_FILE = os.path.join(DIR_HERE, 'certdata.pem')

if not os.path.isfile(CERT_FILE):
    raise Exception("Required file '{}' not found.".format(CERT_FILE))

ctx = ssl.create_default_context(cafile=CERT_FILE)
conn = ctx.wrap_socket(socket.socket(socket.AF_INET), server_hostname=HOST)
conn.connect((HOST, 443))
cert = conn.getpeercert()
pprint.pprint(cert)
