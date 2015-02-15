from datetime import date
from pony.orm import *


class Pnr(db.Entity):
    _discriminator_ = "P"
    id = PrimaryKey(int, auto=True)
    code = Required(str, unique=True)
    institut = Required("Institut")
    name = Required(str)
    kohorten = Set("Kohorte", reverse="pnrn")
    pflichtkohorten = Set("Kohorte", reverse="pflichtpnrn")


class Institut(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True)
    code = Required(str, unique=True)
    pnrn = Set(Pnr)
    def __init__(self, name, code):
        self.name = name
        self.code = code
    def __str__(self):
        return 'Institut({}, {}, {})'.format(self.id, self.name, self.code)


class Modulpnr(db.Pnr):
    _discriminator_ = "M"
    lehrangebotspnrn = Set("Lehrangebotspnr")


class Lehrangebotspnr(db.Pnr):
    _discriminator_ = "L"
    modulpnrn = Set(Modulpnr)
    komponentenpnrn = Set("Komponentenpnr")
    lehrangebote = Set("Lehrangebot")


class Komponentenpnr(db.Pnr):
    _discriminator_ = "K"
    lehrangebotspnrn = Set(Lehrangebotspnr)
    komponenten = Set("Komponente")


class Pruefungsordnung(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    kohorten = Set("Kohorte")


class Kohorte(db.Entity):
    id = PrimaryKey(int, auto=True)
    pruefungsordnung = Required(Pruefungsordnung)
    fachsemester = Required(int)
    studierende = Optional(int)
    zeitraster = Required(str)
    pnrn = Set(Pnr, reverse="kohorten")
    pflichtpnrn = Set(Pnr, reverse="pflichtkohorten")


class Lehrangebot(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    lehrangebotspnrn = Set(Lehrangebotspnr)
    professur = Required("Professur")
    komponenten = Set("Komponente")
    dozent = Required("Dozent")
    semester = Required("Semester")


class Komponente(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    komponentenpnrn = Set(Komponentenpnr)
    lehrangebot = Required(Lehrangebot)
    dozenten = Set("Dozent")
    zeitbloecke = Required(int)
    gruppen = Required(int)
    parallel = Optional(bool)
    computer = Optional(bool)
    blockveranstaltung = Required(bool)
    mikroturnus = Required("Mikroturnus")
    zeitraster = Required(str, 66)
    wunschraeume = Set("Raum")


class Raum(db.Entity):
    id = PrimaryKey(int, auto=True)
    code = Required(str)
    gebaeude = Required("Gebaeude")
    personen = Required(int)
    computer = Required(bool)
    zeitraster = Required(str)
    wunschkomponenten = Set(Komponente)


class Gebaeude(db.Entity):
    id = PrimaryKey(int, auto=True)
    raeume = Set(Raum)


class Professur(db.Entity):
    id = PrimaryKey(int, auto=True)
    lehrangebote = Set(Lehrangebot)


class Dozent(db.Entity):
    id = PrimaryKey(int, auto=True)
    nachname = Required(str)
    vorname = Required(str)
    komponenten = Set(Komponente)
    lehrangebote = Set(Lehrangebot)
    zeitraster = Required(str)


class Mikroturnus(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    code = Required(str)
    bitmaske = Required(int)
    komponenten = Set(Komponente)


class Semester(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str, unique=True)
    code = Required(str, unique=True)
    naechstes = Optional("Semester", reverse="voriges")
    voriges = Optional("Semester", reverse="naechstes")
    lehrangebote = Set(Lehrangebot)


sql_debug(True)
db.generate_mapping(create_tables=True)
