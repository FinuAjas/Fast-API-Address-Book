from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import schemas
import services
from typing import List

app = FastAPI()

services.create_database()


@app.post("/users", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(services.get_db)):
    """Function to create new User"""
    db_user = services.get_user_by_email(db=db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400, detail="Email is in use! Try again with different email.")
    return services.create_user(db=db, user=user)


@app.get("/users", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(services.get_db)):
    """Shows all Users"""
    users = services.get_users(db=db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(services.get_db)):
    """Shows User by ID"""
    user = services.get_user(db=db, user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"User not found with id {user_id}!")
    return user


@app.post("/users/{user_id}/address", response_model=schemas.Address)
def create_address(user_id: int, address: schemas.AddressCreate, db: Session = Depends(services.get_db)):
    """Create new address"""
    user = services.get_user(db=db, user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"User not found with id {user_id}!")
    return services.create_address(db=db, address=address, user_id=user_id)


@app.get("/address", response_model=List[schemas.Address])
def read_addresses(skip: int = 0, limit: int = 10, db: Session = Depends(services.get_db)):
    """Shows all addresses"""
    addresses = services.get_addresses(db=db, skip=skip, limit=limit)
    return addresses


@app.get("/address/{user_id}", response_model=List[schemas.Address])
def read_addresses_by_user(user_id: int, db: Session = Depends(services.get_db)):
    """Shows all address of a paticular user based on user_id"""
    user = services.get_user(db=db, user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=404, detail=f"User not found with id {user_id}!")
    addresses = services.get_addresses_by_user(user_id=user_id, db=db)
    if addresses is None:
        raise HTTPException(
            status_code=404, detail=f"No addresses found with for user with id {user_id}!")
    return addresses


@app.get("/address/{address_id}", response_model=schemas.Address)
def read_address(address_id: int, db: Session = Depends(services.get_db)):
    """Shows address by address_id"""
    addresses = services.get_address(address_id=address_id, db=db)
    if addresses is None:
        raise HTTPException(
            status_code=404, detail=f"Addresses not found with id {address_id}!")
    return addresses


@app.delete("/address/{address_id}")
def delete_address(address_id: int, db: Session = Depends(services.get_db)):
    """Delete address by address_id"""
    addresses = services.get_address(address_id=address_id, db=db)
    if addresses is None:
        raise HTTPException(
            status_code=404, detail=f"Addresses not found with id {address_id}!")
    services.delete_address(address_id=address_id, db=db)
    return f"Address Deleted with id {address_id}!"


@app.put("/address/{address_id}", response_model=schemas.Address)
def update_address(address_id: int, address: schemas.AddressCreate, db: Session = Depends(services.get_db)):
    """Update address by address_id"""
    address_check = services.get_address(address_id=address_id, db=db)
    if address_check is None:
        raise HTTPException(
            status_code=404, detail=f"Addresses not found with id {address_id}!")
    return services.update_address(db=db, address=address, address_id=address_id)


@app.get("/find_near_by_address")
def find_near_by_address(address: str, distance: int, skip: int = 0, limit: int = 10, db: Session = Depends(services.get_db)):
    """Returns all address in the database base on given city name"""
    near_by_address = services.find_near_by_address(
        address=address, km=distance, db=db, skip=skip, limit=limit)
    return near_by_address
