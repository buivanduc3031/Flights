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

class Plane(db.Model):
    plane_id = Column(Integer, primary_key=True, autoincrement=True)
    plane_name = Column(String(255), nullable=False)
    total_seat = Column(Integer, nullable=False)
    company_id = Column(Integer, ForeignKey('company.com_id'), nullable=False)  # Khóa ngoại liên kết đến bảng Company
    seats = relationship('Seat', backref='plane', lazy=True, cascade="all, delete")

    company = relationship('Company', backref='planes', lazy=True)  # Mối quan hệ với Company

    def __str__(self):
        return self.plane_name


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

    def available_business_seats(self):
        return len(
            [seat for seat in self.plane.seats if seat.seat_class == SeatClass.BUSINESS and seat.seat_status == False])

    def available_economy_seats(self):
        return len(
            [seat for seat in self.plane.seats if seat.seat_class == SeatClass.ECONOMY and seat.seat_status == False])

    def __str__(self):
        return f"Flight {self.flight_id} - Available seats: Business: {self.available_business_seats()}, Economy: {self.available_economy_seats()}"



class FlightSchedule(db.Model):
    schedule_id = Column(Integer, primary_key=True, autoincrement=True)
    flight_id = Column(Integer, ForeignKey(Flight.flight_id), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)


class Booking(db.Model):
    booking_id = Column(Integer, primary_key=True, autoincrement=True)
    book_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    booking_status = Column(Boolean, nullable=False, default=False)  # False: chưa thanh toán, True: đã thanh toán
    group_size = Column(Integer, nullable=False, default=1)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    flight_id = Column(Integer, ForeignKey(Flight.flight_id), nullable=False)
    seat_id = Column(Integer, ForeignKey(Seat.seat_id), nullable=False)

    user = relationship('User', backref='bookings', lazy=True)
    flight = relationship('Flight', backref='bookings', lazy=True)
    seat = relationship('Seat', backref='bookings', lazy=True)

    def __str__(self):
        return f"Booking {self.booking_id} - User: {self.user.name} - Flight: {self.flight.flight_id} - Seat: {self.seat.seat_number} - Type: {self.seat.seat_type}"

