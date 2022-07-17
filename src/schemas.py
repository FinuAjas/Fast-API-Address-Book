from pydantic import BaseModel, EmailStr
from typing import List, Optional


class AddressBase(BaseModel):
    name: str
    city: str
    longitude: Optional[float] = None
    latitude: Optional[float] = None


class AddressCreate(AddressBase):
    pass


class Address(AddressBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    addresses: List[Address] = []

    class Config:
        orm_mode = True
