from app.models import User, Airport, FlightRoute, Flight, Company
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