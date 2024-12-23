from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import QueuePool

from .models import Base


# Get the directory of the current script
current_dir = Path(__file__).parent.resolve()

# Set the SQLite database path relative to the current directory
DB_PATH = current_dir / "sqlite.db"

# Ensure the directory for the database exists
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Create engine with connection pooling and timeout settings
engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={
        "check_same_thread": False,
        "timeout": 30,  # Wait up to 30 seconds for locks to be released
    },
    poolclass=QueuePool,
    pool_size=20,  # Maximum number of connections to keep
    max_overflow=0,  # Maximum number of connections that can be created beyond pool_size
    pool_timeout=30,  # Seconds to wait before giving up on getting a connection from the pool
    pool_recycle=1800,  # Recycle connections after 30 minutes
)

# Create scoped session factory
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

# Create all tables
Base.metadata.create_all(engine)


@contextmanager
def get_db_session():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
        Session.remove()  # Remove session from scoped registry
