from cryptography.fernet import Fernet


class Encrypt:
    symmetricKey = ""
    x = None

    def GenerateSymetricKey(self):
        global x
        symmetricKey = Fernet.generate_key()
        x = Fernet(symmetricKey)
        return symmetricKey

    def addKey(self, key):
        global symmetricKey, x
        symmetricKey = key
        x = Fernet(symmetricKey)

    def encryptSym(self, str):
        global x
        return x.encrypt(str)

    def decryptSym(self, str):
        global x
        original = x.decrypt(str)
        return original

    private_key = None
    public_key = None

    def GenerateAsymmetric(self):
        global private_key, public_key
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives.asymmetric import rsa
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()

    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding

    def encryptAsymmetric(self, str, publicKey):
        encrypted = publicKey.encrypt(
            str,
            self.padding.OAEP(
                mgf=self.padding.MGF1(algorithm=self.hashes.SHA256()),
                algorithm=self.hashes.SHA256(),
                label=None
            )
        )
        return encrypted

    def decryptAssymetric(self, encrypted):
        original_message = private_key.decrypt(
            encrypted,
            self.padding.OAEP(
                mgf=self.padding.MGF1(algorithm=self.hashes.SHA256()),
                algorithm=self.hashes.SHA256(),
                label=None
            )
        )
        return original_message

    def getPublicKey(self):
        global public_key

        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.backends import default_backend

        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        # print(pem)
        return pem

    def getOppPublicKey(self, key):
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.backends import default_backend
        public_key = serialization.load_pem_public_key(
            key,
            backend=default_backend()
        )
        return public_key

# en = Encrypt()
# en.GenerateAsymmetric()
# en.getPublicKey()
