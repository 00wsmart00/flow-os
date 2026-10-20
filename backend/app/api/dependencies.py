from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.database import get_session

SessionDependency = Annotated[Session, Depends(get_session)]
