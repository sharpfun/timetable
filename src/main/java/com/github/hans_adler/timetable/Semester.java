package com.github.hans_adler.timetable;

import java.util.List;
import org.javalite.activejdbc.Model;
import org.javalite.activejdbc.annotations.Table;
import com.github.hans_adler.timetable.mixin.MitCodename;
import com.github.hans_adler.timetable.mixin.MitKurzbezeichnung;

@Table(value="semester")
public class Semester
extends Model
implements MitKurzbezeichnung, MitCodename {
    public int getJahr() {
        return getInteger("jahr");
    }
    public Semester getVorgaenger() {
        return Semester.findById(get("vorgaenger"));
    }
    public List<GeplanteLehrveranstaltung> getAllGeplanteLehrveranstaltungen() {
        //return getAll(GeplanteLehrveranstaltung.class);
        return GeplanteLehrveranstaltung.findBySQL(
               "SELECT geplante_lehrveranstaltungen.* "
               + "FROM geplante_lehrveranstaltungen JOIN lehrveranstaltungen "
               + "ON geplante_lehrveranstaltungen.lehrveranstaltung = lehrveranstaltungen.id "
               + "WHERE geplante_lehrveranstaltungen.semester = ? ORDER BY lehrveranstaltungen.bezeichnung", this.getId());
    }
    public int countAllGeplanteLehrveranstaltungen() {
        return getAllGeplanteLehrveranstaltungen().size();
    }
    public String getName() {
        return getBezeichnung() + " " + getJahr();
    }
    public String getKurzname() {
        return getKurzbezeichnung() + getJahr();
    }
    @Override
    public String toString() {
        return getName();
    }
}
