from sqlalchemy import func
from sqlalchemy.orm import aliased, selectinload

from app.models import User, Airport, FlightRoute, Flight, Company, Plane, Seat
from app import app, db
import hashlib
import cloudinary.uploader
from datetime import datetime

def get_user_by_id(id):
    return User.query.get(id)


def auth_user(username, password, role = None):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    u = User.query.filter(User.username.__eq__(username.strip()),
                             User.password.__eq__(password))
    if role:
        u = u.filter(User.user_role.__eq__(role))

    return u.first()


def add_user(name, username, password, email, dob, gender, avatar):

    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    gender_bool = True

    if isinstance(dob, str):
        try:
            dob_obj = datetime.strptime(dob, '%Y-%m-%d')
            dob = dob_obj.strftime('%d-%m-%Y')
        except ValueError:
            raise ValueError("Ngày sinh không hợp lệ. Định dạng phải là YYYY-MM-DD.")
    u = User(name=name.strip(), username=username.strip(), password=password, email=email.strip(),dob=dob,gender=gender_bool)

    if avatar:
        res = cloudinary.uploader.upload(avatar)
        u.avatar = res.get('secure_url')

    db.session.add(u)
    db.session.commit()


def load_airports():
    return Airport.query.all()

def load_flight_routes():
    return FlightRoute.query.all()

def get_airport_by_id(id):
    return Airport.query.get(id)

def load_flights():
    return Flight.query.all()


def show_flights():
    # Truy vấn danh sách chuyến bay và thông tin liên quan
    flights = db.session.query(
        Flight.flight_id,
        Flight.f_dept_time,
        Flight.flight_arr_time,
        Flight.flight_price,
        FlightRoute.departure_airport_id,
        FlightRoute.arrival_airport_id,
        Airport.airport_name.label('departure_airport_name'),
        Airport.airport_image.label('departure_airport_image'),
        Company.com_name.label('company_name')
    ).join(FlightRoute, Flight.flight_route_id == FlightRoute.fr_id) \
        .join(Airport, Airport.airport_id == FlightRoute.departure_airport_id) \
        .join(Company, Company.com_id == FlightRoute.departure_airport_id) \
        .limit(10).all()
    return flights


def get_popular_routes(departure_name=None):
    # Alias cho bảng airport
    arrival_airport = db.aliased(Airport)

    # Truy vấn cơ bản
    query = db.session.query(
        FlightRoute.fr_id,
        Airport.airport_name.label('departure'),
        arrival_airport.airport_name.label('arrival'),
        arrival_airport.airport_image.label('image'),
        FlightRoute.description
    ).join(
        Airport, FlightRoute.departure_airport_id == Airport.airport_id
    ).join(
        arrival_airport, FlightRoute.arrival_airport_id == arrival_airport.airport_id
    )

    # Lọc theo tên sân bay nếu `departure_name` được cung cấp
    if departure_name:
        query = query.filter(Airport.airport_address.ilike(f"%{departure_name}%"))

    return query.all()


def load_flights():

    flights = db.session.query(Flight) \
        .join(Plane) \
        .join(FlightRoute, Flight.flight_route_id == FlightRoute.fr_id) \
        .options(
        selectinload(Flight.plane)  # Sử dụng selectinload để tải thông tin máy bay
    ).all()

    return flights

def search_flights(departure, arrival, departure_date):
    # Query the Airport model for departure and arrival airports
    departure_airport = Airport.query.filter_by(airport_name=departure).first()
    arrival_airport = Airport.query.filter_by(airport_name=arrival).first()

    if not departure_airport or not arrival_airport:
        return None, "Airport not found"

    # Query FlightRoute model for matching routes
    flight_routes = FlightRoute.query.filter(
        FlightRoute.departure_airport_id == departure_airport.airport_id,
        FlightRoute.arrival_airport_id == arrival_airport.airport_id
    ).all()

    if not flight_routes:
        return [], None  # No matching routes

    # Query Flight model for flights on the specified date
    departure_date_obj = datetime.strptime(departure_date, '%Y-%m-%d').date() if departure_date else None
    flights = Flight.query.filter(
        Flight.flight_route_id.in_([route.fr_id for route in flight_routes]),
        func.date(Flight.f_dept_time) == departure_date_obj
    ).all()

    return flights, None

