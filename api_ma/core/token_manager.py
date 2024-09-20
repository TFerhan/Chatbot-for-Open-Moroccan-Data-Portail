# token_manager.py
current_valid_token = {}
cipher_suite = None


def get_current_valid_token():
    return current_valid_token

def update_current_valid_token(new_tokens):
    global current_valid_token
    current_valid_token = new_tokens


def get_cipher_suite():
    return cipher_suite

def update_cipher_suite(new_cipher_suite):
    global cipher_suite
    cipher_suite = new_cipher_suite