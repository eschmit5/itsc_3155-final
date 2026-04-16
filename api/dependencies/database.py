from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import conf
from urllib.parse import quote_plus

try:
    from .local_config import local_conf as conf
    print("Using local configuration")
except ImportError:
    from .config import conf
    print("Using default configuration")


SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{conf.db_user}:{quote_plus(conf.db_password)}@{conf.db_host}:{conf.db_port}/{conf.db_name}?charset=utf8mb4"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()