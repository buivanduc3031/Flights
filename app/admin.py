from app import db, app
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from app.models import User, UserRole, Flight, FlightRoute, Airport, Plane, Ticket, Luggage
from flask_login import current_user, logout_user
from flask_admin import BaseView, expose
from flask import redirect

class AuthenticatedView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

# class AdminView(AuthenticatedView):
#     can_export = True
#     column_searchable_list = ['id', 'name']
#     column_filters = ['id', 'name']
#     can_view_details = True



class MyView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated


class LogoutView(MyView):
    @expose("/")
    def index(self):
        logout_user()
        return redirect('/admin')


class StatsView(MyView):
    @expose("/")
    def index(self):

        return self.render('admin/stats.html')


admin = Admin(app, name='ecourseapp', template_mode='bootstrap4')


admin.add_view(ModelView(Flight, db.session))
admin.add_view(ModelView(FlightRoute, db.session))
admin.add_view(ModelView(Plane, db.session))
# admin.add_view(ModelView(Airport, db.session))
# admin.add_view(ModelView(Ticket, db.session))
# admin.add_view(ModelView(Luggage, db.session))
# admin.add_view(AuthenticatedView(User, db.session))
# admin.add_view(StatsView(name = 'Thống kê báo cáo'))
admin.add_view(LogoutView(name = "Đăng xuất"))

