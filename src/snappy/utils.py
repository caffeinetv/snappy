import string
import random
import base64

def rnd_str(length, choices=string.ascii_letters + string.digits):
    return ''.join(random.choice(choices) for i in range(length))

def base64_encode(b_value):
	return base64.b64encode(b_value).decode()

def base64_decode(bs64_value):
	return base64.b64decode(bs64_value)