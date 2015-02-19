from flask import Flask, url_for, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy, Model
from sqlalchemy import Table, Sequence
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
    form_widget_args = {
        'id': {
            'disabled': True
        }
    }
    def __init__(self, model, session=db.session, name=None, category='Database', endpoint=None, url=None):
        basename = self.__class__.__name__[:-len('AdminView')]
        if not name:
            name = basename + ' (Admin)'
        if not endpoint:
            endpoint = basename.lower() + '_admin'
        if not url:
            url = '/admin/db/{}'.format(basename.lower())
        sqla.ModelView.__init__(self, model, session, name=name, category=category, endpoint=endpoint, url=url)
    def is_accessible(self):
        return login.current_user.is_authenticated() and login.current_user.is_admin

class UserView(sqla.ModelView):
    form_widget_args = {
        'id': {
            'disabled': True
        }
    }
    def __init__(self, model, session=db.session, name=None, category=None, endpoint=None, url=None):
        basename = self.__class__.__name__[:-len('UserView')]
        if not name:
            name = basename
        if not endpoint:
            endpoint = basename.lower() + '_user'
        if not url:
            url = '/admin/{}'.format(basename.lower())
        sqla.ModelView.__init__(self, model, session, name=name, category=category, endpoint=endpoint, url=url)
    def is_accessible(self):
        return login.current_user.is_authenticated()



# class UserView2(admin.BaseView):
#     def __init__(self, name=None, category=None, url=None):
#         if not name:
#             name = self.__class__.__name__[:-len('UserView2')]
#         if not url:
#             url = self.__class__.__name__[:-len('UserView2')].lower()
#         admin.BaseView.__init__(self, name=name, category=category, url=url)
#     def is_accessible(self):
#         return login.current_user.is_authenticated()




### JOIN TABLES

jt_cohort_course = Table('jt_cohort_course', db.Model.metadata,
                             db.Column('cohort_id', db.Integer, db.ForeignKey('cohort.id')),
                             db.Column('course_id', db.Integer, db.ForeignKey('course.id'))
                         )


###
### From here on follows a long list of entities (classes of database-backed objects), each with an admin interface
###

### USER

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=True)
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

class UserAdminView(AdminView):
    column_display_pk = True
    form_columns = ['id', 'login', 'is_admin', 'email', 'password']

### SEMESTER

class Semester(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    name = db.Column(db.String(7))
    #courses = db.relationship('Course', backref='semester')
    def __init__(self, name, id=None):
        self.id=id
        self.name=name
    def __str__(self):
        return self.name

class SemesterAdminView(AdminView):
    column_display_pk = True
    form_columns = ['id', 'name', 'courses']

class SemesterUserView(UserView):
    column_display_pk = False
    form_columns = ['id', 'name', 'courses']
    can_create = False
    can_edit = True
    can_delete = False
    form_widget_args = {
        'id': {
            'disabled': True
        },
        'name': {
            'disabled': True
        },
        'courses': {
            'disabled': True
        }
    }



### CHAIR / PROFESSUR

class Chair(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    name = db.Column(db.String(64))
    def __str__(self):
        return self.name

class ChairAdminView(AdminView):
    column_display_pk = True
    form_columns = ['id', 'name']

class ChairUserView(UserView):
    column_display_pk = True
    form_columns = ['id', 'name']
    can_create = False
    can_edit = False
    can_delete = False



### COURSE / LEHRANGEBOT

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    name = db.Column(db.String(128))
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'))
    semester = db.relationship('Semester', backref='courses')
    chair_id = db.Column(db.Integer, db.ForeignKey('chair.id'))
    chair = db.relationship('Chair', backref='courses')
    cohorts = db.relationship('Cohort', secondary=jt_cohort_course, backref='course')
    def __str__(self):
        return '{} {}'.format(self.name, self.semester)

class CourseAdminView(AdminView):
    column_display_pk = True
    form_columns = ['id', 'semester', 'chair', 'name', 'cohorts']

class CourseUserView(UserView):
    column_display_pk = True
    form_columns = ['semester', 'chair', 'name', 'cohorts']
    form_widget_args = {
        'semester': {
            'disabled': True
        }
    }



### PROGRAM / STUDIENGANG

class Program(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    name = db.Column(db.String(200))
    short_name = db.Column(db.String(40))
    def __str__(self):
        return self.short_name

class ProgramAdminView(AdminView):
    column_display_pk = True
    form_columns = ['id', 'short_name', 'name']

class ProgramUserView(UserView):
    column_display_pk = True
    form_columns = ['id', 'short_name', 'name']
    can_create = False
    can_edit = False
    can_delete = False



### COHORT / KOHORTE

class Cohort(db.Model):
    __tablename__ = 'cohort'
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    program_id = db.Column(db.Integer, db.ForeignKey('program.id'))
    program = db.relationship('Program', backref='cohorts')
    study_semester = db.Column(db.Integer)
    courses = db.relationship('Course', secondary=jt_cohort_course, backref='cohort')
    def __str__(self):
        if self.study_semester == 1:
            th = 'st'
        elif self.study_semester == 2:
            th = 'nd'
        else:
            th = 'th'
        return '{} {}{} semester'.format(self.program, self.study_semester, th)

class CohortAdminView(AdminView):
    column_display_pk = True
    form_columns = ['id', 'program', 'study_semester', 'courses']

class CohortUserView(UserView):
    column_display_pk = True
    form_columns = ['id', 'program', 'study_semester', 'courses']
    can_create = False
    can_edit = False
    can_delete = False


###
### With all entities defined, we now come to user views. Most of them do not directly correspond to a particular
### entity.
###

# class CourseUserView(UserView):
#     @admin.expose('/')
#     def index(self):
#         print("***")
#         return self.render('course.html')
#





### CENTRAL 'ADMIN' VIEW
### (We are actually using it for normal users as well.)

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

# Create admin interface
adminInterface = admin.Admin(app, 'Abrakadabra', index_view=MyAdminIndexView(), base_template='my_master.html')

# Views for all users
adminInterface.add_view(CourseUserView(Course))
adminInterface.add_view(SemesterUserView(Semester))
adminInterface.add_view(ChairUserView(Chair))
adminInterface.add_view(ProgramUserView(Program))
adminInterface.add_view(CohortUserView(Cohort))

# Additional views for admins
adminInterface.add_view(UserAdminView(User))
adminInterface.add_view(SemesterAdminView(Semester))
adminInterface.add_view(ChairAdminView(Chair))
adminInterface.add_view(CourseAdminView(Course))
adminInterface.add_view(ProgramAdminView(Program))
adminInterface.add_view(CohortAdminView(Cohort))

relevant_semester = 23 # TODO: compute from current date, and make sure this semester and all previous ones exist!

######################################################################################################################
######################################################################################################################
######################################################################################################################

# Building/importing the initial database

def build_db():
    db.create_all()

    # USERS

    user = User(login='admin', password='admin')
    user.is_admin = True
    db.session.add(user)
    user = User(login='user', password='user')
    db.session.add(user)
    db.session.commit()

    # SEMESTERS

    for id in range(1, relevant_semester+3):
        semesterType = 'SS' if id%2==1 else 'WS'
        year = 2004 + int((id-1)/2)
        semester = Semester(id=id, name='{} {}'.format(semesterType, year))
        db.session.add(semester)
    db.session.commit()

if not os.path.exists(db_path):
    db.create_all()
    build_db()
else:
    db.create_all()

######################################################################################################################
######################################################################################################################
######################################################################################################################



# Start app
app.run(debug=True)


from flask_admin.model import BaseModelView
