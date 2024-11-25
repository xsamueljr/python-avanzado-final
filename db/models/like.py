from sqlmodel import SQLModel, Field


class Like(SQLModel, table=True):
    user_id: str = Field(foreign_key="user.id", primary_key=True)
    post_id: str = Field(foreign_key="post.id", primary_key=True)
