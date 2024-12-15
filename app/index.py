from datetime import datetime

import unicodedata
from sqlalchemy.orm import selectinload

from app import db
from flask import render_template, request, redirect, session, jsonify
import dao, utils
from app import app, login
from flask_login import login_user, logout_user
from app.models import UserRole, Flight, Airport, FlightRoute, Plane, Seat
from datetime import datetime
from sqlalchemy import func

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

    # print(departure_name)
    cities = ["Hồ Chí Minh", "Hà Nội", "Đà Nẵng", "Singapore", "Bangkok", "Taipei", "Seoul", "Tokyo"]

    airports = dao.load_airports()

    flights = dao.load_flights()

    return render_template('index.html', airports=airports, routes=routes, cities= cities, flights=flights)


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


    # Call the dao function to search for flights
    flights, error = dao.search_flights(departure, arrival, departure_date)

    # If there's an error (e.g., airports not found), return to index with error
    if error:
        return render_template('booking.html', airports=dao.load_airports(), error=error)

    # Return the results to the template
    return render_template('booking.html', flights=flights, airports=dao.load_airports())


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

if __name__ == '__main__':
    with app.app_context():
        from app import admin
        app.run(debug=True)
