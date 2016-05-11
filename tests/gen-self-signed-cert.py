import os.path
import subprocess

DIR_HERE=os.path.normpath(os.path.abspath(os.path.dirname(__file__)))
OPENSSL_TOOL = os.path.normpath(os.path.join(DIR_HERE, '../bin/openssl'))

if not os.path.isfile(OPENSSL_TOOL):
   raise Exception("file not found: '{}'".format(OPENSSL_TOOL))

LOCAL_OPENSSL_CONFIG = os.path.join(DIR_HERE, 'my-openssl.cnf')

print("Generating custom config for openssl tool ...")
with open(LOCAL_OPENSSL_CONFIG, mode='wt') as my_openssl_cnf:
    my_openssl_cnf.writelines(
"""
[req]
encrypt_key        = no
distinguished_name = req_distinguished_name
[ req_distinguished_name ]
""")

print("Generating self-signed cerificate ...")

gen_cert_argv = [OPENSSL_TOOL, 'req','-config', LOCAL_OPENSSL_CONFIG, '-x509', '-newkey', 'rsa:2048',
    '-keyout', os.path.join(DIR_HERE, 'my-key.pem'),
    '-out', os.path.join(DIR_HERE, 'my-cert.pem'),
    '-days', '365', '-subj', '/CN=localhost.localdomain']
subprocess.check_call(gen_cert_argv)
