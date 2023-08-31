from contextlib import asynccontextmanager

from fastapi import FastAPI

from pharmacy.database.core import Base, engine
from pharmacy.routers import users, inventories, admins


@asynccontextmanager
async def lifespan(app: FastAPI):
        # Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        yield
       
app = FastAPI(lifespan=lifespan)
app.include_router(admins.router)
app.include_router(inventories.router)
app.include_router(users.router)


@app.get("/ping")
def ping_pong() -> dict[str, str]:
    return {"message": "pong"}

@app.get("/name")
def get_first_name(first_name: str) -> dict[str, str]:
    return {"name": first_name}
