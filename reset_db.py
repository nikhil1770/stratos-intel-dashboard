import os
from database.models import Base, engine

def reset():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Recreating tables...")
    Base.metadata.create_all(bind=engine)
    print("Database reset complete. All #UNCLASSIFIED data flushed.")

if __name__ == "__main__":
    reset()