class Luggage(db.Model):
    luggage_id = Column(Integer, primary_key=True, autoincrement=True)
    luggage_name = Column(String(255), nullable=False)
    weight = Column(Float, nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    flight_id = Column(Integer, ForeignKey(Flight.flight_id), nullable=False)

class Ticket(db.Model):
    ticket_id = Column(Integer, primary_key=True, autoincrement=True)
    issue_date = Column(Date, nullable=False)
    departure_airport_id = Column(Integer, ForeignKey(Airport.airport_id), nullable=False)
    ticket_price = Column(Float, nullable=False)
    ticket_status = Column(Boolean, nullable=False)
    ticket_gate = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    flight_id = Column(Integer, ForeignKey(Flight.flight_id), nullable=False)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Tạo lại các bảng

        user1 = User(name="Nguyễn Văn A", username="nguyenvana", password="password123", email="nguyenvana@example.com",
                     dob=datetime(1990, 1, 1), gender=True, user_role=UserRole.CUSTOMER)
        user2 = User(name="Trần Thị B", username="tranthib", password="password456", email="tranthib@example.com",
                     dob=datetime(1985, 5, 10), gender=False, user_role=UserRole.ADMIN)
        user3 = User(name="Lê Văn C", username="levanc", password="password789", email="levanc@example.com",
                     dob=datetime(2000, 3, 15), gender=True, user_role=UserRole.CUSTOMER)
        user4 = User(name="Phan Thị D", username="phanthid", password="password101", email="phanthid@example.com",
                     dob=datetime(1995, 7, 20), gender=False, user_role=UserRole.STAFF_MANAGE)
        user5 = User(name="Vũ Quang E", username="vuquange", password="password202", email="vuquange@example.com",
                     dob=datetime(1988, 12, 25), gender=True, user_role=UserRole.STAFF_TICKET)

        db.session.add_all([user1, user2, user3, user4, user5])
        db.session.commit()

        airport1 = Airport(airport_name="Sân bay Nội Bài", airport_address="Hà Nội, Việt Nam",
                           airport_image="https://link_to_image1.jpg")
        airport2 = Airport(airport_name="Sân bay Tân Sơn Nhất", airport_address="TP.HCM, Việt Nam",
                           airport_image="https://link_to_image2.jpg")
        airport3 = Airport(airport_name="Sân bay Đà Nẵng", airport_address="Đà Nẵng, Việt Nam",
                           airport_image="https://link_to_image3.jpg")
        airport4 = Airport(airport_name="Sân bay Cần Thơ", airport_address="Cần Thơ, Việt Nam",
                           airport_image="https://link_to_image4.jpg")
        airport5 = Airport(airport_name="Sân bay Phú Quốc", airport_address="Phú Quốc, Việt Nam",
                           airport_image="https://link_to_image5.jpg")

        db.session.add_all([airport1, airport2, airport3, airport4, airport5])
        db.session.commit()

        company1 = Company(com_name="Vietnam Airlines", com_country="Việt Nam")
        company2 = Company(com_name="Bamboo Airways", com_country="Việt Nam")
        company3 = Company(com_name="VietJet Air", com_country="Việt Nam")
        company4 = Company(com_name="Jetstar Pacific", com_country="Australia")
        company5 = Company(com_name="Cathay Pacific", com_country="Hong Kong")

        db.session.add_all([company1, company2, company3, company4, company5])
        db.session.commit()


        plane1 = Plane(plane_name="Boeing 737",total_seat=10, company_id=company1.com_id)  # Máy bay thuộc Vietnam Airlines
        plane2 = Plane(plane_name="Airbus A320",total_seat=15, company_id=company2.com_id)  # Máy bay thuộc Bamboo Airways
        plane3 = Plane(plane_name="Airbus A321",total_seat=5, company_id=company1.com_id)  # Máy bay thuộc Vietnam Airlines
        plane4 = Plane(plane_name="Boeing 777",total_seat=20, company_id=company2.com_id)  # Máy bay thuộc Bamboo Airways
        plane5 = Plane(plane_name="Boeing 787",total_seat=25, company_id=company1.com_id)  # Máy bay thuộc Vietnam Airlines

        # Thêm tất cả các máy bay vào cơ sở dữ liệu
        db.session.add_all([plane1, plane2, plane3, plane4, plane5])
        db.session.commit()

        seat1 = Seat(seat_number=1, seat_class=SeatClass.ECONOMY, seat_status=False, plane_id=1)
        seat2 = Seat(seat_number=2, seat_class=SeatClass.ECONOMY, seat_status=False, plane_id=1)
        seat3 = Seat(seat_number=3, seat_class=SeatClass.ECONOMY, seat_status=False, plane_id=1)
        seat4 = Seat(seat_number=4, seat_class=SeatClass.ECONOMY, seat_status=True, plane_id=1)
        seat5 = Seat(seat_number=5, seat_class=SeatClass.ECONOMY, seat_status=True, plane_id=1)
        seat6 = Seat(seat_number=6, seat_class=SeatClass.ECONOMY, seat_status=True, plane_id=1)
        seat7 = Seat(seat_number=7, seat_class=SeatClass.ECONOMY, seat_status=False, plane_id=1)
        seat8 = Seat(seat_number=8, seat_class=SeatClass.BUSINESS, seat_status=True, plane_id=1)
        seat9 = Seat(seat_number=9, seat_class=SeatClass.BUSINESS, seat_status=False, plane_id=1)
        seat10 = Seat(seat_number=10, seat_class=SeatClass.BUSINESS, seat_status=False, plane_id=1)

        seat11 = Seat(seat_number=1, seat_class=SeatClass.ECONOMY, seat_status=False, plane_id=2)
        seat12 = Seat(seat_number=2, seat_class=SeatClass.ECONOMY, seat_status=False, plane_id=2)
        seat13 = Seat(seat_number=3, seat_class=SeatClass.ECONOMY, seat_status=False, plane_id=2)
        seat14 = Seat(seat_number=4, seat_class=SeatClass.ECONOMY, seat_status=True, plane_id=2)
        seat15 = Seat(seat_number=5, seat_class=SeatClass.ECONOMY, seat_status=True, plane_id=2)
        seat16 = Seat(seat_number=6, seat_class=SeatClass.ECONOMY, seat_status=True, plane_id=2)
        seat17 = Seat(seat_number=7, seat_class=SeatClass.ECONOMY, seat_status=False, plane_id=2)
        seat18 = Seat(seat_number=8, seat_class=SeatClass.BUSINESS, seat_status=True, plane_id=2)
        seat19 = Seat(seat_number=9, seat_class=SeatClass.BUSINESS, seat_status=True, plane_id=2)
        seat20 = Seat(seat_number=10, seat_class=SeatClass.BUSINESS, seat_status=True, plane_id=2)



        db.session.add_all([seat1, seat2, seat3, seat4,seat5,seat6,seat7,seat8,seat9,seat10,seat11, seat12, seat13, seat14,seat15,seat16,seat17,seat18,seat19,seat20])
        db.session.commit()


        flight_route1 = FlightRoute(departure_airport_id=airport1.airport_id, arrival_airport_id=airport2.airport_id,
                                    distance=1000.0, description="Direct flight from Hanoi to Ho Chi Minh City")
        flight_route2 = FlightRoute(departure_airport_id=airport2.airport_id, arrival_airport_id=airport3.airport_id,
                                    distance=500.0, description="One stop flight from Ho Chi Minh City to Da Nang")
        flight_route3 = FlightRoute(departure_airport_id=airport3.airport_id, arrival_airport_id=airport4.airport_id,
                                    distance=400.0, description="Multiple stop flight from Da Nang to Can Tho")
        flight_route4 = FlightRoute(departure_airport_id=airport4.airport_id, arrival_airport_id=airport5.airport_id,
                                    distance=800.0, description="Direct flight from Can Tho to Phu Quoc")
        flight_route5 = FlightRoute(departure_airport_id=airport1.airport_id, arrival_airport_id=airport5.airport_id,
                                    distance=1200.0, description="One stop flight from Hanoi to Phu Quoc")

        db.session.add_all([flight_route1, flight_route2, flight_route3, flight_route4, flight_route5])
        db.session.commit()

        flight1 = Flight(f_dept_time=datetime(2024, 12, 20, 10, 0), flight_arr_time=datetime(2024, 12, 20, 12, 30),
                         flight_duration=2.5, flight_price=100.0, flight_type=FlightType.DIRECT, flight_route_id=1,
                         plane_id=1)
        flight2 = Flight(f_dept_time=datetime(2024, 12, 21, 8, 15), flight_arr_time=datetime(2024, 12, 21, 10, 45),
                         flight_duration=2.5, flight_price=120.0, flight_type=FlightType.ONE_STOP, flight_route_id=2,
                         plane_id=2)
        flight3 = Flight(f_dept_time=datetime(2024, 12, 22, 15, 30), flight_arr_time=datetime(2024, 12, 22, 17, 30),
                         flight_duration=2.0, flight_price=150.0, flight_type=FlightType.MULTIPLE_STOP,
                         flight_route_id=3, plane_id=3)
        flight4 = Flight(f_dept_time=datetime(2024, 12, 23, 6, 0), flight_arr_time=datetime(2024, 12, 23, 8, 30),
                         flight_duration=2.5, flight_price=90.0, flight_type=FlightType.DIRECT, flight_route_id=4,
                         plane_id=4)
        flight5 = Flight(f_dept_time=datetime(2024, 12, 24, 12, 0), flight_arr_time=datetime(2024, 12, 24, 14, 30),
                         flight_duration=2.5, flight_price=110.0, flight_type=FlightType.ONE_STOP, flight_route_id=5,
                         plane_id=5)

        db.session.add_all([flight1, flight2, flight3, flight4, flight5])
        db.session.commit()

        booking1 = Booking(book_date=datetime.now(timezone.utc), booking_status=True, group_size=2, user_id=user1.id,
                           flight_id=flight1.flight_id, seat_id=seat1.seat_id)
        booking2 = Booking(book_date=datetime.now(timezone.utc), booking_status=False, group_size=1, user_id=user2.id,
                           flight_id=flight2.flight_id, seat_id=seat2.seat_id)
        booking3 = Booking(book_date=datetime.now(timezone.utc), booking_status=True, group_size=3, user_id=user3.id,
                           flight_id=flight3.flight_id, seat_id=seat3.seat_id)
        booking4 = Booking(book_date=datetime.now(timezone.utc), booking_status=False, group_size=1, user_id=user4.id,
                           flight_id=flight4.flight_id, seat_id=seat4.seat_id)
        booking5 = Booking(book_date=datetime.now(timezone.utc), booking_status=True, group_size=2, user_id=user5.id,
                           flight_id=flight5.flight_id, seat_id=seat2.seat_id)

        db.session.add_all([booking1, booking2, booking3, booking4, booking5])
        db.session.commit()
