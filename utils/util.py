import uuid
import random
import re
from config import allowed_documents


def create_uuid():
    return uuid.uuid5(uuid.NAMESPACE_DNS, str(uuid.uuid1()) + str(random.random()))


def check_password(pwd):
    pattern = re.compile(r'^[A-Za-z\d$@$!%*?&.]{6,18}')
    if pattern.findall(pwd):
        return True
    return False


def create_safe_name():
    return str(uuid.uuid5(uuid.NAMESPACE_X500, str(uuid.uuid1()) + str(random.random())))


def allow_document(suffix: str):
    if suffix.lower() in allowed_documents:
        return True
    return False
