from cryptography.fernet import Fernet
key = Fernet.generate_key()
f = Fernet(key)
token = f.encrypt(b"my deep dark secret")
print("* ENCRYPTED *")
print(token)
print("* DECRYPTED *")
print(f.decrypt(token))
