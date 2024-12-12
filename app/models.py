import random
from cloudinary.utils import unique
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum as SQLEnum, Boolean, Date, DateTime
from app import db, app
from enum import Enum as RoleEnum
import hashlib
from flask_login import UserMixin
from datetime import datetime, timezone


class UserRole(RoleEnum):
    ADMIN = 1
    STAFF_MANAGE = 2
    STAFF_TICKET = 3
    CUSTOMER = 4


class SeatClass(RoleEnum):
    BUSINESS = 1
    ECONOMY = 2


# Enum cho loại chuyến bay
class FlightType(RoleEnum):
    DIRECT = 1  # Bay thẳng
    ONE_STOP = 2  # 1 điểm dừng
    MULTIPLE_STOP = 3  # Nhiều điểm dừng


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

    def __str__(self):
        return self.name


class Payment(db.Model):
    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    payment_card_no = Column(String(20), nullable=False)
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

    def __str__(self):
        return self.airport_name


class FlightRoute(db.Model):
    fr_id = Column(Integer, primary_key=True, autoincrement=True)
    departure_airport_id = Column(Integer, ForeignKey(Airport.airport_id), nullable=False)
    arrival_airport_id = Column(Integer, ForeignKey(Airport.airport_id), nullable=False)
    distance = Column(Float)
    description = Column(String(255))
    flights = relationship('Flight', backref='flight_route', lazy=True)

    # Định nghĩa quan hệ để truy cập thông tin sân bay
    departure_airport = relationship('Airport', foreign_keys=[departure_airport_id])
    arrival_airport = relationship('Airport', foreign_keys=[arrival_airport_id])

    def __str__(self):
        return f"Route {self.fr_id}"


class Plane(db.Model):
    plane_id = Column(Integer, primary_key=True, autoincrement=True)
    plane_name = Column(String(255), nullable=False)
    seats = relationship('Seat', backref='plane', lazy=True, cascade="all, delete")

    def __str__(self):
        return self.plane_name


class Flight(db.Model):
    flight_id = Column(Integer, primary_key=True, autoincrement=True)
    f_dept_time = Column(DateTime, nullable=False) #tg di
    flight_arr_time = Column(DateTime, nullable=False) #tg toi
    flight_duration = Column(Float) # tong tg di
    flight_price = Column(Float)
    flight_type = Column(SQLEnum(FlightType), default=FlightType.DIRECT)  # Enum cho flight_type
    flight_route_id = Column(Integer, ForeignKey(FlightRoute.fr_id), nullable=False)
    plane_id = Column(Integer, ForeignKey(Plane.plane_id), nullable=False)

    plane = relationship('Plane', backref='flights', lazy=True)

    # Sửa backref thành 'associated_flights' để tránh xung đột
    economy_cards = relationship('EconomyCard', backref='associated_flight', lazy=True)

    def has_available_seats(self):
        return any(seat.seat_status == False for seat in self.plane.seats)

    def __str__(self):
        return f"Flight {self.flight_id} - Available seats: {self.has_available_seats()}"


class EconomyCard(db.Model):
    card_id = Column(Integer, primary_key=True, autoincrement=True)
    card_name = Column(String(255), nullable=False)
    baggage_check_in = Column(Boolean, default=False)
    baggage_hand_luggage = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    flight_id = Column(Integer, ForeignKey(Flight.flight_id), nullable=False)

    # Sửa backref thành 'economy_cards_associated' để tránh xung đột
    flight = relationship('Flight', backref='economy_cards_associated', lazy=True)

    def __str__(self):
        return f"Economy Card {self.card_name} - Price: {self.price} đ"




class Company(db.Model):
    com_id = Column(Integer, primary_key=True, autoincrement=True)
    com_name = Column(String(255), nullable=False)
    com_country = Column(String(255), nullable=False)


class Seat(db.Model):
    seat_id = Column(Integer, primary_key=True, autoincrement=True)
    seat_number = Column(Integer, nullable=False)
    seat_class = Column(SQLEnum(SeatClass), default=SeatClass.ECONOMY)
    seat_status = Column(Boolean, nullable=False, default=False)  # False = available, True = booked
    plane_id = Column(Integer, ForeignKey(Plane.plane_id), nullable=False)

    __table_args__ = (db.UniqueConstraint('plane_id', 'seat_number', name='uix_plane_seat_number'),)

    def __str__(self):
        return f"Seat {self.seat_number}"


class Ticket(db.Model):
    ticket_id = Column(Integer, primary_key=True, autoincrement=True)
    issue_date = Column(Date, nullable=False)
    departure_airport_id = Column(Integer, ForeignKey(Airport.airport_id), nullable=False)
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


class Booking(db.Model):
    booking_id = Column(Integer, primary_key=True, autoincrement=True)
    book_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    booking_status = Column(Boolean, nullable=False, default=False)  # False: chưa thanh toán, True: đã thanh toán
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    flight_id = Column(Integer, ForeignKey(Flight.flight_id), nullable=False)
    seat_id = Column(Integer, ForeignKey(Seat.seat_id), nullable=False)

    user = relationship('User', backref='bookings', lazy=True)
    flight = relationship('Flight', backref='bookings', lazy=True)
    seat = relationship('Seat', backref='bookings', lazy=True)

    def __str__(self):
        return f"Booking {self.booking_id} - User: {self.user.name} - Flight: {self.flight.flight_id} - Seat: {self.seat.seat_number}"





if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Tạo lại các bảng
