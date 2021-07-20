from datetime import datetime
from uuid import uuid4

from dashdotdb.models.dashdotdb import db
from dashdotdb.models.dashdotdb import Token
from dashdotdb.models.dashdotdb import LatestTokens


def close_token(uuid, data_type):
    db_token = db.session.query(Token) \
        .filter(Token.uuid == uuid, Token.data_type == data_type).first()
    if db_token is None:
        return 'token not found', 404
    db_token.is_open = False
    latest_token = db.session.query(LatestTokens) \
        .filter(Token.data_type == data_type,
                Token.id == LatestTokens.token_id).first()
    if latest_token is None:
        db.session.add(LatestTokens(token_id=db_token.id))
    else:
        # Only update the latest token if the creation timestamp is newer than
        # the current latest token creation timestamp
        latest_token_data = db.session.query(
            Token).filter(Token.id == latest_token.token_id).first()
        if db_token.timestamp > latest_token_data.timestamp:
            latest_token.token_id = db_token.id
    db.session.commit()
    return 'token closed'


def generate_token(data_type):
    # generate a unique id
    uuid = str(uuid4())
    db_token = db.session.query(Token) \
        .filter(Token.uuid == uuid).first()
    if db_token is None:
        db.session.add(Token(uuid=uuid, data_type=data_type,
                             timestamp=datetime.now(),
                             is_open=True))
        db.session.commit()
        return uuid
    return 'token collision', 500
