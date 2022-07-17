from database import SessionLocal, Base, engine
from sqlalchemy.orm import Session
import pydantic
import models
import schemas
from geopy.geocoders import Nominatim
from geopy import distance
import logging


logging.basicConfig(filename='logs.log', level=logging.INFO,
                    format='%(levelname)s : %(asctime)s : %(message)s')


def create_database():
    return Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user_by_email(db: Session, email: pydantic.EmailStr):
    """Returns userdata of given email"""
    user = db.query(models.User).filter(models.User.email == email).first()
    logging.info(f'{user.email} User found')
    return user


def create_user(db: Session, user: schemas.UserCreate):
    """Function to create new user"""
    password = user.password
    db_user = models.User(email=user.email, hashed_password=password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logging.info(f'{db_user.email} User created')
    return db_user


def get_users(db: Session, skip: int, limit: int):
    """Returns all user data"""
    users = db.query(models.User).offset(skip).limit(limit).all()
    logging.info(f'Users found')
    return users


def get_user(db: Session, user_id: int):
    """Return userdata of given user id"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    logging.info(f'{user.email} User found')
    return user


def create_address(db: Session, address: schemas.AddressCreate, user_id: int):
    """Function to create new address. Accepts city name from user and using 'find_cordinates' 
    function gets the geocornitaes and saves latitude and longitude automaticaly"""
    address = models.Addresses(**address.dict(), owner_id=user_id)
    coordinates = find_coordinates(address.city)
    address.name = address.name
    address.city = address.city
    address.latitude = coordinates.latitude
    address.longitude = coordinates.longitude
    db.add(address)
    db.commit()
    db.refresh(address)
    logging.info(f'{address.city} Address created')
    return address


def get_addresses(db: Session, skip: int, limit: int):
    """Returns all address"""
    addresses = db.query(models.Addresses).offset(skip).limit(limit).all()
    logging.info(f'Address found')
    return addresses


def get_addresses_by_user(db: Session, user_id: int):
    """Returns address of single user."""
    addresses = db.query(models.Addresses).filter(
        models.Addresses.owner_id == user_id).all()
    logging.info(f'Address of user {user_id}')
    return addresses


def get_address(db: Session, address_id: int):
    """Returns address by address_id"""
    address = db.query(models.Addresses).filter(
        models.Addresses.id == address_id).first()
    logging.info(f'{address.city} Address found')
    return address


def delete_address(db: Session, address_id: int):
    """Function to delete address"""
    db.query(models.Addresses).filter(
        models.Addresses.id == address_id).delete()
    logging.info(f'Address deleted.')
    db.commit()


def update_address(db: Session, address: schemas.AddressCreate, address_id: int):
    """Function to update an address"""
    db_address = get_address(db=db, address_id=address_id)
    db_address.name = address.name
    db_address.city = address.city
    db_address.longitude = address.longitude
    db_address.latitude = address.latitude
    db.commit()
    db.refresh(db_address)
    logging.info(f'{db_address.city} Address updated')
    return db_address


def find_coordinates(city):
    """Accepts a location name and returns its latitude and longitude"""
    geolocator = Nominatim(user_agent="my_app")
    coordinates = geolocator.geocode(city)
    logging.info(f'{coordinates.longitude}{coordinates.latitude} geolocation')
    return coordinates


def find_near_by_address(address, km, db, skip, limit):
    coordinates = find_coordinates(address)
    coord_long_lat = ((coordinates.longitude, coordinates.latitude))
    logging.info(f'{coord_long_lat} geolocation')
    addresses = get_addresses(db=db, skip=skip, limit=limit)
    address_in_given_km = []
    km = km
    for address in addresses:
        city = find_coordinates(address.city)
        city_long_lat = ((city.longitude, city.latitude))
        logging.info(f'{city_long_lat} geolocation')
        difference_in_km = distance.distance(coord_long_lat, city_long_lat).km
        logging.info(difference_in_km)
        if difference_in_km < km:
            address_in_given_km.append(address)
    return address_in_given_km
