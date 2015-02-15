from flask import Flask, url_for, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy, Model
import flask_admin as admin
import flask_login as login
from flask_admin import helpers, expose
from flask_admin.contrib import sqla
from flask_babelex import Babel, gettext
from wtforms import form, fields, validators
from werkzeug.security import generate_password_hash, check_password_hash
import os.path


# Create application
app = Flask(__name__)
#app.config['BABEL_DEFAULT_LOCALE'] = 'de_DE' # Let's make Wolfgang Severing as happy as practicable!
app.config['BABEL_DEFAULT_LOCALE'] = 'en' # Makes debugging easier!
babel = Babel(app)


# Create dummy secret key so we can use sessions
app.config['SECRET_KEY'] = 'I am not actually secret. Fix me before deployment!'

# Create in-memory database
db_path = 'db.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


# Flask views
@app.route('/')
def index():
    return '<a href="/admin/">Click me to get to Admin!</a>'


### RUDIMENTARY USER MANAGEMENT

# Define login form for flask-login
class LoginForm(form.Form):
    login = fields.TextField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')

        # we're comparing the plaintext pw with the the hash from the db
        if not check_password_hash(user.password, self.password.data):
        # to compare plain text passwords use
        # if user.password != self.password.data:
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        return db.session.query(User).filter_by(login=self.login.data).first()


# Initialize flask-login
def init_login():
    login_manager = login.LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)


### VIEW BASE CLASSES

class AdminView(sqla.ModelView):
    def is_accessible(self):
        return login.current_user.is_authenticated() and login.current_user.is_admin

class UserView(sqla.ModelView):
    def is_accessible(self):
        return login.current_user.is_authenticated()




### USER

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(64))
    is_admin = db.Column(db.Boolean(), default=False)

    def __init__(self, login=None, password=None):
        self.chair = None
        self.semester = None
        if login:
            self.login = login
        if password:
            self.password = generate_password_hash(password)

    def __str__(self):
        return self.login

    # Flask-Login integration
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

class UserAdmin(AdminView):
    column_display_pk = True
    form_columns = ['id', 'login', 'is_admin', 'email', 'password']

# class UserUser(UserView):
#     form_columns = ['login', 'email', 'password']
#     def scaffold_sortable_columns(self):
#         return {}
#     def init_search(self):
#         return False
#     # def scaffold_form(self):
#     #     converter = self.model_form_converter(self.session, self)
#     #     form_class = form.get_form(self.model, converter,
#     #                                base_class=self.form_base_class,
#     #                                only=self.form_columns,
#     #                                exclude=self.form_excluded_columns,
#     #                                field_args=self.form_args,
#     #                                extra_fields=self.form_extra_fields)
#     #
#     #     if self.inline_models:
#     #         form_class = self.scaffold_inline_form_models(form_class)
#     #     return form_class
#     def get_list(self, page, sort_column, sort_desc, search, filters, execute=True):
#         user = login.current_user
#         if user.is_authenticated:
#             return 1, (user,)
#         else:
#             return 0, ()
#     def get_one(self, id):
#         user = login.current_user
#         if user.is_authenticated and user.id == id:
#             return user
#         else:
#             return None
#     def create_model(self, form):
#         return False
#     def update_model(self, form, model):
#         # XXX: Possible privilege escalation!
#         # We must check that users don't try to make themselves admins!
#         try:
#             form.populate_obj(model)
#             self._on_model_change(form, model, False)
#             self.session.commit()
#         except Exception as ex:
#             if not self.handle_view_exception(ex):
#                 flash(gettext('Failed to update record. %(error)s', error=str(ex)), 'error')
#                 log.exception('Failed to update record.')
#
#             self.session.rollback()
#
#             return False
#         else:
#             self.after_model_change(form, model, False)
#
#         return True
#     def delete_model(self, model):
#         return False
#     def scaffold_filters(self, name):
#         return []
#     def get_count_query(self):
#         user = login.current_user
#         if user.is_authenticated:
#             return 1
#         else:
#             return 0

