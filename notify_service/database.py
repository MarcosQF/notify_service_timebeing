from sqlalchemy import create_engine
from sqlalchemy.orm import Session, registry

from .settings import settings

reg = registry()

engine = create_engine(settings.DATABASE_URL)


def get_session():
    return Session(engine)
