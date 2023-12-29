import base64
from cryptography.fernet import Fernet

# all encrypt functions point here
def _encrypt_(key, data) -> bytes:
  if not type(data) is bytes:
    data = str(data).encode('utf-8')
  return Fernet(key).encrypt(data)


# all decrypt functions point here
def _decrypt_(key, data) -> str:
  data = Fernet(key).decrypt(data)
  return data.decode('utf-8')


def toBase64String(data) -> str: 
  return base64.b64encode(data).decode('utf-8')


def fromBase64String(base64string) -> bytes:
  return base64.b64decode(base64string.encode('utf-8'))


def generateKey() -> bytes:
  return Fernet.generate_key()


def generateKeyAsBase64() -> str:
  return toBase64String(generateKey())


def encryptWithKey(key, data) -> bytes:
  return _encrypt_(key, data)


def encryptWithKeyToBase64(key, data) -> str:
  return toBase64String(encryptWithKey(key, data))


def encrypt(data):
  key = generateKey()
  result = lambda:0
  result.key = key
  result.data = encryptWithKey(key, data)
  return result


def encryptToBase64(data):
  result = encrypt(data)
  result.key = toBase64String(result.key)
  result.data = toBase64String(result.data)
  return result


def decryptWithKey(key, data) -> str:
  return _decrypt_(key, data)


def decryptWithKeyFromBase64(base64key, base64data) -> str:
  return decryptWithKey(fromBase64String(base64key), fromBase64String(base64data))
