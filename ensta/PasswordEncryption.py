import os
import time
import base64
from requests import Session
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class PasswordEncryption:

    request_session: Session = None

    def __init__(self, request_session: Session):
        self.request_session = request_session

    def encrypt(self, password: str) -> str:
        public_key, public_key_id = self.__public_keys()
        session_key = os.urandom(32)
        iv = os.urandom(12)
        timestamp = str(int(time.time()))
        decoded_public_key = base64.b64decode(public_key.encode())
        recipient_key = load_pem_public_key(decoded_public_key)
        rsa_encrypted = recipient_key.encrypt(session_key, padding.PKCS1v15())
        cipher_aes = Cipher(algorithms.AES(session_key), modes.GCM(iv)).encryptor()
        cipher_aes.authenticate_additional_data(timestamp.encode())
        aes_encrypted = cipher_aes.update(password.encode("utf8"))
        cipher_aes.finalize()
        tag = cipher_aes.tag
        size_buffer = len(rsa_encrypted).to_bytes(2, byteorder="little")

        payload = base64.b64encode(b"".join([
            b"\x01",
            public_key_id.to_bytes(1, byteorder="big"),
            iv,
            size_buffer,
            rsa_encrypted,
            tag,
            aes_encrypted
        ]))

        return f"#PWD_INSTAGRAM:4:{timestamp}:{payload.decode()}"

    def __public_keys(self) -> tuple[str, int]:
        response = self.request_session.get("https://i.instagram.com/api/v1/qe/sync/")

        public_key: str = response.headers.get("ig-set-password-encryption-pub-key")
        public_key_id: int = int(response.headers.get("ig-set-password-encryption-key-id"))

        return public_key, public_key_id