### SEMESTER

class Semester(db.Model):
    __tablename__ = 'semester'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(7))
    def __str__(self):
        return self.code

class SemesterAdmin(AdminView):
    column_display_pk = True
    form_columns = ['id', 'code']



### CHAIR / PROFESSUR

class Chair(db.Model):
    __tablename__ = 'chair'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64))
    def __str__(self):
        return self.name

class ChairAdmin(AdminView):
    column_display_pk = True
    form_columns = ['id', 'name']



### COURSE / LEHRANGEBOT

class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128))
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'))
    semester = db.relationship('Semester', backref='courses')
    chair_id = db.Column(db.Integer, db.ForeignKey('chair.id'))
    chair = db.relationship('Chair', backref='courses')
    def __str__(self):
        return '{} {}'.format(self.short_name, self.semester)

class CourseAdmin(AdminView):
    column_display_pk = True
    form_columns = ['id', 'semester', 'chair', 'name']



### COURSE OF STUDIES / STUDIENGANG

class CourseOfStudies(db.Model):
    __tablename__ = 'course_of_studies'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200))
    short_name = db.Column(db.String(40))
    def __str__(self):
        return self.short_name

class CourseOfStudiesAdmin(AdminView):
    column_display_pk = True
    form_columns = ['id', 'short_name', 'name']



### COHORT / KOHORTE

class Cohort(db.Model):
    __tablename__ = 'cohort'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_of_studies_id = db.Column(db.Integer, db.ForeignKey('course_of_studies.id'))
    course_of_studies = db.relationship('CourseOfStudies', backref='cohorts')
    study_semester = db.Column(db.Integer)
    def __str__(self):
        if self.study_semester == 1:
            th = 'st'
        elif self.study_semester == 2:
            th = 'nd'
        else:
            th = 'th'
        return '{}{} study semester of {}'.format(self.study_semester, th, self.course_of_studies)

class CohortAdmin(AdminView):
    column_display_pk = True
    form_columns = ['id', 'course_of_studies', 'study_semester']




### ADMIN VIEWS

# Create customized index view class that handles login
class MyAdminIndexView(admin.AdminIndexView):

    @expose('/')
    def index(self):
        if not login.current_user.is_authenticated():
            return redirect(url_for('.login_view'))
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if helpers.validate_form_on_submit(form):
            user = form.get_user()
            login.login_user(user)

        if login.current_user.is_authenticated():
            return redirect(url_for('.index'))
        self._template_args['form'] = form
        return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        login.logout_user()
        return redirect(url_for('.index'))


# Initialize flask-login
init_login()

# Create admin
admin = admin.Admin(app, 'Abrakadabra', index_view=MyAdminIndexView(), base_template='my_master.html')

admin.add_view(UserAdmin(User, db.session, category='Database'))
admin.add_view(SemesterAdmin(Semester, db.session, category='Database'))
admin.add_view(ChairAdmin(Chair, db.session, category='Database'))
admin.add_view(CourseAdmin(Course, db.session, category='Database'))
admin.add_view(CourseOfStudiesAdmin(CourseOfStudies, db.session, category='Database'))
admin.add_view(CohortAdmin(Cohort, db.session, category='Database'))



def build_sample_db():
    db.create_all()
    # passwords are hashed, to use plaintext passwords instead:
    # test_user = User(login="test", password="test")
    user = User(login='admin', password='admin')
    user.is_admin = True
    db.session.add(user)
    user = User(login='user', password='user')
    db.session.add(user)
    db.session.commit()


if __name__ == '__main__':

    if not os.path.exists(db_path):
        db.create_all()
        build_sample_db()
    else:
        db.create_all()


    # Start app
    app.run(debug=True)


from flask_admin.model import BaseModelView
