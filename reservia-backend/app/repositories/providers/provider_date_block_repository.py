from typing import Optional
from sqlalchemy.orm import Session as DBSession
from app.models.providers.provider_date_block import DateBlockEstado, ProviderDateBlock


def create(db: DBSession, provider_profile_id: int, fecha, motivo: Optional[str]) -> ProviderDateBlock:
    block = ProviderDateBlock(provider_profile_id=provider_profile_id, fecha=fecha, motivo=motivo)
    db.add(block)
    db.commit()
    db.refresh(block)
    return block


def get_by_id(db: DBSession, id: int) -> Optional[ProviderDateBlock]:
    return db.query(ProviderDateBlock).filter(ProviderDateBlock.id == id).first()


def get_active_by_provider_and_fecha(db: DBSession, provider_profile_id: int, fecha) -> Optional[ProviderDateBlock]:
    return (
        db.query(ProviderDateBlock)
        .filter(
            ProviderDateBlock.provider_profile_id == provider_profile_id,
            ProviderDateBlock.fecha == fecha,
            ProviderDateBlock.estado == DateBlockEstado.active,
        )
        .first()
    )


def list_by_provider(db: DBSession, provider_profile_id: int) -> list[ProviderDateBlock]:
    return (
        db.query(ProviderDateBlock)
        .filter(ProviderDateBlock.provider_profile_id == provider_profile_id)
        .order_by(ProviderDateBlock.fecha.desc())
        .all()
    )


def deactivate(db: DBSession, block: ProviderDateBlock) -> ProviderDateBlock:
    block.estado = DateBlockEstado.inactive
    db.add(block)
    db.commit()
    db.refresh(block)
    return block