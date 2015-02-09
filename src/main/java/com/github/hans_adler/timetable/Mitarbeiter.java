package com.github.hans_adler.timetable;

import org.javalite.activejdbc.Model;
import org.javalite.activejdbc.annotations.Table;
import com.github.hans_adler.timetable.mixin.MitNamen;

@Table("mitarbeiter")
public class Mitarbeiter
extends Model
implements MitNamen {
    public Raum getRaum() {
        return Raum.findById(get("raum"));
    }
}
