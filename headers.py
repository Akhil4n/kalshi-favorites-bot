import base64
import datetime
import configparser
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

def get_headers(path, method):
    def load_private_key_from_file(file_path):
        with open(file_path, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )
        return private_key

    def sign_pss_text(private_key: rsa.RSAPrivateKey, text: str) -> str:
        message = text.encode('utf-8')
        try:
            signature = private_key.sign(
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.DIGEST_LENGTH
                ),
                hashes.SHA256()
            )
            return base64.b64encode(signature).decode('utf-8')
        except InvalidSignature as e:
            raise ValueError("RSA sign PSS failed") from e

    current_time = datetime.datetime.now()
    timestamp = current_time.timestamp()
    current_time_milliseconds = int(timestamp * 1000)
    timestampt_str = str(current_time_milliseconds)

    private_key = load_private_key_from_file('kalshi.key')

    # Load API Key from config
    config = configparser.ConfigParser()
    config.read('kalshi.cfg')
    access_key = config.get('kalshi', 'access_key')

    # Strip query parameters from path before signing
    path_without_query = path.split('?')[0]
    msg_string = timestampt_str + method + path_without_query
    sig = sign_pss_text(private_key, msg_string)

    return {
        'KALSHI-ACCESS-KEY': access_key,
        'KALSHI-ACCESS-SIGNATURE': sig,
        'KALSHI-ACCESS-TIMESTAMP': timestampt_str
    }
