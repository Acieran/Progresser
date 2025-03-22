from typing import List
from typing import Optional
from sqlalchemy import ForeignKey, Boolean, Integer
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

class Base(DeclarativeBase):
    pass

class Workspace(Base):
    __tablename__ = "workspaces"
    name: Mapped[str] = mapped_column(String(30),primary_key=True)
    description: Mapped[Optional[str]] = mapped_column(String(1000),nullable=True)
    owner_name: Mapped[str] = mapped_column(ForeignKey("users.username"))
    owner: Mapped["User"] = relationship(back_populates="workspace")
    def __repr__(self) -> str:
        return f"Item(Name={self.name!r}, Owner={self.owner_name!r}, Description={self.description!r})"

class User(Base):
    __tablename__ = "users"
    username: Mapped[str] = mapped_column(primary_key=True)
    # password: Mapped[str] = mapped_column(String())
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    telegram_username: Mapped[str] = mapped_column(String, nullable=True)
    workspace: Mapped[List["Workspace"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan", lazy="select"
    )
    user_state: Mapped[List["UserState"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    def __repr__(self) -> str:
        return f"Username(id={self.username!r}, Active={self.active!r}, Chat_id={self.telegram_username!r})"

class UserState(Base):
    __tablename__ = "user_state"
    telegram_username: Mapped[str] = mapped_column(ForeignKey("users.telegram_username"), primary_key=True)
    state: Mapped[Optional[str]] = mapped_column(String(50), default=None, nullable=True)
    user: Mapped["User"] = relationship(User, back_populates="user_state")
    def __repr__(self) -> str:
        return f"Username(id={self.telegram_username!r}, State={self.state!r})"
