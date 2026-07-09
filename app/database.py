from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import Config

# 1. Configure the database engine URL
SQLALCHEMY_DATABASE_URL = Config.DATABASE_URL

# 2. Create the SQLAlchemy engine
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 3. Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Create a Declarative Base class
Base = declarative_base()

# 5. Dependency injection helper for FastAPI routes
def get_db():
    """
    Creates a new database session for a request and ensures it closes 
    automatically after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()