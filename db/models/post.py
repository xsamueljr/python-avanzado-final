from typing import Optional
from enum import Enum
from datetime import datetime

from sqlmodel import SQLModel, Field

from db.utils import generate_id


class PostStatus(Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    FRIENDS_ONLY = "friends_only"
    RESTRICTED = "restricted"


class PostCreate(SQLModel):
    content: str = Field(min_length=1, max_length=280)
    parent_id: Optional[str] = Field(default=None)
    status: PostStatus = Field(default=PostStatus.PUBLIC)


class Post(PostCreate, table=True):
    id: str = Field(primary_key=True, default_factory=generate_id)
    author_id: str
    likes_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.now)
