from datetime import datetime

from sqlalchemy.orm import selectinload

from app import db
from flask import render_template, request, redirect, session, jsonify
import dao
from app import app, login
from flask_login import login_user, logout_user
from app.models import UserRole, Flight, Airport, FlightRoute, Plane, Seat, Booking
from datetime import datetime
from sqlalchemy import func


@app.route("/")
def index():
    # flights = dao.show_flights()
    # print(flights)

    airports = dao.load_airports()

    return render_template('index.html', airports=airports)


@app.route('/register', methods=['get', 'post'])
def register_process():
    err_msg = ''
    if request.method.__eq__('POST'):
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        if password.__eq__(confirm):
            data = request.form.copy()
            del data['confirm']

            gender = data.get('gender', '').lower()
            data['gender'] = True if gender == 'male' else False

            dob = data.get('dob')
            try:
                if dob:
                    data['dob'] = datetime.strptime(dob, '%Y-%m-%d').date()
                else:
                    err_msg = 'Ngày sinh không được bỏ trống.'
                    return render_template('register.html', err_msg=err_msg)
            except ValueError:
                err_msg = 'Định dạng ngày sinh không hợp lệ. Vui lòng nhập theo định dạng YYYY-MM-DD.'
                return render_template('register.html', err_msg=err_msg)

            dao.add_user(avatar=request.files.get('avatar'), **data)
            return redirect('/login')
        else:
            err_msg = 'Mật khẩu không khớp!'

    return render_template('register.html', err_msg=err_msg)


@app.route("/login", methods=['get', 'post'])
def login_process():
    if request.method.__eq__("POST"):
        username = request.form.get('username')
        password = request.form.get('password')
        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user)
            return redirect('/')

    return render_template('login.html')


@app.route("/logout")
def logout_process():
    logout_user()
    return redirect('/login')


@app.route("/login-admin", methods=['post'])
def login_admin_process():
    if request.method.__eq__("POST"):
        username = request.form.get('username')
        password = request.form.get('password')
        user = dao.auth_user(username=username, password=password, role=UserRole.ADMIN)
        if user:
            login_user(user)
            return redirect('/admin')


@login.user_loader
def get_user_by_id(user_id):
    return dao.get_user_by_id(user_id)



@app.route('/booking', methods=['GET'])
def flights():
    # Lấy tất cả các chuyến bay và các thông tin liên quan
    airports = dao.load_airports()
    # Truyền dữ liệu vào template
    return render_template('booking.html',airports=airports)






@app.route('/search', methods=['GET'])
def search_flights():
    # Capture form data from the request
    departure = request.args.get('departure')
    arrival = request.args.get('arrival')
    departure_date = request.args.get('departure_date')
    return_date = request.args.get('return_date')

    adult_count = request.args.get('adult-count')
    child_count = request.args.get('child-count')
    infant_count = request.args.get('infant-count')

    # Convert departure_date to a datetime object
    departure_date_obj = datetime.strptime(departure_date, '%Y-%m-%d').date() if departure_date else None

    # Query the Airport model to get the departure and arrival airports based on user input
    departure_airport = Airport.query.filter_by(airport_name=departure).first()
    arrival_airport = Airport.query.filter_by(airport_name=arrival).first()

    # Check if airports were found
    if not departure_airport or not arrival_airport:
        # If no airports found, return an error message or redirect
        return render_template('booking.html', airports=dao.load_airports(), error="Airport not found")

    # Query FlightRoute model to get the flight routes based on departure and arrival airports
    flight_routes = FlightRoute.query.filter(
        FlightRoute.departure_airport_id == departure_airport.airport_id,
        FlightRoute.arrival_airport_id == arrival_airport.airport_id
    ).all()

    # Query Flight model based on the filtered routes and the departure date
    flights = Flight.query.filter(
        Flight.flight_route_id.in_([route.fr_id for route in flight_routes]),
        func.date(Flight.f_dept_time) == departure_date_obj  # Compare only the date part of f_dept_time
    ).all()

    # Return the results to the template along with airports
    return render_template('booking.html', flights=flights, airports=dao.load_airports())




if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)
