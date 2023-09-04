import string
import random


def generate_unique_token(length=16):
    characters = string.ascii_letters + string.digits
    token = "".join(random.choices(characters, k=length))
    return token
