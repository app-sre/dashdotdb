import logging
import uuid


LOG = logging.getLogger('dashdotdb')


def gen_access_token():
    access_token = str(uuid.uuid4())
    LOG.warning('Access token: %s', access_token)
    return access_token
