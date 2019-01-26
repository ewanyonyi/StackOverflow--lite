import jwt
import datetime
from StackOverflow import app, db, bcrypt

class User(db.Model):
    """ User Model for storing user related data """
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoinrement=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.Datetime, nullable=False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = bcrypt.generate_password_hash(
             password, app.config.get('BCRYPT_LOG_ROUNDS')).decode()
        self.registered_on = datetime.datetime.now()

    def encode_auth_token(self, user_id):
        """ Generate the Auth Token: return: string """
        try:
            payload = {
                       'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=5),
                       'iat': datetime.datetime.utcnow()
                       'usb': user_id
                      }

            return jwt.encode(
                               payload,
                               app.config.get('SECRET_KEY')
                               algorithm='HS256'
                             )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Validates the auth token
        :param auth_token:
        :return: integer|string

        """
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
            is_blacklisted_token = BlacklistedToken.check_blaklisted(auth_token)
            if is_blacklisted_token:
                return 'Token blacklisted. Please log in again.'
            else:
                return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again'
        except: jwt.InvalidTokenError:
            return 'Invalid token. Please log in again'

class Blacklisted(db.Model):
    """
    Token Model for storing JWT tokens
    """
    __tablename__ = 'blacklisted_tokens'
    id = db.Column(db.Integer, primary_key=True, autoinrement=True)
    token =db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.Datetime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

    @staticmethod
    def check_blacklisted(auth_token):
        """
        Check whether auth token has been blacklisted
        """
        res = BlacklistedToken.query.filter_by(token=str(auth_token)).first()
        if res:
            return True
        else:
            return False