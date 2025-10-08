from nacl.public import PrivateKey, PublicKey, Box
from nacl.encoding import Base64Encoder
from nacl.exceptions import CryptoError

class Encryption:
    @staticmethod
    def generate_keypair():
        """
        Generates a new public/private key pair.
        Returns base64 encoded keys as strings.
        """
        private_key = PrivateKey.generate()
        public_key = private_key.public_key
        return (
            private_key.encode(encoder=Base64Encoder).decode('utf-8'),
            public_key.encode(encoder=Base64Encoder).decode('utf-8')
        )

    @staticmethod
    def encrypt_message(message: str, sender_private_key_b64: str, recipient_public_key_b64: str) -> str:
        """
        Encrypts a message string using sender's private key and recipient's public key.
        Returns base64 encoded encrypted message.
        """
        sender_private_key = PrivateKey(sender_private_key_b64.encode('utf-8'), encoder=Base64Encoder)
        recipient_public_key = PublicKey(recipient_public_key_b64.encode('utf-8'), encoder=Base64Encoder)

        box = Box(sender_private_key, recipient_public_key)
        encrypted = box.encrypt(message.encode('utf-8'), encoder=Base64Encoder)
        return encrypted.decode('utf-8')

    @staticmethod
    def decrypt_message(encrypted_message_b64: str, recipient_private_key_b64: str, sender_public_key_b64: str) -> str:
        """
        Decrypts an encrypted message (base64 string) using recipient's private key and sender's public key.
        Returns decrypted plain text message.
        """
        recipient_private_key = PrivateKey(recipient_private_key_b64.encode('utf-8'), encoder=Base64Encoder)
        sender_public_key = PublicKey(sender_public_key_b64.encode('utf-8'), encoder=Base64Encoder)

        box = Box(recipient_private_key, sender_public_key)
        try:
            plaintext = box.decrypt(encrypted_message_b64.encode('utf-8'), encoder=Base64Encoder)
            return plaintext.decode('utf-8')
        except CryptoError:
            raise ValueError("Decryption failed. Invalid keys or corrupted message.")
