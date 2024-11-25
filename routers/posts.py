from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from db.models.like import Like
from db.models.user import User
from dependencies import get_current_user, get_session

from db.models.post import PostCreate, Post
from fastapi import HTTPException
from fastapi import HTTPException
from fastapi import HTTPException


router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("/new", status_code=201)
async def create_post(
    post: PostCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    db_post = Post(**post.model_dump(), author_id=user.id)
    session.add(db_post)
    session.commit()
    return {"message": "Post created successfully"}


@router.delete("/{post_id}", status_code=204)
async def delete_post(
    post_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    post = session.exec(select(Post).where(Post.id == post_id)).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if post.author_id != user.id:
        raise HTTPException(status_code=403, detail="You are not the author of this post")
    
    session.delete(post)
    session.commit()


@router.post("/{post_id}/like", status_code=204)
async def like_post(
    post_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    post = session.exec(select(Post).where(Post.id == post_id)).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.author_id == user.id:
        raise HTTPException(status_code=403, detail="You cannot like your own post")

    existing_like = session.exec(select(Like).where(Like.user_id == user.id, Like.post_id == post_id)).first()
    if existing_like:
        raise HTTPException(status_code=403, detail="You have already liked this post")
    
    like = Like(user_id=user.id, post_id=post_id)
    post.likes_count += 1
    session.add(post)
    session.add(like)
    session.commit()


@router.delete("/{post_id}/like", status_code=204)
async def unlike_post(
    post_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    post = session.exec(select(Post).where(Post.id == post_id)).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.author_id == user.id:
        raise HTTPException(status_code=403, detail="You cannot unlike your own post")

    like = session.exec(select(Like).where(Like.user_id == user.id, Like.post_id == post_id)).first()
    if not like:
        raise HTTPException(status_code=403, detail="You have not liked this post")

    post.likes_count -= 1
    session.add(post)
    session.delete(like)
    session.commit()
