from datetime import datetime
from typing import Optional, Union

from sqlalchemy.orm import Session as DBSession

from app.models.auth.session import Session as SessionModel


def create_session(db: DBSession, user_id: int, token: str) -> SessionModel:
    session = SessionModel(
        id=token,
        user_id=user_id,
        last_seen_at=datetime.utcnow(),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_by_token(db: DBSession, token: str) -> Optional[SessionModel]:
    return db.query(SessionModel).filter(SessionModel.id == token).first()


def update_last_seen(db: DBSession, session: SessionModel) -> SessionModel:
    session.last_seen_at = datetime.utcnow()
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def delete_session(db: DBSession, session_or_token: Union[SessionModel, str]) -> None:
    if isinstance(session_or_token, str):
        session = get_by_token(db, session_or_token)
    else:
        session = session_or_token

    if session is not None:
        db.delete(session)
        db.commit()