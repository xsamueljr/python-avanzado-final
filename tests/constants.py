from enum import Enum


class Endpoints(Enum):
    REGISTER = "/auth/register"
    CONFIRM = "/auth/confirm/{}"
    LOGIN = "/auth/token"

    NEW_POST = "/posts/new"
    DELETE_POST = "/posts/{}"
    LIKE_POST = "/posts/{}/like"

    FOLLOW_USER = "/users/{}/follow"
    GET_FOLLOWERS = "/users/{}/followers"


VALID_PAYLOAD = {
    "email": "user@example.com",
    "username": "cooluser",
    "password": "securepassword",
    "name": "CoolUser",
    "birthday": "2000-01-01",
}
