from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import InventorySnapshot, MaterialSupplyPosition


class InventoryRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_snapshot(self, snapshot_id: int) -> InventorySnapshot | None:
        statement = (
            select(InventorySnapshot)
            .options(
                selectinload(InventorySnapshot.positions).joinedload(
                    MaterialSupplyPosition.material
                )
            )
            .where(InventorySnapshot.id == snapshot_id)
        )
        return self.session.scalar(statement)
