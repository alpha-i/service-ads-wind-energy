import enum
import logging

from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired
)
from passlib.apps import custom_app_context as pwd_context
from sqlalchemy import (event, Column, String, JSON, ForeignKey, Boolean, Enum, UniqueConstraint)
from sqlalchemy.orm import relationship, validates
from sqlalchemy.orm.exc import NoResultFound

from config import SECRET_KEY
from core.database import db_session, local_session_scope
from core.models.base import BaseModel


class Actions(enum.Enum):
    FILE_UPLOAD = 'FILE_UPLOAD'
    DETECTION_STARTED = 'DETECTION_STARTED'
    CONFIGURATION_UPDATE = 'CONFIGURATION_UPDATE'


class UserPermissions(enum.Enum):
    USER = 'USER'
    ADMIN = 'ADMIN'


class Company(BaseModel):
    __tablename__ = 'company'

    INCLUDE_ATTRIBUTES = ('current_configuration', 'current_datasource', 'actions',
                          'detection_results', 'data_sources', 'detection_tasks')

    name = Column(String, nullable=False, unique=True)
    logo = Column(String)
    domain = Column(String, nullable=False)
    profile = Column(JSON)

    actions = relationship('CustomerAction', back_populates='company')
    configuration = relationship('CompanyConfiguration', back_populates='company',
                                 order_by="desc(CompanyConfiguration.id)")
    data_sources = relationship('DataSource', back_populates='company', order_by="desc(DataSource.id)")
    users = relationship('User', back_populates='company')

    @classmethod
    def get_for_email(cls, email):
        domain = email.split('@')[-1]
        try:
            logging.info('Searching for a company %s', domain)
            company = cls.query.filter(cls.domain == domain).one()
        except NoResultFound:
            return None
        return company

    @classmethod
    def get_for_domain(cls, domain):
        try:
            company = cls.query.filter(cls.domain == domain).one()
        except NoResultFound:
            return None
        return company

    @classmethod
    def get_by_id(cls, company_id):
        try:
            company = cls.query.filter(cls.id == company_id).one()
        except NoResultFound:
            return None
        return company

    @property
    def current_configuration(self):
        if len(self.configuration):
            return self.configuration[0]

    @property
    def windfarm_configuration(self):
        # import later to escape circular imports
        # TODO: it's probably better to fix this sometime in the future
        from core.services.windfarm import build_windfarm_for_company
        return build_windfarm_for_company(self.id)



class User(BaseModel):
    __tablename__ = 'user'
    __table_args__ = (UniqueConstraint('email', 'company_id', name='unique_user_in_company'),)

    INCLUDE_ATTRIBUTES = ('actions', 'company')
    EXCLUDE_ATTRIBUTES = ('password_hash',)

    email = Column(String(32), index=True)
    password_hash = Column(String(128))

    data_sources = relationship('DataSource', back_populates='user')

    company_id = Column(ForeignKey('company.id'), nullable=False)
    company = relationship('Company', foreign_keys=company_id)

    profile = relationship('UserProfile', uselist=False)
    permissions = Column(Enum(UserPermissions), default=UserPermissions.USER)

    confirmed = Column(Boolean, default=False)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=3600):  # TODO: change this!
        s = Serializer(SECRET_KEY, expires_in=expiration)
        return s.dumps({'id': self.id})

    @validates('email')
    def convert_email_to_lowercase(self, key, value):
        return value.lower()

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None

        user = db_session.query(User).get(data['id'])

        db_session.commit()
        return user

    @classmethod
    def get_user_by_email(cls, email):
        email = email.lower()
        try:
            return cls.query.filter(cls.email == email).one()
        except NoResultFound:
            return None

    @classmethod
    def check_credentials(cls, username: str, password: str):
        user = db_session.query(cls).filter(cls.email == username.lower()).one_or_none()
        if user.verify_password(password):
            return user
        else:
            return None


class CustomerAction(BaseModel):
    __tablename__ = 'customer_action'

    company_id = Column(ForeignKey('company.id'), nullable=False)
    company = relationship('Company', foreign_keys=company_id)
    user_id = Column(ForeignKey('user.id'), nullable=False)
    user = relationship('User', foreign_keys=user_id)
    action = Column(Enum(Actions))


class UserProfile(BaseModel):
    __tablename__ = 'user_profile'

    user_id = Column(ForeignKey('user.id'), nullable=False)
    user = relationship('User', foreign_keys=user_id)


class CompanyConfiguration(BaseModel):
    __tablename__ = 'company_configuration'

    company_id = Column(ForeignKey('company.id'), nullable=False)
    company = relationship('Company', foreign_keys=company_id)
    user_id = Column(ForeignKey('user.id'), nullable=False)
    user = relationship('User', foreign_keys=user_id)
    configuration = Column(JSON)  # TODO: Decide what the configuration should look like

    @classmethod
    def get_by_id(cls, id):
        try:
            configuration = cls.query.filter(CompanyConfiguration.id == id).one()
        except NoResultFound:
            return None
        return configuration

    @classmethod
    def get_by_company_id(cls, company_id):
        return cls.query.filter(cls.company_id == company_id).all()


def update_user_action(mapper, connection, self):
    action = CustomerAction(
        company_id=self.company_id,
        user_id=self.user_id,
        action=Actions.CONFIGURATION_UPDATE
    )
    with local_session_scope() as session:
        session.add(action)


event.listen(CompanyConfiguration, 'after_insert', update_user_action)
