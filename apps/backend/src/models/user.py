from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from ..db.base_class import Base

class User(Base):
    __tablename__ = 'users'
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    user_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    signup_key: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    def __repr__(self) -> str:
        return f'<User(user_name={self.user_name}, email={self.email}, first_name={self.first_name}, last_name={self.last_name})>'
