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
import datetime
from sqlalchemy.dialects.mysql import LONGTEXT
from threading import Thread
from time import sleep

# Create application
app = Flask(__name__)
#app.config['BABEL_DEFAULT_LOCALE'] = 'de_DE' # Let's make Wolfgang Severing as happy as practicable!
app.config['BABEL_DEFAULT_LOCALE'] = 'en' # Makes debugging easier!
babel = Babel(app)


# Create dummy secret key so we can use sessions
app.config['SECRET_KEY'] = 'I am not actually secret. Fix me before deployment!'

# Create in-memory database
#db_path = 'db.sqlite'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:cognitivesystems@localhost/pokus'
#app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


# Flask views
@app.route('/')
def index():
    return 'Aus technischen Gründen befindet sich die Einstiegsseite <a href="/admin/">hier.</a>'


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
    column_display_pk = True
    form_widget_args = {
        'id': {
            'disabled': True
        }
    }
    def __init__(self, model, session=db.session, name=None, category='Direct database access', endpoint=None, url=None):
        basename = self.__class__.__name__[:-len('AdminView')]
        if not name:
            name = basename + ' (Admin)'
        if not endpoint:
            endpoint = basename.lower() + '_admin'
        if not url:
            url = '/admin/db/{}'.format(basename.lower())
        sqla.ModelView.__init__(self, model, session, name=name, category=category, endpoint=endpoint, url=url)
    def is_accessible(self):
        return login.current_user.is_authenticated() and login.current_user.admin

class UserView(sqla.ModelView):
    column_display_pk = False
    form_widget_args = {
        'id': {
            'disabled': True
        }
    }
    can_create = False
    can_edit = False
    can_delete = False
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

jt_chair_employee = Table('jt_chair_person', db.Model.metadata,
    db.Column('chair_id', db.Integer, db.ForeignKey('chair.id')),
    db.Column('employee_id', db.Integer, db.ForeignKey('employee.id'))
)
jt_cohort_course = Table('jt_cohort_course', db.Model.metadata,
    db.Column('cohort_id', db.Integer, db.ForeignKey('cohort.id')),
    db.Column('course_id', db.Integer, db.ForeignKey('course.id'))
)
jt_component_roomtype = Table('jt_component_roomtype', db.Model.metadata,
    db.Column('component_id', db.Integer, db.ForeignKey('component.id')),
    db.Column('roomtype_id', db.Integer, db.ForeignKey('roomtype.id'))
)


###
### From here on follows a long list of entities (classes of database-backed objects), each with an admin interface
### and a user interface.
###

### USER

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    login = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120))
    password = db.Column(db.String(128), nullable=False)
    admin = db.Column(db.Boolean(), default=False, nullable=False)

    def __init__(self, login=None, password=None):
        self.login = login
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
    form_columns = ['id', 'login', 'admin', 'email', 'password']


### SEMESTER

