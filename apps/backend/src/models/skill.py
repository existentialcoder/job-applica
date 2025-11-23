from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from ..db.base_class import Base

class Skill(Base):
    __tablename__ = 'skills'
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    logo_url: Mapped[str] = mapped_column(String(500), nullable=True)
    description: Mapped[str] = mapped_column(String(500), nullable=True)

    def __repr__(self) -> str:
        return f'<Skill(name={self.name}, label={self.label}, description={self.description})>'