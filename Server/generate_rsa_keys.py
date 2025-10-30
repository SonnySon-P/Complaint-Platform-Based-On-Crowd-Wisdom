from cryptography.hazmat.primitives.asymmetric import rsa

def run_generate_rsa_keys_task():
    private_key = rsa.generate_private_key(
        public_exponent = 65537,
        key_size = 2048
    )

    public_key = private_key.public_key()

    return private_key, public_key