from typing import Optional
from datetime import timezone, datetime, timedelta

import jwt
from jwt.exceptions import InvalidTokenError

SECRET_KEY = "534b743934c2b72c5f910b527c84594632c3355b7b7a6d87b97cf2b3d9726550"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expires_delta = expires_delta or timedelta(minutes=15)
    expire = datetime.now(timezone.utc) + expires_delta
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# We should be able to recover the user's username with his access token
def decode_access_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        return username
    except InvalidTokenError:
        return None