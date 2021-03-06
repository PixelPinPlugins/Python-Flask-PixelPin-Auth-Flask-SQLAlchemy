"""Flask SQLAlchemy ORM models for Pixelpin Auth"""
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

from pixelpin_auth_core.utils import setting_name, module_member
from pixelpin_auth_sqlalchemy.storage import SQLAlchemyUserMixin, \
                                      SQLAlchemyAssociationMixin, \
                                      SQLAlchemyNonceMixin, \
                                      SQLAlchemyCodeMixin, \
                                      SQLAlchemyPartialMixin, \
                                      BaseSQLAlchemyStorage


PSABase = declarative_base()


class _AppSession(PSABase):
    __abstract__ = True

    @classmethod
    def _set_session(cls, app_session):
        cls.app_session = app_session

    @classmethod
    def _session(cls):
        return cls.app_session


class UserPixelpinAuth(_AppSession, SQLAlchemyUserMixin):
    """Pixelpin Auth association model"""
    # Temporary override of constraints to avoid an error on the still-to-be
    # missing column uid.
    __table_args__ = ()

    @classmethod
    def user_model(cls):
        return cls.user.property.argument

    @classmethod
    def username_max_length(cls):
        user_model = cls.user_model()
        return user_model.__table__.columns.get('username').type.length


class Nonce(_AppSession, SQLAlchemyNonceMixin):
    """One use numbers"""
    pass


class Association(_AppSession, SQLAlchemyAssociationMixin):
    """OpenId account association"""
    pass


class Code(_AppSession, SQLAlchemyCodeMixin):
    """Mail validation single one time use code"""
    pass


class Partial(_AppSession, SQLAlchemyPartialMixin):
    """Partial pipeline storage"""
    pass


class FlaskStorage(BaseSQLAlchemyStorage):
    user = UserPixelpinAuth
    nonce = Nonce
    association = Association
    code = Code
    partial = Partial


def init_pixelpin_auth(app, session):
    UID_LENGTH = app.config.get(setting_name('UID_LENGTH'), 255)
    User = module_member(app.config[setting_name('USER_MODEL')])
    _AppSession._set_session(session)
    UserPixelpinAuth.__table_args__ = (UniqueConstraint('provider', 'uid'),)
    UserPixelpinAuth.uid = Column(String(UID_LENGTH))
    UserPixelpinAuth.user_id = Column(User.id.type, ForeignKey(User.id),
                                    nullable=False, index=True)
    UserPixelpinAuth.user = relationship(User, backref=backref('pixelpin_auth',
                                                             lazy='dynamic'))
