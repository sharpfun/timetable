from datetime import date
from pony.orm import *;

db = Database()
db.bind('mysql', host='localhost', user='root', passwd='cognitivesystems', db='pokus')

class Semester(db.Entity):
    bezeichnung = Required(str)
    kurzbezeichnung = Required(str)
    jahr = Required(int)
    codename = Required(str)
    von = Required(date)
    bis = Required(date)
    vorgaenger = Optional('Semester', reverse = 'nachfolger')
    nachfolger = Optional('Semester', reverse = 'vorgaenger')
    glvs = Set('GLV')
    def __str__(self):
        return self.codename

class Lehrform(db.Entity):
    _table_ = 'lehrformen'
    bezeichnung = Required(str)
    kurzbezeichnung = Required(str)
    codename = Required(str)
    order = Required(int)
    lvs = Set('LV')
    glvts = Set('GLVT')

class Stg(db.Entity):
    _table_ = 'stg'
    name = Required(str)
    kuerzel = Required(str)
    stgmodule = Set('Stgmodul')

class Stgmodul(db.Entity):
    _table_ = 'stgmodule'
    stg = Required('Stg')
    pnr = Required(int)
    name = Required(str)
    lp = Required(int)
    lvs = Set('LV', table='lv_stgmodul', column='lv')

class LV(db.Entity):
    _table_ = 'lehrveranstaltungen'
    pnr = Optional(int)
    pnrma = Optional(int)
    bezeichnung = Required(str)
    leistungspunkte = Required(float)
    lehrform = Required('Lehrform')
    glvs = Set('GLV')
    stgmodule = Set('Stgmodul')
    def __str__(self):
        return 'LV({}, {})'.format(self.id, self.bezeichnung)

class Professur(db.Entity):
    _table_ = 'professuren'
    bezeichnung = Required(str)
    glvs = Set('GLV')

class Modul(db.Entity):
    _table_ = 'module'
    pnr = PrimaryKey(int, auto=False)
    name = Required(str)
    lp = Required(int)
    glvs = Set('GLV', table='modulzuordnungen', column='modul')

class GLV(db.Entity):
    _table_ = 'geplante_lehrveranstaltungen'
    lv = Required('LV', column='lehrveranstaltung')
    semester = Required('Semester')
    professur = Required('Professur')
    empfohlen = Required(int)
    praktischeleistungspunkte = Required(float)
    prioritaet = Required(int)
    kurzbeschreibung = Required(str)
    website = Optional(str)
    pruefungsnr_intern = Optional(int)
    module = Set('Modul', table='modulzuordnungen', column='geplante_lehrveranstaltung')
    glvts = Set('GLVT')
    def __str__(self):
        return 'GLV({}, {}, {})'.format(self.id, self.lv.bezeichnung, self.semester)

class Raum(db.Entity):
    _table_ = 'raeume'
    haus = Required(str)
    etage = Required(int)
    zimmer = Required(str)
    codename = Required(str)
    mitarbeiter = Set('Mitarbeiter')

class Mitarbeiter(db.Entity):
    _table_ = 'mitarbeiter'
    vorname = Required(str)
    nachname = Required(str)
    raum = Optional('Raum')
    telefon = Optional(str)
    email = Optional(str)

class GLVT(db.Entity):
    _table_ = 'geplante_lehrveranstaltungen_termine'
    glv = Required('GLV', column='geplante_lehrveranstaltung')
    bloecke = Required(int)
    lehrform = Required('Lehrform')
    alternativetermine = Required(int)
    paralleltermine = Required(int)
    gruppe = Optional(int)
    def __str__(self):
        return 'GLVT({}, {})'.format(self.id, self.glv.lv.bezeichnung)

db.generate_mapping(check_tables=True, create_tables=False)

@db_session
def test():
    aktuelles_semester = get(s for s in Semester if s.id == 23)
    print(aktuelles_semester.bezeichnung, aktuelles_semester.jahr)

    aktuelle_glvs = select(glv for glv in GLV if glv.semester == aktuelles_semester)
    for glv in aktuelle_glvs:
        print(glv)

    aktuelle_lvs = select(glv.lv for glv in GLV if glv.semester == aktuelles_semester)
    for lv in aktuelle_lvs:
        print(lv)
test()