class Semester(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    name = db.Column(db.String(10))
    #courses = db.relationship('Course', backref='semester')
    def __init__(self, name=None, id=None):
        self.id=id
        self.name=name
    def __str__(self):
        return self.name
    @property
    def shortname(self):
        return '{}{}'.format(self.name[0:2], self.name[5:])
    __mapper_args__ = {
        'order_by' : id.desc()
    }

class SemesterAdminView(AdminView):
    form_columns = ['id', 'name', 'courses']

class SemesterUserView(UserView):
    column_display_pk = True
    form_columns = ['id', 'name', 'courses']
    can_edit = True
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
    active = db.Column(db.Boolean(), default=True, nullable=False)
    employees = db.relationship('Employee', secondary=jt_chair_employee, backref='chairs')
    def __init__(self, id=None, name=None, active=True):
        self.id = id
        self.name = name
        self.active = active
    def __str__(self):
        return self.name
    __mapper_args__ = {
        'order_by' : (active.desc(), name)
    }

class ChairAdminView(AdminView):
    form_columns = ['id', 'name', 'active', 'employees']
    column_filters = ['active']

class ChairUserView(UserView):
    form_columns = ['name', 'active', 'employees']



### EMPLOYEE

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    lastname = db.Column(db.String(48))
    firstname = db.Column(db.String(32))
    salutation = db.Column(db.Enum('Frau', 'Herr'))
    degree = db.Column(db.Enum('', 'Dipl.-Inform.', 'Dipl.-Ing.', 'Dipl.-Ling.', 'Dipl.-Math.', 'Dipl.-Phys.',
                              'Dipl.-Sprachw.', 'Dr.', 'Dr.habil.', 'Mag.-Math.', 'Prof.Dr.', 'PD Dr.'))
    active = db.Column(db.Boolean(), default=True, nullable=False)
    aspcode = db.Column(db.String(20), nullable=False)
    #chairs = db.relationship('Chair', secondary=jt_chair_employee, backref='employees')
    #courses = db.relationship('Course', backref='employee')
    availability = db.Column(db.String(60), nullable=False, default='Mon:5++++5:Tue:5++++5:Wed:5++++5:Thu:5++++5:Fri:5++++5:')
    def __init__(self, id=None, lastname=None, firstname=None, salutation=None, degree=None, active=None, aspcode=None):
        self.id = id
        self.lastname = lastname
        self.firstname = firstname
        self.salutation = salutation
        self.degree = degree
        self.active = active
        self.aspcode = aspcode if aspcode else 'e{}'.format(id)
    __mapper_args__ = {
        'order_by' : (active.desc(), lastname, firstname)
    }
    def __str__(self):
        return '{} {}'.format(self.firstname, self.lastname)

class EmployeeAdminView(AdminView):
    form_columns = ['id', 'salutation', 'degree', 'lastname', 'firstname', 'active', 'chairs', 'courses', 'availability', 'aspcode']
    column_filters = ['active', 'degree']

class EmployeeUserView(UserView):
    form_columns = ['salutation', 'degree', 'lastname', 'firstname', 'active', 'chairs', 'courses', 'availability', 'aspcode']
    column_filters = ['active', 'degree']



### DELIVERY TYPE / LEHRFORM

class Deliverytype(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    name = db.Column(db.String(128))
    shortname = db.Column(db.String(64))
    code = db.Column(db.String(2))
    sortkey = db.Column(db.Integer())
    def __init__(self, id, name, shortname, code, sortkey):
        self.id = id
        self.name = name
        self.shortname = shortname
        self.code = code
        self.sortkey = sortkey
    def __str__(self):
        return self.name
    __mapper_args__ = {
        'order_by' : sortkey
    }

class DeliverytypeAdminView(AdminView):
    form_columns = ['id', 'name', 'shortname', 'sortkey']

class DeliverytypeUserView(UserView):
    form_columns = ['name', 'shortname', 'sortkey']



### COURSE / LEHRANGEBOT

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    name = db.Column(db.String(128))
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'))
    semester = db.relationship('Semester', backref='courses')
    chair_id = db.Column(db.Integer, db.ForeignKey('chair.id'))
    chair = db.relationship('Chair', backref='courses')
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    employee = db.relationship('Employee', backref='courses')
    deliverytype_id = db.Column(db.Integer, db.ForeignKey('deliverytype.id'))
    deliverytype = db.relationship('Deliverytype', backref='courses')
    prerequisites = db.Column(db.Text())
    remarks = db.Column(db.Text())
    shortdescription = db.Column(db.String(128))
    readinglist = db.Column(db.Text())
    url = db.Column(db.String(128))
    assessment = db.Column(db.Text())
    internalcomment = db.Column(db.Text())
    #cohorts = db.relationship('Cohort', secondary=jt_cohort_course, backref='courses')
    def __init__(self, id=None, semester_id=None, chair_id=None, deliverytype_id=None, name=None, url=None,
                 prerequisites=None, remarks=None, shortdescription=None, assessment=None, readinglist=None, internalcomment=None):
        self.id = id
        self.semester_id = semester_id
        self.chair_id = chair_id
        self.deliverytype_id = deliverytype_id
        self.name = name
        self.prerequisites = prerequisites
        self.remarks = remarks
        self.shortdescription = shortdescription
        self.assessment = assessment
        self.readinglist = readinglist
        self.internalcomment = internalcomment
    def __str__(self):
        return '{} ({} {})'.format(self.name, self.deliverytype.code, self.semester.shortname)
    __mapper_args__ = {
        'order_by' : (semester_id.desc(), name)
    }

class CourseAdminView(AdminView):
    form_columns = ['id', 'semester', 'chair', 'deliverytype', 'name', 'url', 'employee', 'cohorts',
                    'prerequisites', 'remarks', 'shortdescription', 'assessment', 'readinglist', 'internalcomment']

class CourseUserView(UserView):
    form_columns = ['semester', 'chair', 'deliverytype', 'name', 'url', 'employee', 'cohorts',
                    'prerequisites', 'remarks', 'shortdescription', 'assessment', 'readinglist', 'internalcomment']
    can_edit = True
    form_widget_args = {
        'semester': {
            'disabled': True
        }
    }



### CURRICULUM / STUDIENPLAN

class Curriculum(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    name = db.Column(db.String(200))
    shortname = db.Column(db.String(40))
    internalcomment = db.Column(db.Text())
    aspcode = db.Column(db.String(20), nullable=False)
    def __str__(self):
        return self.name
    __mapper_args__ = {
        'order_by' : shortname
    }

class CurriculumAdminView(AdminView):
    form_columns = ['id', 'shortname', 'name', 'aspcode']

class CurriculumUserView(UserView):
    form_columns = ['shortname', 'name', 'aspcode']



### COHORT / KOHORTE

class Cohort(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    curriculum_id = db.Column(db.Integer, db.ForeignKey('curriculum.id'))
    curriculum = db.relationship('Curriculum', backref='cohorts')
    studysemester = db.Column(db.Integer)
    courses = db.relationship('Course', secondary=jt_cohort_course, backref='cohorts')
    availability = db.Column(db.String(60), nullable=False, default='Mon:5++++5:Tue:5++++5:Wed:5++++5:Thu:5++++5:Fri:5++++5')
    internalcomment = db.Column(db.Text())
    def __str__(self):
        if self.studysemester == 1:
            th = 'st'
        elif self.studysemester == 2:
            th = 'nd'
        else:
            th = 'th'
        return '{} {}{} semester'.format(self.curriculum.shortname, self.studysemester, th)
    @property
    def aspcode(self):
        return '{}_{}'.format(self.curriculum.aspcode, self.studysemester)
    __mapper_args__ = {
        'order_by' : (curriculum_id, studysemester) # This won't do. Maybe add sortkey to this class?
    }

class CohortAdminView(AdminView):
    form_columns = ['id', 'curriculum', 'studysemester', 'courses', 'availability', 'internalcomment']

class CohortUserView(UserView):
    form_columns = ['curriculum', 'studysemester', 'courses', 'availability', 'internalcomment']



### ROOM TYPE / RAUMTYP

class Roomtype(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    name = db.Column(db.String(40), nullable=False)
    code = db.Column(db.String(17), nullable=False)
    aspcode = db.Column(db.String(20), nullable=False)
    def __str__(self):
        return self.name
    def __init__(self, id=None, name=None, code=None):
        self.id = id
        self.name = name
        self.code = code
        self.aspcode = 'rt_{}'.format(code)

class RoomtypeAdminView(AdminView):
    form_columns = ['id', 'name', 'code', 'components', 'aspcode']

class RoomtypeUserView(UserView):
    form_columns = ['name', 'code', 'components', 'aspcode']



### ROOM / RAUM

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    code = db.Column(db.String(17), nullable=False)
    roomtype_id = db.Column(db.Integer, db.ForeignKey('roomtype.id'), nullable=False)
    roomtype = db.relationship('Roomtype', backref='rooms')
    capacity = db.Column(db.Integer(), default=0, nullable=False)
    availability = db.Column(db.String(60), nullable=False, default='Mon:++++++:Tue:++++++:Wed:++++++:Thu:++++++:Fri:++++++:')
    internalcomment = db.Column(db.Text())
    aspcode = db.Column(db.String(20), nullable=False)
    def __str__(self):
        return '{} {}{}'.format(self.code, 'C' if self.computers else '', self.capacity)
    def __init__(self, id=None, code=None, roomtype=None):
        self.id = id
        self.code = code
        self.roomtype = roomtype
        self.aspcode = 'r' + code.replace('.', '_').replace('-', '_')

class RoomAdminView(AdminView):
    form_columns = ['id', 'code', 'roomtype', 'capacity', 'availability', 'aspcode', 'internalcomment']

class RoomUserView(UserView):
    form_columns = ['code', 'roomtype', 'capacity', 'availability', 'aspcode', 'internalcomment']



### RHYTHM / RHYTHMUS

class Rhythm(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    hours = db.Column(db.Integer, nullable=False) # for biweekly events the number of hours in an odd or even week
    oddweeks = db.Column(db.Boolean, nullable=False, default=True)   # takes place in odd calendar weeks
    evenweeks = db.Column(db.Boolean, nullable=False, default=True)  # takes place in even calendar weeks
    @property
    def name(self):
        if self.oddweeks and self.evenweeks:
            return '{} SWS'.format(self.hours)
        elif self.oddweeks:
            return '{}/2 SWS, in ungeraden Wochen'.format(self.hours)
        elif self.evenweeks:
            return '{}/2 SWS, in geraden Wochen'.format(self.hours)
        else:
            return '{} Std. Blockveranstaltung'
    @property
    def code(self):
        if self.oddweeks and self.evenweeks:
            return '{}W'.format(self.hours)
        elif self.oddweeks:
            return '{}U'.format(self.hours)
        elif self.evenweeks:
            return '{}G'.format(self.hours)
        else:
            return '{}B'
    def __str__(self):
        return self.name
    def __init_(self, id=None, hours=None, oddweeks=True, evenweeks=True):
        self.id = id
        self.hours = hours
        self.oddweeks = oddweeks
        self.evenweeks = evenweeks

class RhythmAdminView(AdminView):
    form_columns = ['id', 'hours', 'oddweeks', 'evenweeks', 'components']
    form_widget_args = {
        'name': {
            'disabled': True
        },
        'code': {
            'disabled': True
        }
    }

class RhythmUserView(UserView):
    form_columns = ['hours', 'oddweeks', 'evenweeks', 'components']



### COMPONENT / KOMPONENTE

class Component(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    course = db.relationship('Course', backref='components')
    deliverytype_id = db.Column(db.Integer, db.ForeignKey('deliverytype.id'))
    deliverytype = db.relationship('Deliverytype', backref='components')
    capacity = db.Column(db.Integer())
    roomtypes = db.relationship('Roomtype', secondary=jt_component_roomtype, backref='components')
    rhythm_id = db.Column(db.Integer, db.ForeignKey('rhythm.id'))
    rhythm = db.relationship('Rhythm', backref='components')
    internalcomment = db.Column(db.Text)
    groups = db.Column(db.Integer)
    minparallel = db.Column(db.Integer)
    maxparallel = db.Column(db.Integer)
    @property
    def aspcode(self):
        return 'c{}'.format(self.id)
    
    @property
    def aspcapacity(self):
        if self.capacity == None:
            return 0
        return self.capacity

    def __str__(self):
        return '{} ({} {})'.format(self.course.name, self.deliverytype.code, self.course.semester)
    def __init__(self, id=None, course_id=None, deliverytype_id=None, capacity=None, rhythm_id=None,
                 groups=1, minparallel=1, maxparallel=1):
        self.id = id
        self.course_id = course_id
        self.deliverytype_id = deliverytype_id
        self.capacity = capacity
        self.rhythm_id = rhythm_id

class ComponentAdminView(AdminView):
    form_columns = ['id', 'course', 'deliverytype', 'capacity', 'roomtypes', 'rhythm']

class ComponentUserView(UserView):
    form_columns = ['course', 'deliverytype', 'capacity', 'roomtypes', 'rhythm']


###
### With all entities defined, we now come to additional views. Most of them do not directly correspond to a particular
### entity.
###

timeslots = [
    'mon08', 'mon10', 'mon12', 'mon14', 'mon16', 'mon18',
    'tue08', 'tue10', 'tue12', 'tue14', 'tue16', 'tue18',
    'wed08', 'wed10', 'wed12', 'wed14', 'wed16', 'wed18',
    'thu08', 'thu10', 'thu12', 'thu14', 'thu16', 'thu18',
    'fri08', 'fri10', 'fri12', 'fri14', 'fri16', 'fri18'
]
def available(availability, timeslot):
    result = availability[3 + 4*(timeslot%6) + timeslot]
    return result != '0'

class OptimizeView(admin.BaseView):
    def is_accessible(self):
        return login.current_user.is_authenticated() and login.current_user.admin
    def __init__(self, name="Optimize", category=None, session=db.session):
        admin.BaseView.__init__(self, name, category)
        self.session = session
    @admin.expose('/')
    def index(self):
        inputArr = []
            
        inputArr.append('% Rooms\n')
        for room, capacity, availability in self.session.query(Room.aspcode, Room.capacity, Room.availability):
            if capacity == 0: continue
            inputArr.append('room("{0}",{1}).\n'.format(room, capacity))
            for t in range(len(timeslots)):
                if available(availability, t):
                    inputArr.append('room_availability("{}",{}). '.format(room, timeslots[t]))
            inputArr.append('\n\n')

        inputArr.append('\n% Employees\n')
        for employee, active, availability in self.session.query(Employee.aspcode, Employee.active, Employee.availability):
            if not active: continue
            inputArr.append('employee({}).\n'.format(employee))
            for t in range(len(timeslots)):
                if available(availability, t):
                    inputArr.append('employee_availability({},{}). '.format(employee, timeslots[t]))
            inputArr.append('\n\n')

        inputArr.append('\n% Course components\n')
        for component in self.session.query(Component):
            if component.id <= 4429: continue
            #print(dir(component.course.employee))
            print(component)
            inputArr.append('course({0},{1}).\n'.format(component.aspcode, component.aspcapacity))
            inputArr.append('groups({0},{1}). minparallel({0},{2}). maxparallel({0},{3}).\n'.format(component.aspcode, 0,0,0))

        inputStr = ''.join(inputArr)

        #with open('timetable.lp', 'w') as outfile:
        solution = AspSolution(input=inputStr)
        db.session.merge(solution)
        db.session.commit()
        
        return 'LP program is now in database queue'



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

class AspSolution(db.Model):
    __tablename__ = 'aspsolution'
    id = db.Column(db.Integer, primary_key=True, nullable=True)
    loaddate = db.Column(db.DateTime)
    status = db.Column(db.Enum('New','In process','Completed','Error'))
    input = db.Column(LONGTEXT())
    output = db.Column(LONGTEXT())
    comment = db.Column(LONGTEXT())
    #cohorts = db.relationship('Cohort', secondary=jt_cohort_course, backref='courses')
    def __init__(self, id=None, loaddate=datetime.datetime.utcnow(), status='New', input=None, 
                 output=None, comment=None):
        self.id = id
        self.loaddate = loaddate
        self.status = status
        self.input = input
        self.output = output
        self.comment = comment
    __mapper_args__ = {
        'order_by' : (id.desc())
    }

class AspSolutionView(AdminView):
    form_columns = ['id', 'loaddate', 'status', 'comment']

# for AspSolution
db.create_all()

# Initialize flask-login
init_login()

# Create admin interface
adminInterface = admin.Admin(app, 'Abrakadabra', index_view=MyAdminIndexView(), base_template='my_master.html')

# Views for all users
adminInterface.add_view(CourseUserView(Course))
adminInterface.add_view(EmployeeUserView(Employee, category='Resources'))
adminInterface.add_view(RoomUserView(Room, category='Resources'))
adminInterface.add_view(ChairUserView(Chair, category='Types'))
adminInterface.add_view(CohortUserView(Cohort, category='Types'))
adminInterface.add_view(CurriculumUserView(Curriculum, category='Types'))
adminInterface.add_view(DeliverytypeUserView(Deliverytype, category='Types'))
adminInterface.add_view(RhythmUserView(Rhythm, category='Types'))
adminInterface.add_view(RoomtypeUserView(Roomtype, category='Types'))
adminInterface.add_view(SemesterUserView(Semester, category='Types'))
adminInterface.add_view(OptimizeView())
adminInterface.add_view(AspSolutionView(AspSolution))

# Additional views for admins
adminInterface.add_view(ChairAdminView(Chair))
adminInterface.add_view(CohortAdminView(Cohort))
adminInterface.add_view(ComponentAdminView(Component))
adminInterface.add_view(CourseAdminView(Course))
adminInterface.add_view(CurriculumAdminView(Curriculum))
adminInterface.add_view(DeliverytypeAdminView(Deliverytype))
adminInterface.add_view(EmployeeAdminView(Employee))
adminInterface.add_view(RhythmAdminView(Rhythm))
adminInterface.add_view(RoomAdminView(Room))
adminInterface.add_view(RoomtypeAdminView(Roomtype))
adminInterface.add_view(SemesterAdminView(Semester))
adminInterface.add_view(UserAdminView(User))

relevant_semester = 23 # TODO: compute from current date, and make sure this semester and all previous ones exist!

######################################################################################################################
######################################################################################################################
######################################################################################################################

# Building/importing the initial database
def build_db():
    db.create_all()

    # USERS (complete)
    # Just create an admin and a normal user for testing.
    print('Creating users')

    user = User(login='admin', password='admin')
    user.id=1
    user.admin = True
    db.session.merge(user)
    user = User(login='user', password='user')
    user.id=2
    db.session.merge(user)

    # SEMESTERS (complete for optimization)
    # Instead of importing this information, we make it up in such a way that it is compatible to the old
    # database (same id for same semester).
    # Original database has a lot more information of unclear relevance for anything.

    for id in range(1, relevant_semester+3):
        semesterType = 'SS' if id%2==1 else 'WS'
        year = 2004 + int((id-1)/2)
        if id%2 == 1:
            year = str(year)
        else:
            year = '{}/{}'.format(year, str(year+1)[2:])
        semester = Semester(id=id, name='{} {}'.format(semesterType, year))
        db.session.merge(semester)

    # CHAIRS (complete)
    print('Importing chairs')

    class Professur(db.Model):
        __tablename__ = 'professuren'
        id = db.Column(db.Integer, primary_key=True, nullable=True)
        bezeichnung = db.Column(db.String())
        aktiv = db.Column(db.Enum('Y', 'N'))

    for professur in db.session.query(Professur):
        chair = Chair(id=professur.id, name=professur.bezeichnung, active=(professur.aktiv=='Y'))
        db.session.merge(chair)

    # EMPLOYEES (complete for optimization)
    # Original database has a lot more information of unclear relevance for the course catalog.
    print('Importing employees')

    class Mitarbeiter(db.Model):
        id = db.Column(db.Integer, primary_key=True, nullable=True)
        nachname = db.Column(db.String())
        vorname = db.Column(db.String())
        anrede = db.Column(db.String())
        titel = db.Column(db.String())
        aktiv = db.Column(db.String())

    for mitarbeiter in db.session.query(Mitarbeiter):
        employee = Employee(id=mitarbeiter.id, lastname=mitarbeiter.nachname, firstname=mitarbeiter.vorname,
                            salutation=mitarbeiter.anrede, degree=mitarbeiter.titel,
                            active=(mitarbeiter.aktiv=='Y'))
        db.session.merge(employee)

    # EMPLOYEE-CHAIR RELATIONS (without employment types)
    print('NOT importing employee-chair relations')

    # TODO: Do this manually with SQL!

    # DELIVERY TYPES (complete)
    print('Importing delivery types')

    class Lehrform(db.Model):
        __tablename__ = 'lehrformen'
        id = db.Column(db.Integer, primary_key=True, nullable=True)
        bezeichnung = db.Column(db.String())
        kurzbezeichnung = db.Column(db.String())
        codename = db.Column(db.String())
        order = db.Column(db.Integer())

    for lehrform in db.session.query(Lehrform):
        deliverytype = Deliverytype(id=lehrform.id, name=lehrform.bezeichnung, shortname=lehrform.kurzbezeichnung,
                        code=lehrform.codename, sortkey=lehrform.order)
        db.session.merge(deliverytype)

    # COURSES (essentially complete for optimization?)
    print('Importing courses')

    class Lehrveranstaltung(db.Model):
        __tablename__ = 'lehrveranstaltungen'
        id = db.Column(db.Integer, primary_key=True, nullable=True)
        bezeichnung = db.Column(db.String())
        lehrform_id = db.Column(db.Integer, name='lehrform')
    class GeplanteLehrveranstaltung(db.Model):
        __tablename__ = 'geplante_lehrveranstaltungen'
        id = db.Column(db.Integer, primary_key=True, nullable=True)
        lehrveranstaltung_id = db.Column(db.Integer, db.ForeignKey('lehrveranstaltungen.id'), name='lehrveranstaltung')
        lehrveranstaltung = db.relationship('Lehrveranstaltung', backref='geplante_lehrveranstaltungen')
        semester_id = db.Column(db.Integer, name='semester')
        professur_id = db.Column(db.Integer, name='professur')
        website = db.Column(db.String())
        voraussetzungen = db.Column(db.Text())
        bemerkungen = db.Column(db.Text())
        kurzbeschreibung = db.Column(db.String())
        leistungserfassung = db.Column(db.Text())
        literatur = db.Column(db.Text())
        planungshinweis = db.Column(db.Text())

    for glv in db.session.query(GeplanteLehrveranstaltung):
        course = Course(id=glv.id, semester_id=glv.semester_id, chair_id=glv.professur_id,
                        deliverytype_id=glv.lehrveranstaltung.lehrform_id, name=glv.lehrveranstaltung.bezeichnung,
                        url=glv.website, prerequisites=glv.voraussetzungen, remarks=glv.bemerkungen,
                        shortdescription=glv.kurzbeschreibung, assessment=glv.leistungserfassung,
                        readinglist=glv.literatur, internalcomment = glv.planungshinweis)
        db.session.merge(course)

    # ROOM TYPES (new)
    print('Creating room types')

    roomtype_h = Roomtype(id=1, name='Hörsaal (keine Tische)', code='H')
    roomtype_s = Roomtype(id=2, name='Seminarraum (Tische)', code='S')
    roomtype_c = Roomtype(id=3, name='Computerraum (Tische)', code='C')
    roomtype_b = Roomtype(id=4, name='Büro', code='B')
    db.session.merge(roomtype_h)
    db.session.merge(roomtype_s)
    db.session.merge(roomtype_c)
    db.session.merge(roomtype_b)

    # ROOMS (complete)
    print('Importing rooms')

    class Raum(db.Model):
        __tablename__ = 'raeume'
        id = db.Column(db.Integer, primary_key=True, nullable=True)
        codename = db.Column(db.String(17))

    class Seminarraum(db.Model):
        __tablename__ = 'seminarraeume'
        id = db.Column(db.Integer, primary_key=True, nullable=True)
        computerpool = db.Column(db.String())
        kapazitaet = db.Column(db.Integer)

    store = {}
    for raum in db.session.query(Raum):
        room = Room(id=raum.id, code=raum.codename, roomtype=roomtype_b)
        store[room.id] = room
    for seminarraum in db.session.query(Seminarraum):
        room = store[seminarraum.id]
        if seminarraum.computerpool == 'Y':
            room.roomtype = roomtype_c
        elif seminarraum.computerpool == 'N': # XXX: Must check this manually for all rooms!
            if 'H' in room.code:
                room.roomtype = roomtype_h
            else:
                room.roomtype = roomtype_s
        room.capacity = seminarraum.kapazitaet
    for room in store.values():
        db.session.merge(room)

    ### RHYTHMS (new)
    print('Creating rhythms')

    for h in range(1,13):
        rhythm = Rhythm(id=h, hours=h)
        db.session.merge(rhythm)
    for h in range(1,13):
        rhythm = Rhythm(id=12+h, hours=h, oddweeks=True, evenweeks=False)
        db.session.merge(rhythm)
    for h in range(1,13):
        rhythm = Rhythm(id=24+h, hours=h, oddweeks=False, evenweeks=True)
        db.session.merge(rhythm)
    for h in range(1,13):
        rhythm = Rhythm(id=36+h, hours=h, oddweeks=False, evenweeks=False)
        db.session.merge(rhythm)

    ### COMPONENTS
    print('Importing course components')

    class GeplanteLehrveranstaltungenTermine(db.Model):
        __tablename__ = 'geplante_lehrveranstaltungen_termine'
        id = db.Column(db.Integer, primary_key=True, nullable=True)
        geplante_lehrveranstaltung = db.Column(db.Integer())
        bloecke = db.Column(db.Integer)
        typ = db.Column(db.String)
        lehrform = db.Column(db.Integer)
        kapazitaet = db.Column(db.Integer)
        computerpool = db.Column(db.String)
        raumkommentar = db.Column(db.Text)
        zeitkommentar = db.Column(db.Text)
        alternativetermine = db.Column(db.Integer)
        paralleltermine = db.Column(db.Integer)

    for glvt in db.session.query(GeplanteLehrveranstaltungenTermine):
        print(glvt.id)
        component = Component(id=glvt.id, course_id=glvt.geplante_lehrveranstaltung, deliverytype_id=glvt.lehrform,
                              capacity=glvt.kapazitaet, groups=glvt.alternativetermine,
                              minparallel=glvt.paralleltermine, maxparallel=glvt.paralleltermine)
        if glvt.typ == 'woechentlich':
            component.rhythm_id = glvt.bloecke
        elif glvt.typ == 'zweiwoechentlich':
            component.rhythm_id = glvt.bloecke+12
        elif glvt.typ == 'blockveranstaltung':
            component.rhythm_id = glvt.bloecke+36
        if glvt.computerpool in 'YE':
            component.roomtypes.append(roomtype_c)
        if glvt.computerpool in 'NE':
            component.roomtypes.append(roomtype_h)
            component.roomtypes.append(roomtype_s)
        if not glvt.raumkommentar:
            component.internalcomment = glvt.zeitkommentar
        elif not glvt.zeitkommentar:
            component.internalcomment = glvt.raumkommentar
        elif glvt.raumkommentar == glvt.zeitkommentar:
            component.internalcomment = glvt.raumkommentar
        else:
            component.internalcomment = glvt.raumkommentar + '\n\n' + glvt.zeitkommentar
        db.session.merge(component)

    db.session.commit()

from subprocess import call, Popen, PIPE

def aspsolver_thread(arg):
    while True:
        
        tmpfilepath = "/tmp/cs_timetable.lp"
        #read db
        sql = 'select id, loaddate, status, input, comment from '+AspSolution.__tablename__+' where status=\'New\' or status=\'In process\' order by loaddate limit 1'
        result = db.engine.execute(sql)
        
        any_record = False
        for row in result:
            print("start asp solving")
            solution = AspSolution(id = row[0], loaddate = row[1], status = row[2], 
                                   input=row[3], comment = row[4])
            solution.status = 'In process'
            db.session.merge(solution)
            db.session.commit()
            
            with open(tmpfilepath, "w") as inputfile:
                inputfile.write(solution.input)
            p1 = Popen(["./gringo",tmpfilepath,"solver.lp"], stdout=PIPE)
            p2 = Popen(["./clasp","1"], stdin=p1.stdout, stdout=PIPE)
            solution.output = p2.communicate()[0]
            
            solution.status = 'Completed'
            db.session.merge(solution)
            db.session.commit()
            
            any_record = True
            print("end solving")
        if not any_record:
            sleep(10)

if __name__ == '__main__':
#    build_db()
    thread = Thread(target = aspsolver_thread, args = (10,), name="aspsolver_thread")
    thread.start()

######################################################################################################################
######################################################################################################################
######################################################################################################################

# Start app
#     app.jinja_env.add_extension('jinja2.ext.do')
app.run(debug=True, use_reloader=False)#no reloader, because there is thread which should be started once


from flask_admin.model import BaseModelView
