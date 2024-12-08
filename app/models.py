import random
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum as SQLEnum, Boolean, Date, DateTime
from app import db, app
from enum import Enum as RoleEnum
import hashlib
from flask_login import UserMixin

class UserRole(RoleEnum):
    ADMIN = 1
    STAFF_MANAGE = 2
    STAFF_TICKET = 3
    CUSTOMER = 4

class SeatClass(RoleEnum):
    BUSINESS = 1
    ECONOMY = 2

class User(UserMixin, db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    dob = Column(Date)
    gender = Column(Boolean)
    avatar = Column(String(200),
                    default="https://res.cloudinary.com/dxxwcby8l/image/upload/v1690528735/cg6clgelp8zjwlehqsst.jpg")
    user_role = Column(SQLEnum(UserRole), default=UserRole.CUSTOMER)

# class Staff(User):
#     id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
#     hire_date = Column(Date, nullable=False)
#     staff_salary = Column(Float, nullable=False)


class Payment(db.Model):
    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    payment_card_no =Column(String(20), nullable=False)
    payment_type = Column(Boolean, nullable=False)
    payment_date = Column(Date, nullable=False)
    payment_cost = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)


class Cancellation(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)
    refund = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    payment_id = Column(Integer, ForeignKey(Payment.payment_id), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)

class Airport(db.Model):
    airport_id = Column(Integer, primary_key=True, autoincrement=True)
    airport_name = Column(String(255), nullable=False)
    airport_address = Column(String(255), nullable=False)
    airport_image = Column(String(255), nullable=False)


class FlightRoute(db.Model):
    fr_id = Column(Integer, primary_key=True, autoincrement=True)
    departure_airport_id = Column(Integer, ForeignKey(Airport.airport_id), nullable=False)
    arrival_airport_id = Column(Integer, ForeignKey(Airport.airport_id), nullable=False)
    distance = Column(Float)
    description = Column(String(255))
    flights = relationship('Flight', backref='FlightRoute', lazy = True)


class Flight(db.Model):
    flight_id = Column(Integer, primary_key=True, autoincrement=True)
    f_dept_time = Column(DateTime, nullable=False)
    flight_arr_time = Column(DateTime, nullable=False)
    flight_duration = Column(Float)
    flight_price = Column(Float)
    flight_route_id = Column(Integer, ForeignKey(FlightRoute.fr_id), nullable=False)


class Plane(db.Model):
    plane_id = Column(Integer, primary_key=True, autoincrement=True)
    plane_name = Column(String(255), nullable=False)
    seats = relationship('Seat', backref = 'Plane', lazy = True, cascade="all, delete")


class Company(db.Model):
    com_id = Column(Integer, primary_key=True, autoincrement=True)
    com_name = Column(String(255), nullable=False)
    com_country = Column(String(255), nullable=False)


class Seat(db.Model):
    seat_id = Column(Integer, primary_key=True, autoincrement=True)
    seat_number = Column(Integer, nullable=False)
    seat_class = Column(SQLEnum(SeatClass), default = SeatClass.ECONOMY)
    seat_status = Column(Boolean, nullable=False)
    plane_id = Column(Integer, ForeignKey(Plane.plane_id), nullable=False)


class Ticket(db.Model):
    ticket_id = Column(Integer, primary_key=True, autoincrement=True)
    issue_date = Column(Date, nullable=False)
    ticket_place = Column(Integer, ForeignKey(Airport.airport_id), nullable=False)
    ticket_price = Column(Float, nullable=False)
    ticket_status = Column(Boolean, nullable=False)
    ticket_gate = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    flight_id = Column(Integer, ForeignKey(Flight.flight_id), nullable=False)



class Luggage(db.Model):
    luggage_id = Column(Integer, primary_key=True, autoincrement=True)
    luggage_name = Column(String(255), nullable=False)
    weight = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    flight_id = Column(Integer, ForeignKey(Flight.flight_id), nullable=False)

class FlightSchedule(db.Model):
    schedule_id = Column(Integer, primary_key=True, autoincrement=True)
    flight_id = Column(Integer, ForeignKey(Flight.flight_id), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
