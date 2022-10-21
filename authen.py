# authen.py
# provides simple HMAC signatures of data

import hmac
import json 


TESTKEY1 = "development key"


def getHMAC(data, key):
    """Accepts arbitrary data (including dict). Returns hmac as string.
    
    See: https://stackoverflow.com/questions/5884066/hashing-a-dictionary
    We can stably sign dict data by serializing first with json.dumps()
    """
    hmac_instance = hmac.new(bytes(key, 'utf-8'), digestmod='sha256')
    frozen = json.dumps(data, sort_keys=True)
    hmac_instance.update(bytes(frozen, 'utf-8'))
    return hmac_instance.hexdigest()


def checkHMAC(userdata, userHMAC, key):
    """Checks whether the provided user data matches the provided hmac. Return bool."""
    calcHMAC = getHMAC(userdata, key)
    return hmac.compare_digest(userHMAC, calcHMAC)
