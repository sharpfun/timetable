room_cap_av(ROOM, CAP, PERIOD) :- room(ROOM, CAP), room_availability(ROOM, PERIOD).

1 { assigned(COURSE, ROOM, PERIOD) : room_cap_av(ROOM, CAP, PERIOD), CAP >= AMOUNT } 1 :- course(COURSE, AMOUNT).

:- assigned(COURSE, ROOM, PERIOD), assigned(COURSE2, ROOM, PERIOD), COURSE != COURSE2.

#show assigned/3.
