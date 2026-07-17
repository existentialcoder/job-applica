from sqlalchemy import Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from ..db.base_class import Base

class Skill(Base):
    __tablename__ = 'skills'
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    label: Mapped[str] = mapped_column(Text, nullable=False)
    logo_url: Mapped[str] = mapped_column(Text, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f'<Skill(name={self.name}, label={self.label}, description={self.description})>'