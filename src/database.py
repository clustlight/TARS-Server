import datetime
import sqlalchemy
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, Text, DateTime, Boolean

engine = sqlalchemy.create_engine('sqlite:///data/tars.sqlite3', echo=False)
Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(Text, primary_key=True)
    screen_id = Column(Text)
    name = Column(Text)

    profile_image = Column(Text)
    profile_description = Column(Text)

    level = Column(Integer)
    supporter_count = Column(Integer)
    supporting_count = Column(Integer)

    last_update = Column(DateTime)

    subscriptions = Column(Boolean, default=False)


def get_user(user_id):
    session = sessionmaker(bind=engine)()
    user = session.query(User).filter_by(id=user_id).one()
    session.close()

    return user


def get_users(user_list):
    session = sessionmaker(bind=engine)()
    users = session.query(User).filter(User.id.in_(user_list)).all()
    session.close()

    return users


def get_subscription_users():
    session = sessionmaker(bind=engine)()
    users = session.query(User).filter(User.subscriptions == True).all()
    session.close()

    return users


def update_user(user_data):
    session = sessionmaker(bind=engine)()

    user = User()
    user.id = user_data["user"]["id"]
    user.screen_id = user_data["user"]["screen_id"]
    user.name = user_data["user"]["name"]

    user.profile_image = user_data["user"]["image"]
    user.profile_description = user_data["user"]["profile"]

    user.level = user_data["user"]["level"]
    user.supporter_count = user_data["supporter_count"]
    user.supporting_count = user_data["supporting_count"]

    user.last_update = datetime.datetime.now()

    session.merge(user)
    session.commit()

    session.close()


def set_subscription_user(user_id):
    session = sessionmaker(bind=engine)()
    user = User()
    user.id = user_id
    user.subscriptions = True

    session.merge(user)
    session.commit()

    session.close()


def unset_subscription_user(user_id):
    session = sessionmaker(bind=engine)()

    user = User()
    user.id = user_id
    user.subscriptions = False

    session.merge(user)
    session.commit()

    session.close()
