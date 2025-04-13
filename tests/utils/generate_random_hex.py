import secrets

def generate_random_hex() -> str:
    return "0033" + secrets.token_hex(22)