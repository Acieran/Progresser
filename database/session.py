from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker
from fastapi import Depends

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# In FastAPI endpoint:
def get_current_user(
    db = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    user = get_user_from_db(db, token)
    return user