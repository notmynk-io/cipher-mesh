from sqlalchemy import create_engine
from app.models import metadata, DATABASE_URL

def create_db():
    engine = create_engine(DATABASE_URL)
    metadata.create_all(engine)

if __name__ == "__main__":
    create_db()

