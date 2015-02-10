package com.github.hans_adler.timetable;

import java.util.List;
import org.javalite.activejdbc.Model;
import org.javalite.activejdbc.annotations.BelongsTo;
import org.javalite.activejdbc.annotations.Many2Many;
import org.javalite.activejdbc.annotations.Table;
import com.github.hans_adler.timetable.mixin.MitKapazitaet;

@Table("geplante_lehrveranstaltungen_termine")
@BelongsTo(parent=GeplanteLehrveranstaltung.class, foreignKeyName="geplante_lehrveranstaltung")
@Many2Many(other = Mitarbeiter.class, join = "geplante_lehrveranstaltungen_mitarbeiter", sourceFKName = "termin", targetFKName = "mitarbeiter")
public class GeplanteLehrveranstaltungTermin
extends Model
implements MitKapazitaet {
    public GeplanteLehrveranstaltung getGeplanteLehrveranstaltung() {
        return GeplanteLehrveranstaltung.findById(get("geplante_lehrveranstaltung"));
    }
    public int getBloecke() {
        return getInteger("bloecke");
    }
    public Lehrform getLehrform() {
        return Lehrform.findById(get("lehrform"));
    }
    public List<Mitarbeiter> getAllMitarbeiter() {
        return getAll(Mitarbeiter.class);
    }
}
