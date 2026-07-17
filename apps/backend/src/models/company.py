# src/models/company.py
from sqlalchemy import Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db.base_class import Base

class Company(Base):
    __tablename__ = 'companies'
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    website: Mapped[str] = mapped_column(Text, nullable=True)
    email: Mapped[str] = mapped_column(Text, nullable=True)
    logo_url: Mapped[str] = mapped_column(Text, nullable=True)
    size: Mapped[int] = mapped_column(Integer, nullable=True)
    industry: Mapped[str] = mapped_column(Text, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    def __repr__(self):
        return f"<Company id={self.id} name='{self.name}'>"
