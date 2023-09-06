from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pharmacy.database.core import Base, engine
from pharmacy.routers import users, inventories, admins


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(engine)

    yield
       
app = FastAPI(lifespan=lifespan)
app.include_router(inventories.router)
app.include_router(users.router)
app.include_router(admins.router)

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
    "http://localhost:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping")
def ping_pong() -> dict[str, str]:
    return {"message": "pong"}

@app.get("/name/{first_name}}")
def get_first_name(first_name: str) -> dict[str, str]:
    return {"name": first_name}
