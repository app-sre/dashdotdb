from datetime import datetime
from uuid import uuid4

from dashdotdb.models.dashdotdb import db
from dashdotdb.models.dashdotdb import Token
from dashdotdb.models.dashdotdb import LatestTokens
from dashdotdb.services import DataTypes

from connexion.exceptions import OAuthProblem


TOKEN_CLOSED_CODE = 400
TOKEN_CLOSED_MSG = 'token is closed for data'
TOKEN_NOT_FOUND_CODE = 404
TOKEN_NOT_FOUND_MSG = 'token not found'
TOKEN_UNKNOWN_SCOPE_CODE = 405
TOKEN_UNKNOWN_SCOPE_MSG = 'unknown scope'

scope_to_data_type = {
    "imagemanifestvuln": DataTypes.CSODataType,
    "deploymentvalidation": DataTypes.DVODataType,
    "serviceslometrics": DataTypes.SLODataType
}


def auth_token(token, required_scopes):
    db_token = db.session.query(Token) \
        .filter(Token.uuid == token).first()
    if not db_token:
        raise OAuthProblem(TOKEN_NOT_FOUND_MSG)

    if not db_token.is_open:
        raise OAuthProblem(TOKEN_CLOSED_MSG)

    return {'sub': db_token.uuid}


def delete(token, scope):
    if scope not in scope_to_data_type:
        return TOKEN_UNKNOWN_SCOPE_MSG, TOKEN_UNKNOWN_SCOPE_CODE
    data_type = scope_to_data_type[scope]

    with db.session.begin():
        db_token = db.session.query(Token) \
            .filter(Token.uuid == token, Token.data_type == data_type).first()
        if db_token is None:
            return TOKEN_NOT_FOUND_MSG, TOKEN_NOT_FOUND_CODE
        if not db_token.is_open:
            return TOKEN_CLOSED_MSG, TOKEN_CLOSED_CODE
        db_token.is_open = False
        latest_token = db.session.query(LatestTokens) \
            .filter(Token.data_type == data_type,
                    Token.id == LatestTokens.token_id).first()
        if latest_token is None:
            db.session.add(LatestTokens(token_id=db_token.id))
        else:
            # only update the latest token if the creation timestamp is newer than
            # the current latest token creation timestamp
            latest_token_data = db.session.query(
                Token).filter(Token.id == latest_token.token_id).first()
            if db_token.timestamp > latest_token_data.timestamp:
                latest_token.token_id = db_token.id
    return 'token closed'


def search(scope):
    if scope not in scope_to_data_type:
        return TOKEN_UNKNOWN_SCOPE_MSG, TOKEN_UNKNOWN_SCOPE_CODE
    data_type = scope_to_data_type[scope]

    # generate a unique id
    uuid = str(uuid4())

    # store the token information so we can validate requests via token uuid
    db.session.add(Token(uuid=uuid, data_type=data_type,
                         timestamp=datetime.now(),
                         is_open=True))
    db.session.commit()
    return uuid
