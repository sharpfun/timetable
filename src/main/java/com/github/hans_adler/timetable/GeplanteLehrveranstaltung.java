package com.github.hans_adler.timetable;

import java.util.List;
import org.javalite.activejdbc.Model;
import org.javalite.activejdbc.annotations.BelongsTo;
import org.javalite.activejdbc.annotations.Table;
import com.github.hans_adler.timetable.mixin.MitBeschreibung;

@Table(value="geplante_lehrveranstaltungen")
@BelongsTo(parent=Semester.class, foreignKeyName="semester")
public class GeplanteLehrveranstaltung
extends Model
implements MitBeschreibung {
    public Semester getSemester() {
        return Semester.findById(get("semester"));
    }
    public Lehrveranstaltung getLehrveranstaltung() {
        return Lehrveranstaltung.findById(get("lehrveranstaltung"));
    }
    public List<GeplanteLehrveranstaltungTermin> getAllGeplanteLehrveranstaltungTermine() {
        return getAll(GeplanteLehrveranstaltungTermin.class);
    }
    public int countAllGeplanteLehrveranstaltungTermine() {
        return getAllGeplanteLehrveranstaltungTermine().size();
    }
}
