from datetime import date

from sqlmodel import SQLModel, Field

from db.utils import generate_id


class ConfirmationToken(SQLModel, table=True):
    user_id: str = Field(foreign_key="user.id", primary_key=True)
    token: str = Field(primary_key=True, default_factory=generate_id)
    created_at: date = Field(default_factory=date.today)
