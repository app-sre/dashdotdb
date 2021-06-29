import datetime

from uuid import uuid4

from dashdotdb.models.dashdotdb import db
from dashdotdb.models.dashdotdb import Tokens
from dashdotdb.models.dashdotdb import LatestTokens


def close_token(uuid, data_type):
    db_token = db.session.query(Tokens) \
        .filter(Tokens.uuid == uuid, Tokens.data_type == data_type).first()
    if db_token is None:
        return 'token not found', 404
    db.session.update(Tokens).where(
        Tokens.id == db_token.id).values(is_open=False)
    latest_token = db.session.query(LatestTokens) \
        .filter(Tokens.data_type == data_type).first()
    if latest_token is None:
        db.session.add(LatestTokens(data_type=data_type, token_id=db_token.id))
    else:
        # Only update the latest token if the creation timestamp is newer than
        # the current latest token creation timestamp
        latest_token_data = db.session.query(
            Tokens).filter(Tokens.id == latest_token.id)
        if db_token.creation_timestamp > latest_token_data.createion_timestamp:
            db.session.update(LatestTokens).where(
                data_type=data_type).values(token_id=db_token.id)
    db.session.commit()
    return 'token closed'


def generate_token(data_type):
    # generate a unique id
    uuid = str(uuid4())
    db_token = db.session.query(Tokens) \
        .filter(Tokens.uuid == uuid).first()
    if db_token is None:
        db.session.add(Tokens(uuid=uuid, data_type=data_type,
                              creation_timestamp=datetime.now(),
                              is_open=True))
        db.session.commit()
        return uuid
    return 'token collision', 500
