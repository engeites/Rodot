from sqlalchemy.orm import sessionmaker
from .models import AdminUser
from .db import engine

Session = sessionmaker(bind=engine)


def get_all_admins() -> list:
    session = Session()
    return session.query(AdminUser).all()