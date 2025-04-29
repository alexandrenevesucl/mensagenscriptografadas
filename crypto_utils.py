# Funções de criptografia

from cryptography.fernet import Fernet

# Chave fixa (no projeto real, salve isso com segurança)
key = Fernet.generate_key()
cipher = Fernet(key)

def encrypt_message(message):
    return cipher.encrypt(message.encode()).decode()

def decrypt_message(token):
    return cipher.decrypt(token.encode()).decode()
