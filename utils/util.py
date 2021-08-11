import uuid
import random


def create_uuid():
    return uuid.uuid5(uuid.NAMESPACE_DNS, str(uuid.uuid1()) + str(random.random()))
