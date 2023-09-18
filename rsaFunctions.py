import math
import random
import os
import io
import PIL.Image as Image

def encrypt(pubKey, message, tcp_socket):
    encrypted = ""
    for c in message:
        encrypted += "{0:04x}".format(apply_key(pubKey, ord(c)))
    size = encrypted.encode().__sizeof__()
    tcp_socket.send(encrypted.encode())
    tcp_socket.send(b'\r\n')
        
def encryptPass(pubKey,password, tcp_socket):
    padded = str(password).zfill(20)
    encrypted = ""
    for c in padded:
        encrypted += "{0:04x}".format(apply_key(pubKey, ord(c)))
    tcp_socket.sendall(encrypted.encode())
    
def readimage(path):
    count = os.stat(path).st_size / 2
    with open(path, "rb") as f:
        return bytearray(f.read())
    
def decrypt(priv,byte):
    message = byte.decode('ASCII')
    decrypted = ""
    for i in range(0, len(message), 4):
        enc_string = message[i: i + 4]
        enc = int(enc_string, 16)
        dec = apply_key(priv, enc)
        if dec >= 0 and dec < 256:
            decrypted += chr(dec)
        else:
            print("Warning: Could not decode encrypted entity: " + enc_string)
            print("         decrypted as: " +
                    str(dec) + " which is out of range.")
            print("         inserting _ at position of this character")
            message += "_"
    return decrypted

def sendKey(c):
    key_pair = create_keys()
    e,d,n = key_pair
    pub = get_public_key(key_pair)
    e,n = pub
    #send modulus
    m = (n.bit_length() + 7) // 8
    mb = int.to_bytes(m,2,'big')
    c.send(mb)
    c.send(int.to_bytes(n,m,'big'))
    c.send(b'\r\n')
    #send e
    m = (e.bit_length() + 7) // 8
    mb = int.to_bytes(m, 2, 'big')
    c.send(mb)
    c.send(int.to_bytes(e,m,"big"))
    c.send(b'\r\n')
    
    return get_private_key(key_pair)

def recvKey(tcp_socket):
        #receive public mod
    m = tcp_socket.recv(2)
    D = tcp_socket.recv(int.from_bytes(m,'big'))
    n = int.from_bytes(D,'big')
    CRLF = tcp_socket.recv(2)

        #receive e
    m = tcp_socket.recv(2)
    D = tcp_socket.recv(int.from_bytes(m, 'big'))
    e = int.from_bytes(D, 'big')
    CRLF = tcp_socket.recv(2)
    
    return (e,n)

def get_public_key(key_pair):
    """
    Pulls the public key out of the tuple structure created by
    create_keys()

    :param key_pair: (e,d,n)
    :return: (e,n)
    """
    return (key_pair[0], key_pair[2])


def get_private_key(key_pair):
    """
    Pulls the private key out of the tuple structure created by
    create_keys()

    :param key_pair: (e,d,n)
    :return: (d,n)
    """
    return (key_pair[1], key_pair[2])
def create_keys():
    """
    Create the public and private keys.

    :return: the keys as a three-tuple: (e,d,n)
    """

    primes = generate_primes(100, 254)
    p = random.choice(primes)
    q = random.choice(primes)
    n = p * q
    lcm = math.lcm((p - 1), (q - 1))
    done = False
    d= 1
    while not done:
        if (e * d) % lcm == 1:
            done = True
        else: d = d + 1
    return e, d, n


def apply_key(key, m):
    """
    Apply the key, given as a tuple (e,n) or (d,n) to the message.

    This can be used both for encryption and decryption.

    :param tuple key: (e,n) or (d,n)
    :param int m: the message as a number 1 < m < n (roughly)
    :return: the message with the key applied. For example,
             if given the public key and a message, encrypts the message
             and returns the ciphertext.
    """
    a, n = key
    return pow(m,a) % n

def generate_primes(l, h):
    assert l >= 1
    assert h > l
    primes = []
    for x in range(l, h + 1):
        prime = True
        for y in range(2, x):
            if x % y == 0:
                prime = False
                break
        if prime:
            primes.append(x)
    return primes

primes = generate_primes(100, 254)

e = 17
p = random.choice(primes)
while math.gcd(p - 1, e) != 1:
    p = random.choice(primes)