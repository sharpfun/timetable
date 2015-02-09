package com.github.hans_adler.timetable;

import org.javalite.activejdbc.Model;
import org.javalite.activejdbc.annotations.Table;
import com.github.hans_adler.timetable.mixin.MitBeschreibung;

@Table(value="geplante_lehrveranstaltungen")
public class GeplanteLehrveranstaltung
extends Model
implements MitBeschreibung {
    public Semester getSemester() {
        return Semester.findById(get("semester"));
    }
    public Lehrveranstaltung getLehrveranstaltung() {
        return Lehrveranstaltung.findById(get("lehrveranstaltung"));
    }
}
