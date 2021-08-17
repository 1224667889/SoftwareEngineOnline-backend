import uuid
import random
import re


def create_uuid():
    return uuid.uuid5(uuid.NAMESPACE_DNS, str(uuid.uuid1()) + str(random.random()))


def check_password(pwd):
    pattern = re.compile(r'^[A-Za-z\d$@$!%*?&.]{6,18}')
    if pattern.findall(pwd):
        return True
    return False
