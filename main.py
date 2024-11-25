from contextlib import asynccontextmanager

from fastapi import FastAPI

from config import PORT, HOST
from db.config import create_db_and_tables
from routers import auth_router, posts_router, users_router
from email_manager import EmailManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    EmailManager.start()
    yield
    EmailManager.close()


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(posts_router)
app.include_router(users_router)


@app.get("/")
async def index():
    return {"message": "Hello World"}


if __name__ == '__main__': # pragma: no cover
    from uvicorn import run
    run(app, host=HOST, port=PORT)
