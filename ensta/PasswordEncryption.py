import time
import base64
from requests import Session
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import AES, PKCS1_v1_5
from Cryptodome.Random import get_random_bytes


class PasswordEncryption:

    request_session: Session = None

    def __init__(self, request_session: Session):
        self.request_session = request_session

    def encrypt(self, password: str) -> str:
        public_key, public_key_id = self.__public_keys()
        session_key = get_random_bytes(32)
        iv = get_random_bytes(12)
        timestamp = str(int(time.time()))
        decoded_public_key = base64.b64decode(public_key.encode())
        recipient_key = RSA.importKey(decoded_public_key)
        cipher_rsa = PKCS1_v1_5.new(recipient_key)
        rsa_encrypted = cipher_rsa.encrypt(session_key)
        cipher_aes = AES.new(session_key, AES.MODE_GCM, iv)
        cipher_aes.update(timestamp.encode())
        aes_encrypted, tag = cipher_aes.encrypt_and_digest(password.encode("utf8"))
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
