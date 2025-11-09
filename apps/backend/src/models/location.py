from sqlalchemy import Enum, String, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db.base_class import Base

class Location(Base):
    __tablename__ = 'locations'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    city: Mapped[str] = mapped_column(String, index=True)
    state: Mapped[str] = mapped_column(String, index=True)
    country: Mapped[str] = mapped_column(String, index=True)
