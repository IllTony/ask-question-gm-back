import typer
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import create_engine

from src.core.settings import settings
from src.models.user import User
from src.utils.password import generate_password

app = typer.Typer()
dsn = settings.database_url_sync
engine = create_engine(dsn, echo=False, future=True)
sync_session = sessionmaker(engine, class_=Session, expire_on_commit=False)


@app.command()
def create_user(username: str, password: str):
    with sync_session() as session:
        query = select(User).filter(User.username == username)
        result = session.execute(query).scalars().all()
        if result:
            print("Пользователь с логином {} уже существует".format(username))
            return
        user = User(username=username, password=generate_password(password), is_active=True)
        session.add(user)
        session.commit()
        print("Пользователь с логином {}  успешно создан".format(username))


@app.command()
def create_superuser(username: str, password: str):
    with sync_session() as session:
        query = select(User).filter(User.username == username)
        result = session.execute(query).scalars().all()
        if result:
            print("Пользователь с логином {} уже существует".format(username))
            return
        user = User(username=username, password=generate_password(password), is_active=True, is_admin=True)
        session.add(user)
        session.commit()
        print("Пользователь с логином {} с правами администратора успешно создан".format(username))


if __name__ == "__main__":
    app()
