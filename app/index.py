from datetime import datetime

from sqlalchemy.orm import selectinload

from app import db
from flask import render_template, request, redirect, session, jsonify
import dao
from app import app, login
from flask_login import login_user, logout_user
from app.models import UserRole, Flight, Airport, FlightRoute, Plane, EconomyCard


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



@app.route('/flights', methods=['GET'])
def flights():
    # Lấy tất cả các chuyến bay và các thông tin liên quan
    flights = db.session.query(Flight) \
        .join(Plane) \
        .join(FlightRoute, Flight.flight_route_id == FlightRoute.fr_id) \
        .options(
        selectinload(Flight.economy_cards),  # Sử dụng selectinload để tải trước các Economy Cards
        selectinload(Flight.plane)  # Sử dụng selectinload để tải thông tin máy bay
    ).all()

    # Truyền dữ liệu vào template
    return render_template('booking.html', flights=flights)



@app.route('/search_flights', methods=['GET', 'POST'])
def search_flights():
    # Lấy các tham số lọc từ form
    flight_type = request.form.getlist('flight_type')  # Danh sách các loại chuyến bay
    dept_time = request.form.getlist('departure_time')  # Giờ cất cánh
    arr_time = request.form.getlist('arrival_time')  # Giờ hạ cánh

    # Xây dựng câu truy vấn để lọc chuyến bay
    flights_query = Flight.query.join(FlightRoute).join(Airport,
                                                        Airport.airport_id == FlightRoute.departure_airport_id).filter()

    if flight_type:
        flights_query = flights_query.filter(Flight.flight_type.in_(flight_type))

    if dept_time:
        # Xử lý lọc giờ cất cánh (ví dụ: 06:00 - 12:00)
        flights_query = flights_query.filter(Flight.f_dept_time.between(dept_time[0], dept_time[1]))

    if arr_time:
        # Xử lý lọc giờ hạ cánh
        flights_query = flights_query.filter(Flight.flight_arr_time.between(arr_time[0], arr_time[1]))

    flights = flights_query.all()

    # Trả về trang với kết quả chuyến bay
    return render_template('booking.html', flights=flights)


if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True)
