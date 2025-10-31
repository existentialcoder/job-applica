from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from ..db.base_class import Base

class Skill(Base):
    __tablename__ = 'skills'
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    proficiency_level: Mapped[int] = mapped_column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f'<Skill(name={self.name}, proficiency_level={self.proficiency_level})>'
