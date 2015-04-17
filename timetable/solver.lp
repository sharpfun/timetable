% room has some capacity, is available at some period, and it belongs to a category from 1 to 4, where 1 is Hörsaal (keine Tische), 2 is Seminarraum (Tische), 3 is Computerraum (Tische), 4 is Büro, 4 is not presented here
room_cap_av_type(ROOM, CAP, PERIOD, TYPE) :- room_capacity(ROOM, CAP), room_availability(ROOM, PERIOD), room_type(ROOM, TYPE).

% course is available when any of teachers of this course is available
course_av(COURSE, PERIOD) :- course_employee(COURSE, EMPL), employee_availability(EMPL, PERIOD).

% course has some capacity, is available at some period and can be hold at some type of room
course_cap_av_type(COURSE, CAPACITY, PERIOD, ROOMTYPE) :- course_av(COURSE, PERIOD), course_roomtype(COURSE, ROOMTYPE), course_capacity(COURSE, CAPACITY).

% this course can be presented in this room at some period
course_room_av(COURSE, ROOM, PERIOD) :- course_cap_av_type(COURSE, COURSECAPACITY, PERIOD, TYPE), room_cap_av_type(ROOM, ROOMCAPACITY, PERIOD, TYPE), COURSECAPACITY <= ROOMCAPACITY.

% this line makes schedule based on the AMOUNT of hours, using cardinality rule
((AMOUNT+1)/2) { assigned(COURSE, ROOM, PERIOD) : course_room_av(COURSE, ROOM, PERIOD) } ((AMOUNT+1)/2) :- course_rhythm(COURSE, AMOUNT, _, _).

% courses cannot take place at the same period in the same room
:- assigned(COURSE, ROOM, PERIOD), assigned(COURSE2, ROOM, PERIOD), COURSE != COURSE2.

% get real name of course and room
assigned_course(COURSE, COURSENAME, ROOMNAME, PERIOD) :- assigned(COURSE, ROOM, PERIOD), course(COURSE, COURSENAME), room(ROOM, ROOMNAME).

% get real name of employee
assigned_employee(COURSE, EMPLOYEENAME) :- course_employee(COURSE, EMPLOYEE), employee(EMPLOYEE, EMPLOYEENAME).

% output
#show assigned_course/4.
#show assigned_employee/2.
