from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# استفاده از DATABASE_URL که در فایل .env تعریف کردی
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# برای PostgreSQL نیاز به آن connect_args نداریم
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency برای استفاده در مسیرها
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
