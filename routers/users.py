from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from db.models.follow import Follow
from dependencies import get_current_user, get_session
from db.models.user import User, UserRead, UserStatus
from fastapi import Depends

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/{user_id}/follow", status_code=204)
def follow_user(
    user_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    user_to_follow = session.exec(select(User).where(User.id == user_id)).first()
    if not user_to_follow:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_to_follow.status == UserStatus.PENDING_CONFIRMATION:
        raise HTTPException(status_code=400, detail="User is pending confirmation")
    
    if user.id == user_to_follow.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    
    already_followed = session.exec(select(Follow).where(Follow.follower_id == user.id, Follow.following_id == user_to_follow.id)).first() is not None
    if already_followed:
        raise HTTPException(status_code=400, detail="Already followed")
    
    follow = Follow(follower_id=user.id, following_id=user_to_follow.id)
    session.add(follow)
    session.commit()
    

@router.delete("/{user_id}/follow", status_code=204)
def unfollow_user(
    user_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    user_to_unfollow = session.exec(select(User).where(User.id == user_id)).first()
    if not user_to_unfollow:
        raise HTTPException(status_code=404, detail="User not found")
    
    follow = session.exec(select(Follow).where(Follow.follower_id == user.id, Follow.following_id == user_to_unfollow.id)).first()
    if not follow:
        raise HTTPException(status_code=400, detail="Not followed")
    
    session.delete(follow)
    session.commit()


@router.get("/{user_id}/followers", response_model=list[UserRead])
def get_followers(
    user_id: str,
    session: Session = Depends(get_session)
):
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    followers = session.exec(
        select(User).join(Follow, User.id == Follow.follower_id).where(Follow.following_id == user_id)
    ).all()
    return followers
    