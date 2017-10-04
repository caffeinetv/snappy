import string
import random

def rnd_str(length, choices=string.ascii_letters + string.digits):
    return ''.join(random.choice(choices) for i in range(length))