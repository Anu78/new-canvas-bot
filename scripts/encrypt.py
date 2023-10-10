from cryptography.fernet import Fernet
import os
import ctypes
import db


class Encrypt():
    def __init__(self):
        return
    class SecureKeyContext:
        def __init__(self, key):
            self.key = key

        def __enter(self):
            return Fernet(self.key)

        def __exit__(self, exc_type, exc_value, traceback):
            self.key = None
            libc = ctypes.CDLL(None)
            libc.free(self.key)

    class Encrypt:
        def __init__(self):
            self.key = os.getenv("ENCRYPTION_KEY")

            if self.key is None:
                raise ValueError("Encryption key was not found in the environment variable. ")

        def encrypt(self, phrase):
            with self.SecureKeyContext(self.key.encode()) as cipher_suite:
                return cipher_suite.encrypt(phrase.encode())

        def decrypt(self, phrase):
            with self.SecureKeyContext(self.key.encode()) as cipher_suite:
                return cipher_suite.decrypt(phrase).decode()