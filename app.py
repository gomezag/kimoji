from datetime import timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from lib import schemas, models
from lib.auth import (ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token,
                      get_current_active_user, is_authenticated)
from lib.crud import get_machines, get_simulation_runs
from lib.db import SessionLocal, engine, get_db


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response


@app.post("/token")
async def login_for_access_token(
    db: Annotated[Session, Depends(get_db)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> schemas.Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return schemas.Token(access_token=access_token, token_type="bearer")


@app.get("/users/me/")
async def read_users_me(
    current_user: Annotated[schemas.User, Depends(get_current_active_user)],
) -> schemas.User:
    return current_user


@app.get("/machines")
async def get_machine_list(
    db: Annotated[Session, Depends(get_db)],
    token_data: Annotated[schemas.TokenData, Depends(is_authenticated)]
) -> list[schemas.Machine]:
    return get_machines(db)


@app.get("/runs")
async def get_simulation_runs_list(
    db: Annotated[Session, Depends(get_db)],
    request: Request,
    token_data: Annotated[schemas.TokenData, Depends(is_authenticated)]
) -> list[schemas.SimulationRun]:
    return get_simulation_runs(db, **request.query_params)


@app.get("/")
async def root():
    return {"message": "Hello World"}
