from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base

from datetime import datetime

# Строка подключения к SQLite
sqlite_database = "sqlite:///university_appeals.db"

# Создаем движок
engine = create_engine(sqlite_database, echo=True)

# Создаем класс сессии
Session = sessionmaker(autoflush=False, bind=engine)
session = Session()

Base = declarative_base()

def get_now_date():
    return datetime.now()

class Appeal(Base):
    __tablename__ = 'appeals'
    id = Column(Integer, primary_key=True)
    tg_user_id = Column(String, nullable=False)
    tg_username = Column(String, nullable=True)
    appeal_text = Column(String, nullable=False)
    date = Column(DateTime, default=get_now_date(), nullable=False)

    def __str__(self):
        return f'{self.tg_user_id} {self.tg_username} {self.appeal_text} {self.date}'

class Admin(Base):
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True)
    tg_user_id = Column(String, nullable=True)
    tg_username = Column(String, nullable=True)
    is_admin = Column(Boolean, nullable=False, default=True)

# Создаем все таблицы
Base.metadata.create_all(engine)

async def create_appeal(now_session: Session, user_id: str, username: str, text: str) -> None:
    try:
        new_appeal = Appeal(
            tg_user_id=user_id,
            tg_username=username,
            appeal_text=text
        )
        now_session.add(new_appeal)
        now_session.commit()
    except Exception as e:
        now_session.rollback()
        print(e)

async def get_all_appeal(now_session: Session) -> list[Appeal]:
    appeals = now_session.query(Appeal).all()
    return appeals

def add_admin(now_session: Session, id: str = None, username: str = None):
    if id is None and username is None:
        raise ValueError('Хотя бы одно значение из ["id", "username"] должно быть указано')
    admin = Admin(
        tg_user_id=id,
        tg_username=username
    )
    now_session.add(admin)
    now_session.commit()

async def get_admins_ids(now_session: Session) -> list[str]:
    admins = now_session.query(Admin).filter(
        Admin.is_admin == True
    ).all()
    return [admin.tg_user_id for admin in admins]

async def get_admins_names(now_session: Session) -> list[str]:
    admins = now_session.query(Admin).filter(
        Admin.is_admin == True
    ).all()
    return [admin.tg_username for admin in admins]

# add_admin()
