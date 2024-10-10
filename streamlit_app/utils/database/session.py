from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from .models import Base

# Get the directory of the current script
current_dir = Path(__file__).parent.resolve()

# Set the SQLite database path relative to the current directory
DB_PATH = current_dir / "sqlite.db"

# Ensure the directory for the database exists
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Create engine and session
engine = create_engine(
    f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False}
)
Session = sessionmaker(bind=engine)

# Create all tables
Base.metadata.create_all(engine)
