from datetime import date
from sqlalchemy import String, Date
from sqlalchemy.orm import Mapped, mapped_column

from pharmacy.database.core import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    contact: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    address: Mapped[str | None] = mapped_column(String)
    email: Mapped[str | None] = mapped_column(String, unique=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    password: Mapped[str] = mapped_column(String, nullable=False)