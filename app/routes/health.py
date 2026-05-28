from fastapi import APIRouter, Depends
from sqlmodel import Session, text

from app.infra.db import get_session
router = APIRouter()

@router.get("")
def health(session: Session = Depends(get_session)) -> dict[str, str]:
    result = session.exec(text("SELECT * from Cliente"))
    print(result.all())
    return {
        "status": "API E DB OK"
    }
