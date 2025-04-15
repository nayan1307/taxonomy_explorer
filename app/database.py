from sqlmodel import SQLModel, create_engine, Session

# Define the SQLite database file name
sqlite_file_name = "taxonomy.db"

# Create the database connection URL for SQLite
sqlite_url = f"sqlite:///{sqlite_file_name}"

# Create the database engine (echo=True prints SQL commands for debugging)
engine = create_engine(sqlite_url, echo=True)

# Function to create database tables based on SQLModel metadata
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Function to get a new database session for querying
def get_session():
    return Session(engine)
