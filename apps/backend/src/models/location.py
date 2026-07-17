from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from ..db.base_class import Base

class Location(Base):
    __tablename__ = 'locations'
    city: Mapped[str] = mapped_column(String, index=True)
    state: Mapped[str] = mapped_column(String, index=True)
    country: Mapped[str] = mapped_column(String, index=True)

    __table_args__ = (
        UniqueConstraint('city', 'state', 'country', name='uq_locations_city_state_country'),
    )
