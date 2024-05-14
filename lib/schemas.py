from typing import Union

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    hashed_password: str


class User(UserBase):
    username: str
    email: str

    class ConfigDict:
        from_attributes = True


class UserInDB(User):
    hashed_password: str


class MachineCreate(BaseModel):
    name: str


class Machine(MachineCreate):
    id: int
    state: str

    class ConfigDict:
        from_attributes = True


class SimulationRunCreate(BaseModel):
    name: str
    machine_id: int


class SimulationRun(SimulationRunCreate):
    loss: float


class SimulationRunFull(SimulationRun):
    id: int
    machine: Machine | None = None
