room_cap_av_type(ROOM, CAP, PERIOD, TYPE) :- room_capacity(ROOM, CAP), room_availability(ROOM, PERIOD), room_type(ROOM, TYPE).

course_av(COURSE, PERIOD) :- course_employee(COURSE, EMPL), employee_availability(EMPL, PERIOD).

course_room_av(COURSE, ROOM, PERIOD) :- course_av(COURSE, PERIOD), course_roomtype(COURSE, ROOMTYPE), room_type(ROOM, ROOMTYPE), room_availability(ROOM, PERIOD), room_capacity(ROOM, ROOMCAPACITY), course_capacity(COURSE, COURSECAPACITY), COURSECAPACITY <= ROOMCAPACITY.

((AMOUNT+1)/2) { assigned(COURSE, ROOM, PERIOD) : course_room_av(COURSE, ROOM, PERIOD) } ((AMOUNT+1)/2) :- course_rhythm(COURSE, AMOUNT, _, _).

:- assigned(COURSE, ROOM, PERIOD), assigned(COURSE2, ROOM, PERIOD), COURSE != COURSE2.

assigned_course(COURSE, COURSENAME, ROOMNAME, PERIOD) :- assigned(COURSE, ROOM, PERIOD), course(COURSE, COURSENAME), room(ROOM, ROOMNAME).
assigned_employee(COURSE, EMPLOYEENAME) :- course_employee(COURSE, EMPLOYEE), employee(EMPLOYEE, EMPLOYEENAME).

#show assigned_course/4.
#show assigned_employee/2.
