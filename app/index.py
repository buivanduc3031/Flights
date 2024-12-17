import math

import unicodedata

from flask import render_template, request, redirect, session, jsonify
import dao, utils
from app import app, login
from flask_login import login_user, logout_user

from app.dao import count_flights
from app.models import UserRole, Seat, Flight
from datetime import datetime


def remove_accents(input_str):
    return ''.join(
        c for c in unicodedata.normalize('NFD', input_str)
        if unicodedata.category(c) != 'Mn'
    )

@app.route("/")
def index():
        departure_name = request.args.get('departure', 'Ho Chi Minh')
        departure_name = remove_accents(departure_name)


        routes = dao.get_popular_routes(departure_name)

        cities = ["Hồ Chí Minh", "Hà Nội", "Đà Nẵng", "Singapore", "Bangkok", "Taipei", "Seoul", "Tokyo"]

        airports = dao.load_airports()


        page = request.args.get('page', 1)
        page = int(page)

        flights = dao.get_flights(page)
        flights_counter = dao.count_flights()
        total_pages = math.ceil(flights_counter / app.config['PAGE_SIZE'])

        return render_template(
            'index.html',
            airports=airports,
            routes=routes,
            cities=cities,
            flights=flights,
            departure_name=departure_name,
            pages=total_pages,
        )


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

    airports = dao.load_airports()

    return render_template('booking.html',airports=airports)


@app.route('/search', methods=['GET'])
def search_flights_route():
    # Lấy thông tin từ yêu cầu
    departure = request.args.get('departure')
    arrival = request.args.get('arrival')
    departure_date = request.args.get('departure_date')
    adult_count = int(request.args.get('adult_count', 1))
    child_count = int(request.args.get('child_count', 0))
    infant_count = int(request.args.get('infant_count', 0))

    total_passengers = adult_count + child_count + infant_count

    # Gọi hàm tìm chuyến bay
    flights_result, error = dao.search_flights(departure, arrival, departure_date,total_passengers )

    if error:
        return render_template('booking.html', airports=dao.load_airports(), error=error)

    return render_template('booking.html', flights=flights_result, airports=dao.load_airports(),total_passengers=total_passengers)


@app.route("/api/carts", methods=['post'])
def add_to_cart():
    cart = session.get('cart')


    if not cart:
        cart = {}
        print(request.json)
        id = str(request.json.get('id'))
        flight_number = request.json.get('flight_number')
        departure = request.json.get('departure')
        arrival = request.json.get('arrival')
        price = request.json.get('price')
    if id in cart:
        cart[id]['quantity'] += 1
    else:
        cart[id] = {"id": id, "flight_number": flight_number, "departure": departure,
                    "arrival": arrival, "price": price, "quantity": 1}
    session['cart'] = cart
    print(session['cart'])

    return jsonify(utils.cart_stats(cart))

@app.route("/cart")
def cart_view():
    return render_template('cart.html')

@app.context_processor
def common_response_data():
    return {
        # 'categories': dao.load_categories(),
        'cart_stats': utils.cart_stats(session.get('cart'))
    }


@app.route("/flight_details/<int:flight_id>")
def flight_details(flight_id):
    flight = Flight.query.get(flight_id)

    if flight:
        # Lấy các thông tin từ chuyến bay và các bảng liên quan
        plane_name = flight.plane.plane_name
        company_name = flight.plane.company.com_name
        departure_time = flight.f_dept_time.strftime('%H:%M')
        arrival_time = flight.flight_arr_time.strftime('%H:%M')
        flight_duration = flight.flight_duration
        flight_price = flight.flight_price

        # Truyền dữ liệu vào template
        return render_template(
            'flight_details.html',
            plane_name=plane_name,
            company_name=company_name,
            departure_time=departure_time,
            arrival_time=arrival_time,
            flight_duration=flight_duration,
            flight_price=flight_price
        )
    else:
        return "Flight not found", 404


if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)
