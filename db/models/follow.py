from sqlmodel import SQLModel, Field


class Follow(SQLModel, table=True):
    follower_id: str = Field(foreign_key="user.id", primary_key=True)
    following_id: str = Field(foreign_key="user.id", primary_key=True)
