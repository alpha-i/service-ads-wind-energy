from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, URLSafeTimedSerializer)

from config import SECRET_KEY
from core.models.customer import User


def generate_auth_token(user, expiration=3600):
    s = Serializer(SECRET_KEY, expires_in=expiration)
    return s.dumps({'id': user.id})


def verify_token(token):
    user = User.verify_auth_token(token)
    return user


def get_by_email(email):
    user = User.get_user_by_email(email)
    return user


def verify_password(user: User, password: str):
    return user.verify_password(password)


def insert(user: User):
    user.save()
    return user


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    return serializer.dumps(email)


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    try:
        email = serializer.loads(token, max_age=expiration)
    except:
        return False
    return email


def confirm(user):
    user.confirmed = True
    user.save()
    return user
